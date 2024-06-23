import asyncio
import google.generativeai as genai
from google.generativeai import protos
from pydantic import BaseModel, Field, field_validator
import logging
from typing import Any, AsyncIterator, Awaitable, Callable, Iterable


class FunctionCalling(BaseModel, frozen=True):
    functions: (
        list[Callable[..., Awaitable[Any]]]
        | dict[str, Callable[..., Awaitable[Any]]]
        | None
    )
    func: dict[str, Callable[..., Awaitable[Any]]] = Field(
        default_factory=dict,
        repr=False,
        exclude=True,
    )

    @field_validator("functions")
    @classmethod
    def function_names_must_be_unique(cls, functions):
        if isinstance(functions, list):
            names = [function.__name__ for function in functions]
            if len(names) != len(set(names)):
                raise ValueError("Function names must be unique.")
        return functions

    @property
    def has_functions(self) -> bool:
        return self.functions is not None and len(self.functions) > 0

    def model_post_init(self, _):
        if self.functions:
            if isinstance(self.functions, list):
                for function in self.functions:
                    self.func[function.__name__] = function
            elif isinstance(self.functions, dict):
                self.func = self.functions

    async def call_once(
        self, function_call: protos.FunctionCall
    ) -> protos.FunctionResponse:
        try:
            function_name = function_call.name
            if function_name not in self.func:
                raise ValueError(f"Function {function_name} not found.")

            function = self.func[function_name]
            result = await function(**function_call.args)
            if not isinstance(result, dict):
                result = {"success": result}

            return protos.FunctionResponse(name=function_name, response=result)
        except Exception as e:
            logging.exception(e)
            return protos.FunctionResponse(
                name=function_name, response={"error": str(e)}
            )

    async def call_sequentially(
        self,
        model_responses: Iterable[protos.Part],
    ) -> AsyncIterator[protos.Part]:
        failed = False
        for part in model_responses:
            if function_call := part.function_call:
                if failed:
                    yield protos.Part(
                        function_response=protos.FunctionResponse(
                            name=function_call.name,
                            response={"skipped": "Previous function call failed."},
                        )
                    )
                    continue

                response = await self.call_once(function_call)
                if "error" in response.response:
                    failed = True
                yield protos.Part(function_response=response)

    async def call_parallelly(
        self, model_responses: Iterable[protos.Part]
    ) -> Iterable[protos.Part]:
        results = await asyncio.gather(
            *[
                self.call_once(part.function_call)
                for part in model_responses
                if part.function_call
            ],
        )
        return [
            protos.Part(function_response=response)
            for response in results
            if not isinstance(response, Exception)
        ]


class ChatSession(BaseModel, frozen=True, arbitrary_types_allowed=True):
    model: genai.GenerativeModel
    tools: FunctionCalling | None = Field(default=None)
    conversation: list[genai.protos.Content] = Field(default_factory=list)

    @property
    def history(self) -> Iterable[genai.protos.Content]:
        return self.conversation

    async def send_message(
        self,
        message: genai.types.ContentType,
    ) -> genai.types.GenerateContentResponse:
        self.conversation.append(
            genai.protos.Content(parts=[genai.protos.Part(text=message)], role="user")
        )

        while True:
            response = await self.model.generate_content_async(self.conversation)
            _check_response(response)

            response_content = response.candidates[0].content
            self.conversation.append(response_content)

            if (
                (not self.tools)
                or (not self.tools.has_functions)
                or (
                    len([part for part in response_content.parts if part.function_call])
                    == 0
                )
            ):
                break

            function_calling_response_parts = await self.tools.call_parallelly(
                response_content.parts
            )
            self.conversation.append(
                genai.protos.Content(parts=function_calling_response_parts, role="user")
            )

        return response


def _check_response(response: genai.types.AsyncGenerateContentResponse) -> None:
    if response.prompt_feedback.block_reason:
        raise genai.types.BlockedPromptException(response.prompt_feedback)
    if response.candidates[0].finish_reason not in (
        genai.protos.Candidate.FinishReason.FINISH_REASON_UNSPECIFIED,
        genai.protos.Candidate.FinishReason.STOP,
        genai.protos.Candidate.FinishReason.MAX_TOKENS,
    ):
        raise genai.types.StopCandidateException(response.candidates[0])

import asyncio
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

from goog.decorators import retry_on_server_error
from goog.function_calling import ChatSession, FunctionCalling
import google.generativeai as genai
import logging
from pydantic import BaseModel, ValidationError
from typing import Any, Awaitable, Callable, Iterable, Type, TypeVar

T = TypeVar("T")


_DEBUG = False


def configure(*, debug: bool = False) -> None:
    """Configures the agent module.

    Args:
        debug: Whether to enable debug mode.
    """
    global _DEBUG
    _DEBUG = debug


async def agent(
    output_type: Type[T],
    *,
    instruction: str,
    data: genai.types.ContentType | None = None,
    tools: Iterable[Callable[..., Awaitable[Any]]] | None = None,
    generation_config: genai.GenerationConfig | None = None,
    model_name: str = "gemini-1.5-pro-latest",
) -> T:
    """Generates an output using a generative model.

    Args:
        output_type: The type of output to generate. It must be either a Pydantic model or `str`.
        instruction: The instruction to use for generating the output.
        data: The data to use for generating the output.
        tools: The tools to use for generating the output.
        generation_config: The generation configuration to use for generating the output.
        model_name: The name of the model to use for generating the output.

    Returns:
        The generated output.
    """
    system_instruction = instruction + (
        "\n\nExplain your thoughts step by step. "
        "If you made an error, go right ahead to fix the problem and try again. "
        "When you have figured out the answer, restate clearly what the final response is with the full details but without the intermediate steps.\n"
    )
    if issubclass(output_type, BaseModel):
        system_instruction += (
            "Your final response should include the following information:\n"
            + _format_model_description(output_type)
        )
    if tools:
        system_instruction += (
            "\n\nIf you are calling functions, be careful to escape the quotes"
            " inside strings properly."
        )

    function_calling = FunctionCalling(functions=list(tools) if tools else None)
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_instruction,
        tools=function_calling.functions,
    )
    chat = ChatSession(model=model, tools=function_calling)

    message = data or "Begin."
    i = 0
    while True:
        response = await _send_message(chat, message)
        if _DEBUG:
            logging.info(
                "#### Chat starts ##############################################################"
            )
            logging.info(f"Instruction: {system_instruction}")
            for history_message in chat.history:
                logging.info(f"Message: {history_message}")
            logging.info(
                "#### Chat ends ##############################################################"
            )

        if output_type is str:
            return response.text
        assert issubclass(output_type, BaseModel)

        try:
            return await _parse(response.text, model_name=model_name, output_type=output_type)  # type: ignore
        except ValidationError as ex:
            logging.exception(f"Attempt #{i}. Failed to parse: {response.text}")
            if i > 3:
                raise RuntimeError(response.text) from ex
            message = _format_feedback(ex, output_type)
            i += 1


async def _parse(answer: str, *, model_name: str, output_type: Type[T]) -> T:
    assert issubclass(output_type, BaseModel)

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
        system_instruction=(
            "I will give you a passage that may have both the intermediate step-by-step thoughts and the final conclusion. "
            "Ignore the intermediate steps but extract the conclusion of the passage into a JSON object. "
            f"Use this JSON schema: {output_type.model_json_schema()}.\n\n"
        ),
    )
    response = await model.generate_content_async(answer)
    if _DEBUG:
        logging.info(f"Parsing: {response.text}")

    return output_type.model_validate_json(response.text)  # type: ignore


def _format_model_description(cls: Type[BaseModel]) -> str:
    """Formats the description of the model for self-correction."""
    return "\n".join(
        [
            f"""
Final response:
```
{cls.__doc__}
```
""",
            "Details to include in the final response.",
        ]
        + [
            f"""
{field_name}:
```
{field.description}
```
"""
            for field_name, field in cls.model_fields.items()
        ]
    )


def _format_feedback(e: ValidationError, cls: Type[BaseModel]) -> str:
    """Formats a descriptive feedback to the model for self-correction."""
    error_details: list[str] = []
    for i, error in enumerate(e.errors()):
        error_detail = f"Error #{i + 1}:\n"
        if error["loc"]:
            field_name = str(error["loc"][0])
            error_detail += (
                f"Field: {error['loc']}\n"
                f"Field description: {cls.model_fields[field_name].description}\n"
                f"Invalid value: {error['input']}\n"
            )
        error_detail += f"Error message: {error['msg']}\n"

        error_details.append(error_detail)

    return "\n\n".join(
        [f"Failed to parse the final response."]
        + error_details
        + ["Please resolve the error and restate the final response."]
    )


@retry_on_server_error
async def _send_message(
    chat: ChatSession, message: genai.types.ContentType
) -> genai.types.GenerateContentResponse:
    return await chat.send_message(message)

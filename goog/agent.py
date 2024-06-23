from goog.decorators import retry_on_server_error
import google.generativeai as genai
import logging
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar

T = TypeVar("T")


_DEBUG = True


def agent(
    output_type: Type[T],
    *,
    instruction: str,
    data: genai.types.ContentType | None = None,
    tools: genai.types.FunctionLibraryType | None = None,
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
        "When you have figured out the answer, restate clearly what the final response is with full details but without the intermediate steps."
    )
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_instruction,
        tools=tools,
    )
    chat = model.start_chat(enable_automatic_function_calling=True)

    message = data or "Begin."
    i = 0
    while True:
        response = _send_message(chat, message)
        if _DEBUG:
            print(
                "#### Chat starts ##############################################################"
            )
            for message in chat.history:
                print(f"Message: {message}")
            print(
                "#### Chat ends ##############################################################"
            )

        if output_type is str:
            return response.text
        assert issubclass(output_type, BaseModel)

        try:
            return _parse(response.text, model_name=model_name, output_type=output_type)  # type: ignore
        except ValidationError as ex:
            logging.error(f"Attempt #{i}. Failed to parse `{response.text}`: {ex}")
            if i > 3:
                raise RuntimeError(response.text) from ex
            message = _format_feedback(ex, output_type)
            i += 1


def _parse(answer: str, *, model_name: str, output_type: Type[T]) -> T:
    assert issubclass(output_type, BaseModel)

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
        system_instruction=(
            f"Given a passage that has both the intermediate step-by-step thoughts and the final conclusion, "
            f"extract the conclusion of a passage into a JSON object by following this JSON schema: {output_type.model_json_schema()}."
        ),
    )
    response = model.generate_content(answer)
    if _DEBUG:
        print(f"Parsed: {response.text}")

    return output_type.model_validate_json(response.text)  # type: ignore


def _format_feedback(e: ValidationError, cls: Type[BaseModel]) -> str:
    error_details = [
        f"Error #{i + 1}:\n"
        f"Field: {error['loc']}\n"
        f"Field description: {cls.model_fields[str(error['loc'][0])].description}\n"
        f"Invalid value: {error['input']}\n"
        f"Error message: {error['msg']}\n"
        for i, error in enumerate(e.errors())
    ]
    return "\n\n".join(
        [f"Failed to parse the final response."]
        + error_details
        + ["Please resolve the error and restate the final response."]
    )


@retry_on_server_error
def _send_message(
    chat: genai.ChatSession, message: genai.types.ContentType
) -> genai.types.GenerateContentResponse:
    return chat.send_message(message)

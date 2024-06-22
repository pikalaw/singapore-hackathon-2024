from typing import Type, TypeVar
import google.generativeai as genai
import logging
from pydantic import BaseModel

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
        output_type: The type of output to generate.
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
        "If you made an error, go right ahead to fix the problem and try again."
    )
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_instruction,
        tools=tools,
    )
    chat = model.start_chat(enable_automatic_function_calling=True)

    message = data
    i = 0
    while True:
        chat.send_message(message)
        response = chat.send_message(
            "Give the final response with details but without the intermediate reasoning. "
            "Don't add anything else. "
            "Just a succinct response."
        )
        if _DEBUG:
            print("#### Chat starts")
            for message in chat.history:
                print(f"Message: {message}")
            print("#### Chat ends")

        if output_type is str:
            return response.text
        assert issubclass(output_type, BaseModel)

        try:
            return _parse(response.text, model_name=model_name, output_type=output_type)  # type: ignore
        except Exception as ex:
            logging.error(f"Attempt #{i}. Failed to parse `{response.text}`: {ex}")
            if i > 3:
                raise
            message = (
                f"There's a problem with the final response. {ex}\n\n"
                "Please resolve the error and restate the final response."
            )
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
            f"Extract the information into a JSON object by following this JSON schema: {output_type.model_json_schema()}."
        ),
    )
    chat = model.start_chat()

    response = chat.send_message(answer)
    if _DEBUG:
        print(f"Parsed: {response.text}")

    try:
        return output_type.model_validate_json(response.text)  # type: ignore
    except Exception as ex:
        feedback = chat.send_message(
            f"Failed to parse the response. Reason: {ex}.\n\n"
            "Please interpret the error message and provide a feedback on how to fix it."
        )
        raise ValueError(feedback) from ex

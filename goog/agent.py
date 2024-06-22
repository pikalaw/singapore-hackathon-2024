from typing import Type, TypeVar
import google.generativeai as genai
import logging
from pydantic import BaseModel

T = TypeVar("T")


DEBUG = False


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
    chat.send_message(data)
    model_response = chat.send_message(
        "Give the final response with details but without the intermediate reasoning. "
        "Don't add anything else. "
        "Just a succinct response."
    )

    if DEBUG:
        for message in chat.history:
            print(message)

    if output_type is str:
        return model_response.text

    assert issubclass(output_type, BaseModel)

    parser = genai.GenerativeModel(
        model_name=model_name,
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
        system_instruction=(
            f"Extract the information into a JSON object of the following JSON schema: {output_type.model_json_schema()}."
        ),
    )
    parser_response = parser.generate_content(model_response.text)

    if DEBUG:
        print(f"Parsing {parser_response}")

    try:
        return output_type.model_validate_json(parser_response.text)  # type: ignore
    except Exception as ex:
        logging.error(f"Failed to parse the response: {parser_response.text}")
        raise

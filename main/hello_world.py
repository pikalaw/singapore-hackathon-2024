import asyncio
import google.generativeai as genai
import json
from pydantic import BaseModel, Field
from typing import Any


def send_message(recipient: str, text: str) -> Any:
    """Sends a message to the recipient.

    Args:
        recipient: The recipient of the message.
        text: The text of the message.

    Returns:
        True if the message was sent successfully.
    """
    print(f"Attempting to send a message to {recipient} saying {text}.")

    if recipient != "Bob":
        return {
            "error": "John is out of the country right now. Please send a message to Bob instead. Bob will relay the message to John."
        }

    print(f"I sent a message to {recipient} saying {text}.")
    return {"success": True}


async def function_calling() -> None:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=genai.GenerationConfig(
            temperature=0.6,
        ),
        system_instruction="Explain your thoughts. If you made an error, go right ahead and try again. ",
        tools=[send_message],
    )
    chat = model.start_chat(enable_automatic_function_calling=True)
    response = chat.send_message("Send a greeting to John.")
    print(response.text)


class Date(BaseModel):
    """A date entity."""

    day: int = Field(
        description="the day of the month",
    )
    month: int = Field(
        description="the month of the year",
    )
    year: int = Field(
        description="the year",
    )


class Song(BaseModel):
    """A song entity."""

    title: str = Field(
        description="the title of the song",
    )
    artist: str = Field(
        description="the singer or band of the song",
    )
    date: Date = Field(
        description="the date the song was released",
    )


async def json_mode() -> None:
    parser = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
        system_instruction=(
            f"Extract the information into a JSON object of the following JSON schema: {Song.model_json_schema()}."
        ),
    )
    response = parser.generate_content(
        """
Song Title: "Bohemian Rhapsody"
Artist: Queen
Published Date: October 31, 1975

Song Title: "Imagine"
Artist: John Lennon
Published Date: October 11, 1971

Song Title: "Billie Jean"
Artist: Michael Jackson
Published Date: January 2, 1983

Song Title: "Smells Like Teen Spirit"
Artist: Nirvana
Published Date: September 10, 1991

Song Title: "Like a Rolling Stone"
Artist: Bob Dylan
Published Date: July 20, 1965
"""
    )
    json_response = json.loads(response.text)
    print(json_response)


async def main() -> None:
    await function_calling()
    await json_mode()


if __name__ == "__main__":
    asyncio.run(main())

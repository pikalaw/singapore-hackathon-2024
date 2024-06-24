import asyncio
from agents.webber import web_scraper, web_searcher
from datetime import datetime
from devtools import debug
from goog import agent
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


async def current_datetime() -> str:
    """Returns the current date and time.

    Returns:
        The current date and time.
    """
    print("Getting the current date and time.")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class NextTopics(BaseModel):
    """Top 10 topics to search for next."""

    topics: list[str] = Field(
        default_factory=list,
        description="Topics from the article that would enhance the user's experience.",
    )

    @model_validator(mode="after")
    def check_nonempty_list(self) -> Self:
        if len(self.topics) == 0:
            raise ValueError(
                "The list of topics cannot be empty. Please provide some suggestions."
            )
        return self


async def chelsea(request: str) -> NextTopics:
    """Chelsea is an expert in web scraping and web searching.

    Args:
        request: The request to Chelsea.

    Returns:
        The response from Chelsea.
    """
    return await agent.agent(
        NextTopics,
        instruction=(
            "You are an expert in suggesting what are the next list of topics to search on as a followup on some article. "
            "For example, after reading a biography of a famous person, if the article has only a brief description on some key events, you may suggest to search more on that key events as the next step. "
            "Another example: if the article is a photo, spot any interesting object in the photo and suggest to search more about that object."
        ),
        data=request,
        tools=[
            current_datetime,
            web_scraper,
            web_searcher,
        ],
    )


async def main() -> None:
    agent.configure(debug=True)
    suggestions = await chelsea("Who is Goerge Washington?")
    debug(suggestions)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from agents.webber import web_scraper, web_searcher
from datetime import datetime
from devtools import debug
from goog import agent
from pydantic import BaseModel, Field


async def current_datetime() -> str:
    """Returns the current date and time.

    Returns:
        The current date and time.
    """
    print("Getting the current date and time.")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class NextBrowse(BaseModel):
    """Suggestions to browse next."""

    topics: list[str] = Field(
        default_factory=list,
        description="the topics to browse next",
    )


async def chelsea(request: str) -> NextBrowse:
    """Chelsea is an expert in web scraping and web searching.

    Args:
        request: The request to Chelsea.

    Returns:
        The response from Chelsea.
    """
    return await agent.agent(
        NextBrowse,
        instruction="You are an expert in suggesting what are the best topics to follow up on after reading some web content.",
        data=request,
        tools=[
            current_datetime,
            web_scraper,
            web_searcher,
        ],
    )


async def main() -> None:
    agent.configure(debug=True)
    suggestions = await chelsea("Front page of the New York Times today.")
    debug(suggestions)


if __name__ == "__main__":
    asyncio.run(main())

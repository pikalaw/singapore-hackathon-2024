from agents.next_search_recommender import next_search_recommender
import asyncio
from devtools import debug
from goog import agent
from typing_extensions import Self


async def main() -> None:
    agent.configure(debug=True)
    suggestions = await next_search_recommender("Goerge Washington?")
    debug(suggestions)


if __name__ == "__main__":
    asyncio.run(main())

from agents.next_search_recommender import next_search_recommender
import asyncio
from devtools import debug
from goog import agent
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("chelsea.log", mode="w"),
        # logging.StreamHandler(),
    ],
)


async def main() -> None:
    agent.configure(debug=True)

    USER_STYLE = "\u001b[32m\u001b[1m"
    MODEL_STYLE = "\u001b[31m\u001b[1m"
    RESET_STYLE = "\u001b[0m"

    while True:
        user_query = input(f"\n{USER_STYLE}You{RESET_STYLE}: ")
        suggestions = await next_search_recommender(user_query)
        print(f"\n{MODEL_STYLE}Model{RESET_STYLE}: {debug.format(suggestions)}")


if __name__ == "__main__":
    asyncio.run(main())

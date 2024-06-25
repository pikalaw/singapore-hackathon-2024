from agents.webber import web_researcher
from functions.real_time import current_datetime
from goog import agent
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class NextTopics(BaseModel):
    """Top N topics to search for next from an article."""

    original_topic: str = Field(
        description="The original topic that the user searched for.",
    )
    next_topics: list[str] = Field(
        default_factory=list,
        description="Topics from the original article that would enhance the user's experience.",
    )

    @model_validator(mode="after")
    def check_nonempty_list(self) -> Self:
        if not self.next_topics:
            raise ValueError(
                "The list of topics cannot be empty. Please provide some suggestions."
            )
        return self


async def next_search_recommender(request: str) -> NextTopics:
    """next_search_recommender is an expert in suggesting the next topics to search for after reading an article.

    Args:
        request: The request to next_search_recommender.

    Returns:
        The response from next_search_recommender.
    """
    return await agent.agent(
        NextTopics,
        instruction=(
            "You are an expert in suggesting what are the next list of topics to search on as a followup on some article. "
            "For example, after reading a biography of a famous person, if the article has only a brief description on some key events, you may suggest to search more on that key events as the next step. "
            "Another example: if the article is a photo, spot any interesting object in the photo and suggest to search more about that object.\n\n"
            "I will give you a topic or an URL. "
            "If it is a topic, search the internet for a relevant article. "
            "If it is an URL, just fetch the article pointed by the URL. "
            "Read the article carefully and suggest the top 5 topics to search for next. "
        ),
        data=request,
        tools=[
            current_datetime,
            web_researcher,
        ],
        model_name="gemini-1.5-flash-latest",
    )

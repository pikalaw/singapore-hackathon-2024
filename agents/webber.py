from functions.web import web_scrape, web_search
from goog.agent import agent
from .math_professor import math_professor


async def web_researcher(request: str) -> str:
    """web_researcher is an expert in web research.

    Give him a topic and he will find the best information on the internet on that topic.

    Args:
        request: The request to web_researcher.

    Returns:
        The response from web_researcher.
    """
    return await agent(
        str,
        instruction=(
            "You are an expert in web research. "
            "You have two agents who can help you gather the information. "
            "Once they have found you the information, "
            "you will assemble the information into a coherent presentation on the topic."
        ),
        data=request,
        tools=[math_professor, web_searcher, web_scraper],
    )


async def web_searcher(request: str) -> str:
    """web_searcher is an expert in google search.

    Args:
        request: The request to web_searcher.

    Returns:
        The response from web_searcher.
    """
    return await agent(
        str,
        instruction=(
            "You are an expert with Google search. "
            "When you receive a request for a topic, figure out what would be the best query to search for that topic. "
            "Then, use your queries to search the web."
        ),
        data=request,
        tools=[web_search],
    )


async def web_scraper(request: str) -> str:
    """web_scraper is an expert in returning web content from an URL.

    Args:
        request: The request to web_scraper.

    Returns:
        The response from web_scraper.
    """
    return await agent(
        str,
        instruction=(
            "You are an expert at scraping content from an URL. "
            "You know how to extract text and links from a webpage. "
            "Clean up the content and filter out the noise. "
            "Retain only the text and links that can lead to more information on the topic."
        ),
        data=request,
        tools=[web_scrape],
    )

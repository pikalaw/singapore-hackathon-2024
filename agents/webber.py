from functions.web import web_scrape, web_search
from goog.agent import agent


async def web_searcher(request: str) -> str:
    """web_searcher is an expert in google search.

    Args:
        request: The request to web_searcher.

    Returns:
        The response from web_searcher.
    """
    return await agent(
        str,
        instruction="You are an expert with Google search. You know how to find the best query to search for information on the internet.",
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
        instruction="You are an expert at scraping content from an URL. You know how to extract text and links from a webpage.",
        data=request,
        tools=[web_scrape],
    )

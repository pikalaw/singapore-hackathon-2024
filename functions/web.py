from bs4 import BeautifulSoup, Comment, NavigableString
from googlesearch import search
import logging
import urllib.request


async def web_search(query: str, num_results: int) -> str:
    """Search the web for the given query and return the results.

    Call this function to get information that you need to proceed further.

    Args:
      query: The query to search for. Do not pass a URL to this function!
      num_results: The number of results to retrieve.

    Returns:
      A string containing the search results.
    """
    logging.info(f"Searching the web for '{query}'.")
    try:
        results = search(query, num_results=num_results, advanced=True)

        return "\n\n".join(
            [f"Search result for '{query}':"]
            + [
                f"{result.url}\n{result.title}\n{result.description}"
                for result in results
            ]
        )
    except Exception as e:
        raise RuntimeError(f"Failed to search the web for '{query}': {e}.") from e


async def web_scrape(url: str) -> str:
    """Visit the given URL and return the content.

    The content will contain only text and links.
    Other media like images, videos, and audio will be omitted.

    Args:
      url: The URL to visit.

    Returns:
      A string containing the content of the page.
    """
    logging.info(f"Scraping the web for '{url}'.")
    with urllib.request.urlopen(url) as response:
        content_type = response.headers.get("Content-Type")

        if "text/html" in content_type:
            html_content = response.read().decode("utf-8")
            soup = BeautifulSoup(html_content, "html.parser")
            title_text = _extract_title(soup)
            text_and_links = _extract_text_and_links(soup.body)
            return f"URL: {url}\nTitle: {title_text}\n{text_and_links}"
        else:
            raise NotImplementedError(f"Content type {content_type} not supported")


def _extract_title(soup):
    title_tag = soup.find("title")
    return title_tag.text if title_tag else "No title found"


def _extract_text_and_links(element):
    parts = []
    for content in element:
        if isinstance(content, NavigableString):
            # Direct string, just add it
            parts.append(str(content))
        elif content.name == "a":
            href = content.get("href", "")
            # Check if the link is a JavaScript call or an anchor link
            if href.startswith("http://") or href.startswith("https://"):
                # It's a valid external or different page link, format it in markdown
                parts.append(f"[{content.get_text()}]({href})")
            else:
                # Skip others like JavaScript calls and anchor links, add only the text
                parts.append(content.get_text())
        elif content.name in ["script", "style", "iframe", "noscript"]:
            # Skip all elements that are usually not necessary for text extraction
            continue
        elif isinstance(content, Comment):
            # Skip HTML comments
            continue
        else:
            # It's another tag, recurse
            parts.append(_extract_text_and_links(content))
    return "".join(parts)

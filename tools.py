import os
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient


load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env file.")

tavily = TavilyClient(api_key=TAVILY_API_KEY)


# Search multiple sources using Tavily
@tool
def web_search(query: str) -> str:
    """Search the web and return multiple relevant sources."""

    results = tavily.search(
        query=query,
        max_results=5
    )

    output = []
    seen_urls = set()

    for i, result in enumerate(
        results.get("results", []),
        start=1
    ):
        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "")

        if not url or url in seen_urls:
            continue

        seen_urls.add(url)

        output.append(
            f"SOURCE_{i}\n"
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Snippet: {content[:400]}"
        )

    if not output:
        return "No search results found."

    return "\n\n--------------------\n\n".join(output)


# Scrape multiple research sources
@tool
def scrape_multiple_urls(urls: str) -> str:
    """Scrape multiple URLs and return their readable content."""

    results = []

    for i, url in enumerate(
        urls.splitlines(),
        start=1
    ):
        url = url.strip()

        if not url:
            continue

        try:
            response = requests.get(
                url,
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            for tag in soup([
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside"
            ]):
                tag.decompose()

            text = soup.get_text(
                separator=" ",
                strip=True
            )

            results.append(
                f"SOURCE_{i}\n"
                f"URL: {url}\n"
                f"CONTENT:\n{text[:3000]}"
            )

        except Exception as e:
            results.append(
                f"SOURCE_{i}\n"
                f"URL: {url}\n"
                f"ERROR: {str(e)}"
            )

    if not results:
        return "No sources could be scraped."

    return "\n\n====================\n\n".join(results)
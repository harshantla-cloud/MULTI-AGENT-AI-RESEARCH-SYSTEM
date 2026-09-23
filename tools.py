import os
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient


# Load environment variables from .env
load_dotenv()


# Initialize Tavily client using the API key from .env
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in .env file.")

tavily = TavilyClient(api_key=TAVILY_API_KEY)


# Search the web using Tavily
@tool
def web_search(query: str) -> str:
    """Search the web and return relevant titles, URLs and snippets."""

    results = tavily.search(
        query=query,
        max_results=5
    )

    output = []

    for result in results.get("results", []):
        title = result.get("title", "No title available")
        url = result.get("url", "No URL available")
        content = result.get("content", "")

        output.append(
            f"Title: {title}\n"
            f"URL: {url}\n"
            f"Snippet: {content[:300]}"
        )

    if not output:
        return "No search results found."

    return "\n--------------------\n".join(output)


# Scrape and extract readable text from a webpage
@tool
def scrape_url(url: str) -> str:
    """Scrape a webpage and return clean text content."""

    try:
        # Send HTTP request with a browser-like User-Agent
        response = requests.get(
            url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        response.raise_for_status()

        # Parse the webpage HTML
        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove elements that are not part of the main content
        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside"
        ]):
            tag.decompose()

        # Extract clean text from the webpage
        text = soup.get_text(
            separator=" ",
            strip=True
        )

        # Limit the text sent to the LLM
        return text[:3000]

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"


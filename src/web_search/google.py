import asyncio
from typing import Any, Coroutine, Dict, List
from urllib.parse import unquote

import httpx
from bs4 import BeautifulSoup

from .config import GoogleSearchConfig, SearchResult

GOOGLE_SEARCH_URL = "https://www.googleapis.com/customsearch/v1"


class GoogleSearch:
    google_config: GoogleSearchConfig

    def __init__(self, google_config: GoogleSearchConfig | None = None):
        self.google_config = google_config if google_config else GoogleSearchConfig()

    async def _compile_google_search(self, query: str):
        results = await self._google_search(query)
        return "\n\n".join(str(item) for item in results if item.preview)

    async def _google_search(self, query: str, **kwargs):
        """
        Perform a Google search using the Custom Search Engine API
        """
        params = {
            "q": unquote(query),
            "key": self.google_config.api_key,
            "cx": self.google_config.cse_id,
            "num": 5,
        }
        params.update(kwargs)
        headers = {"Referer": self.google_config.app_domain or ""}

        async with httpx.AsyncClient() as client:
            response = await client.get(GOOGLE_SEARCH_URL, params=params, headers=headers)
            response.raise_for_status()

            json_data = response.json()

        items = json_data.get("items", [])[: self.google_config.max_results]
        result = await self.extract_relevant_items(items)
        return result

    async def extract_relevant_items(self, search_results: List[Dict[str, Any]]) -> List[SearchResult]:
        """
        Extract relevant items from the search results
        """
        tasks: list[Coroutine[Any, Any, SearchResult | None]] = []

        for item in search_results:
            url = item.get("link")
            if url and self._is_valid_url(url):
                tasks.append(self._process_search_item(url, item))

        if not tasks:
            return []

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [item for item in results if isinstance(item, SearchResult)]

    def _is_valid_url(self, url: str) -> bool:
        invalid_extensions = (
            ".pdf",
            ".doc",
            ".docx",
            ".ppt",
            ".pptx",
            ".xls",
            ".xlsx",
            ".zip",
            ".rar",
        )
        invalid_domains = ("youtube.com", "vimeo.com", "facebook.com", "twitter.com")
        return not (url.endswith(invalid_extensions) or any(domain in url for domain in invalid_domains))

    async def _process_search_item(self, url: str, item: Dict, char_limit=2000) -> SearchResult | None:
        """
        Process and fetch the result of a single search item url
        """
        try:
            content = await self._scrape_page_content(url)
            return SearchResult(url=url, title=item.get("title", ""), preview=content[:char_limit])
        except Exception:
            return None

    async def _scrape_page_content(self, url: str) -> str:
        """
        Fetch and extract content from a webpage
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            # Remove unwanted elements
            for element in soup.find_all(["script", "style", "nav", "header", "footer", "ads"]):
                element.decompose()

            content_elements = soup.find_all(
                ["article", "main", "div"],
                class_=["content", "article", "post", "entry", "main-content"],
            )

            if not content_elements:
                # Fallback to paragraph extraction if no main content container found
                content_elements = soup.find_all("p")

            # Extract text from found elements
            content = "\n".join(
                element.get_text(strip=True) for element in content_elements if element.get_text(strip=True)
            )

            # If still no content, try getting all text
            if not content:
                content = soup.get_text(strip=True)

            return self._clean_content(content)
        except Exception:
            return ""

    def _clean_content(self, content: str) -> str:
        """Remove very short lines (likely navigation/menu items)"""
        content = " ".join(content.split())
        lines = [line for line in content.split("\n") if len(line) > 30]
        return "\n".join(lines)

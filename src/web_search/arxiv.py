from typing import List

import httpx
from bs4 import BeautifulSoup, Tag

from .base import BaseSearch, SearchResult
from .config import BaseConfig


class ArxivSearch(BaseSearch):
    arxiv_config: BaseConfig

    def __init__(self, arxiv_config: BaseConfig | None = None):
        self.arxiv_config = arxiv_config if arxiv_config else BaseConfig()

    async def _handle(self, query: str) -> List[SearchResult]:
        return await self._search(query)

    async def _compile(self, query: str) -> str:
        results = await self._search(query)
        return "\n\n".join(str(r) for r in results)

    async def _search(self, query: str) -> List[SearchResult]:
        """
        Search by fetching papers from arXiv
        """
        if not query:
            raise ValueError("Search query cannot be empty")

        ARXIV_URL = "https://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": self.arxiv_config.max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        async with httpx.AsyncClient(timeout=self.arxiv_config.timeout) as client:
            response = await client.get(ARXIV_URL, params=params)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml-xml")
        entries = soup.find_all("entry")

        sources: List[SearchResult] = []
        for entry in entries:
            source = self._extract_search_result(entry)
            if source:
                sources.append(source)

        return sources

    def _extract_search_result(self, entry: Tag):
        try:
            url = entry.id.text.strip() if entry.id else ""
            title = entry.title.text.strip() if entry.title else ""
            preview = entry.summary.text.strip() if entry.summary else ""
            if preview:
                return SearchResult(url=url, title=title, preview=preview, source="arxiv")
        except Exception:
            pass
        return None

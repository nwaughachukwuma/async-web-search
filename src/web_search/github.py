from typing import Dict, List

import httpx

from .base import BaseSearch, SearchResult
from .config import BaseConfig


class GitHubSearch(BaseSearch):
    github_config: BaseConfig

    def __init__(self, github_config: BaseConfig | None = None):
        self.github_config = github_config if github_config else BaseConfig()

    async def _handle(self, query: str) -> List[SearchResult]:
        return await self._search(query)

    async def _compile(self, query: str) -> str:
        results = await self._search(query)
        return "\n\n".join(str(r) for r in results)

    async def _search(self, query: str) -> List[SearchResult]:
        """
        Search GitHub repositories
        """
        if not query:
            raise ValueError("Search query cannot be empty")

        GITHUB_URL = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "per_page": self.github_config.max_results,
            "sort": "stars",
            "order": "desc",
        }

        async with httpx.AsyncClient(timeout=self.github_config.timeout) as client:
            response = await client.get(GITHUB_URL, params=params)
            response.raise_for_status()
            data = response.json()

        items = data.get("items", [])
        sources: List[SearchResult] = []
        for item in items:
            source = self._extract_search_result(item)
            if source:
                sources.append(source)

        return sources

    def _extract_search_result(self, item: Dict):
        try:
            url = item.get("html_url", "")
            title = item.get("name", "")
            preview = item.get("description", "") or ""
            if preview:
                if len(preview) > self.github_config.max_preview_chars:
                    preview = preview[: self.github_config.max_preview_chars] + "..."
                return SearchResult(url=url, title=title, preview=preview, source="github")
        except Exception:
            pass
        return None

from typing import Dict, List

import httpx

from .base import BaseSearch, SearchResult
from .config import NewsAPISearchConfig


class NewsAPISearch(BaseSearch):
    newsapi_config: NewsAPISearchConfig

    def __init__(self, newsapi_config: NewsAPISearchConfig | None = None):
        self.newsapi_config = newsapi_config if newsapi_config else NewsAPISearchConfig()

    async def _handle(self, query: str) -> List[SearchResult]:
        return await self._search(query)

    async def _compile(self, query: str) -> str:
        results = await self._search(query)
        return "\n\n".join(str(r) for r in results)

    async def _search(self, query: str) -> List[SearchResult]:
        """
        Search news articles using NewsAPI
        """
        if not query:
            raise ValueError("Search query cannot be empty")

        NEWSAPI_URL = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": self.newsapi_config.api_key,
            "pageSize": self.newsapi_config.max_results,
            "sortBy": "relevancy",
        }

        async with httpx.AsyncClient(timeout=self.newsapi_config.timeout) as client:
            response = await client.get(NEWSAPI_URL, params=params)
            response.raise_for_status()
            data = response.json()

        articles = data.get("articles", [])
        sources: List[SearchResult] = []
        for article in articles:
            source = self._extract_search_result(article)
            if source:
                sources.append(source)

        return sources

    def _extract_search_result(self, article: Dict):
        try:
            url = article.get("url", "")
            title = article.get("title", "")
            preview = article.get("description", "") or ""
            if preview:
                if len(preview) > self.newsapi_config.max_preview_chars:
                    preview = preview[: self.newsapi_config.max_preview_chars] + "..."
                return SearchResult(url=url, title=title, preview=preview, source="newsapi")
        except Exception:
            pass
        return None

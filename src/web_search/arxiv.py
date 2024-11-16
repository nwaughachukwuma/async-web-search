import httpx
from bs4 import BeautifulSoup

from .base import BaseSearch, SearchResult


class ArxivSearch(BaseSearch):
    async def _compile(self, query: str) -> str:
        results = await self._search_arxiv_papers(query)
        return "\n\n".join(str(item) for item in results)

    async def _search(self, query: str) -> list[SearchResult]:
        """
        Fetch papers from arXiv and other scientific sources
        """
        ARXIV_URL = "http://export.arxiv.org/api/query"
        try:
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": self.knowledge_config.max_results,
                "sortBy": "relevance",
                "sortOrder": "descending",
            }
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(ARXIV_URL, params=params)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml-xml")
            entries = soup.find_all("entry")

            sources: list[SearchResult] = []
            for entry in entries:
                title = entry.title.text.strip()
                url = entry.id.text.strip()
                preview = entry.summary.text.strip()

                if not preview:
                    continue

                sources.append(SearchResult(url=url, title=title, preview=preview))

            return sources
        except Exception:
            return []

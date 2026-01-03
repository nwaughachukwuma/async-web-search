import httpx

from .base import BaseSearch, SearchResult
from .config import BaseConfig


class PubMedSearch(BaseSearch):
    pubmed_config: BaseConfig

    def __init__(self, pubmed_config: BaseConfig | None = None):
        self.pubmed_config = pubmed_config if pubmed_config else BaseConfig()

    async def _compile(self, query: str) -> str:
        results = await self._search(query)
        return "\n\n".join(str(r) for r in results)

    async def _search(self, query: str) -> list[SearchResult]:
        """
        Search PubMed articles
        """
        if not query:
            raise ValueError("Search query cannot be empty")

        # First, search for IDs
        ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query,
            "retmax": self.pubmed_config.max_results,
            "retmode": "json",
        }

        async with httpx.AsyncClient(
            timeout=self.pubmed_config.timeout, headers={"User-Agent": "async-web-search/1.0"}
        ) as client:
            search_response = await client.get(ESEARCH_URL, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

        idlist = search_data.get("esearchresult", {}).get("idlist", [])
        if not idlist:
            return []

        # Then, get summaries
        ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            "db": "pubmed",
            "id": ",".join(idlist),
            "retmode": "json",
        }

        async with httpx.AsyncClient(
            timeout=self.pubmed_config.timeout, headers={"User-Agent": "async-web-search/1.0"}
        ) as client:
            summary_response = await client.get(ESUMMARY_URL, params=summary_params)
            summary_response.raise_for_status()
            summary_data = summary_response.json()

        result = summary_data.get("result", {})
        sources: list[SearchResult] = []
        for uid in idlist:
            article = result.get(uid)
            if article:
                source = self._extract_search_result(article)
                if source:
                    sources.append(source)

        return sources

    def _extract_search_result(self, article: dict):
        try:
            uid = article.get("uid", "")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
            title = article.get("title", "")
            # Use title as preview if no description
            preview = article.get("description", [{}])[0].get("value", "") if article.get("description") else title
            if preview:
                if len(preview) > self.pubmed_config.max_preview_chars:
                    preview = preview[: self.pubmed_config.max_preview_chars] + "..."
                return SearchResult(url=url, title=title, preview=preview)
        except Exception:
            pass
        return None

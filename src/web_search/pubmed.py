import asyncio
import xml.etree.ElementTree as ET
from typing import Dict, List

import httpx

from .base import BaseSearch, SearchResult
from .config import BaseConfig


class PubMedSearch(BaseSearch):
    pubmed_config: BaseConfig

    def __init__(self, pubmed_config: BaseConfig | None = None):
        self.pubmed_config = pubmed_config if pubmed_config else BaseConfig()

    async def _handle(self, query: str) -> List[SearchResult]:
        return await self._search(query)

    async def _compile(self, query: str) -> str:
        results = await self._search(query)
        return "\n\n".join(str(r) for r in results)

    async def _search(self, query: str) -> List[SearchResult]:
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

        abstracts, summary_data = await asyncio.gather(self._fetch_abstracts(idlist), self._fetch_summaries(idlist))

        result = summary_data.get("result", {})
        sources: List[SearchResult] = []
        for uid in idlist:
            article = result.get(uid)
            if article:
                abstract = abstracts.get(uid, "")
                source = self._extract_search_result(article, abstract)
                if source:
                    sources.append(source)

        return sources

    async def _fetch_abstracts(self, idlist: List[str]) -> Dict[str, str]:
        """Fetch abstracts for given PubMed IDs"""
        EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        fetch_params = {"db": "pubmed", "id": ",".join(idlist), "retmode": "xml", "rettype": "abstract"}

        try:
            async with httpx.AsyncClient(
                timeout=self.pubmed_config.timeout, headers={"User-Agent": "async-web-search/1.0"}
            ) as client:
                fetch_response = await client.get(EFETCH_URL, params=fetch_params)
                fetch_response.raise_for_status()
                xml_data = fetch_response.text

            # Parse XML to extract abstracts
            root = ET.fromstring(xml_data)
            abstracts = {}

            for article in root.findall(".//PubmedArticle"):
                pmid_elem = article.find(".//PMID")
                abstract_elem = article.find(".//AbstractText")

                if pmid_elem is not None and abstract_elem is not None:
                    pmid = pmid_elem.text
                    abstract_text = "".join(abstract_elem.itertext())
                    abstracts[pmid] = abstract_text

            return abstracts
        except Exception:
            return {}

    async def _fetch_summaries(self, idlist: List[str]) -> Dict:
        """Fetch summaries for given PubMed IDs"""
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
            return summary_response.json()

    def _build_preview(self, article: Dict) -> str:
        """
        Build preview text from abstract or metadata
        """
        parts = []
        if journal := article.get("source"):
            parts.append(journal)
        if pubdate := article.get("pubdate"):
            parts.append(pubdate)
        if authors := article.get("authors"):
            if authors and len(authors) > 0:
                first_author = authors[0].get("name", "")
                if first_author:
                    parts.append(f"by {first_author} et al.")

        if not parts:
            raise ValueError("No metadata available for preview")

        return " | ".join(parts)

    def _extract_search_result(self, article: Dict, abstract: str):
        try:
            uid = article.get("uid", "")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
            title = article.get("title", "")
            preview = abstract if abstract else self._build_preview(article)

            return SearchResult(
                url=url,
                title=title,
                preview=preview,
                source="pubmed",
            )
        except Exception:
            pass
        return None

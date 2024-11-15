import asyncio

import httpx
import wikipedia
from bs4 import BeautifulSoup
from .config import KnowledgeSearchConfig, SearchResult


class KnowledgeSearch:
    knowledge_config: KnowledgeSearchConfig

    def __init__(self, knowledge_config: KnowledgeSearchConfig | None = None):
        self.knowledge_config = knowledge_config if knowledge_config else KnowledgeSearchConfig()

    async def fetch_knowledge(self, query: str):
        """
        Fetch knowledge from multiple sources concurrently,
        including Wikipedia, arXiv, and other scientific sources
        """
        # listed in order of importance
        tasks = [
            self._search_wikipedia(query),
            self._search_arxiv_papers(query),
            # add more knowledge sources here
        ]

        sources: list[SearchResult] = []

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, list):
                sources.extend(result)

        sources = sources[: self.knowledge_config.max_sources]
        return "\n\n".join(str(source) for source in sources if source.preview)

    async def _compile_wikipedia(self, query: str) -> str:
        results = await self._search_wikipedia(query)
        return "\n\n".join(str(item) for item in results)

    async def _compile_arxiv_papers(self, query: str) -> str:
        results = await self._search_arxiv_papers(query)
        return "\n\n".join(str(item) for item in results)

    async def _search_wikipedia(self, query: str) -> list[SearchResult]:
        """
        Fetch relevant Wikipedia articles
        """
        try:
            sources: list[SearchResult] = []
            search_results = wikipedia.search(query, results=self.knowledge_config.max_results)

            for title in search_results:
                try:
                    page = wikipedia.page(title)
                    if not page.content:
                        continue

                    preview = self._extract_relevant_wiki_sections(page.content)
                    if not preview:
                        continue

                    sources.append(SearchResult(url=page.url, title=page.title, preview=preview))
                except wikipedia.exceptions.DisambiguationError:
                    continue
                except wikipedia.exceptions.PageError:
                    continue

            return sources
        except Exception:
            return []

    async def _search_arxiv_papers(self, query: str) -> list[SearchResult]:
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

    def _extract_relevant_wiki_sections(self, content: str) -> str:
        """
        Extract the most relevant sections from Wikipedia content
        """
        paragraphs = content.split("\n\n")
        # Remove references and other metadata
        cleaned_paragraphs = [
            p
            for p in paragraphs
            if not any(
                marker in p.lower()
                for marker in [
                    "references",
                    "external links",
                    "see also",
                    "== notes ==",
                ]
            )
        ]

        result = ""
        for p in cleaned_paragraphs:
            if len(result + p) <= self.knowledge_config.max_preview_chars:
                result += p + "\n\n"
            else:
                break

        return result.strip()

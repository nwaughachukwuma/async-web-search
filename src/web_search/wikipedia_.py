from typing import List

import wikipedia as wiki

from .base import BaseSearch, SearchResult
from .config import BaseConfig


class WikipediaSearch(BaseSearch):
    wiki_config: BaseConfig

    def __init__(self, wiki_config: BaseConfig | None = None):
        self.wiki_config = wiki_config if wiki_config else BaseConfig()

    async def _handle(self, query: str) -> List[SearchResult]:
        return await self._search(query)

    async def _compile(self, query: str) -> str:
        results = await self._search(query)
        return "\n\n".join(str(r) for r in results)

    async def _search(self, query: str) -> List[SearchResult]:
        """
        search Wikipedia for relevant articles
        """
        if not query:
            raise ValueError("Search query cannot be empty")

        sources: List[SearchResult] = []
        search_results = wiki.search(query, results=self.wiki_config.max_results)

        for title in search_results:
            try:
                page = wiki.page(title)
                if not page.content:
                    continue

                preview = self._extract_relevant_wiki_sections(page.content)
                if not preview:
                    continue

                sources.append(
                    SearchResult(
                        url=page.url,
                        title=page.title,
                        preview=preview,
                        source="wikipedia",
                    )
                )
            except (wiki.exceptions.DisambiguationError, wiki.exceptions.PageError):
                continue

        return sources

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

        return "\n\n".join(p for p in cleaned_paragraphs).strip()

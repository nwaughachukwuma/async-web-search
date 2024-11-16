import wikipedia

from .base import BaseSearch, SearchResult
from .config import BaseConfig


class WikipediaSearch(BaseSearch):
    wiki_config: BaseConfig

    def __init__(self, wiki_config: BaseConfig | None = None):
        self.wiki_config = wiki_config if wiki_config else BaseConfig()

    async def _compile(self, query: str) -> str:
        results = await self._search(query)
        return "\n\n".join(str(item) for item in results)

    async def _search(self, query: str) -> list[SearchResult]:
        """
        search Wikipedia for relevant articles
        """
        if not query:
            raise ValueError("Search query cannot be empty")

        try:
            sources: list[SearchResult] = []
            search_results = wikipedia.search(query, results=self.wiki_config.max_results)

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
            if len(result + p) <= self.wiki_config.max_preview_chars:
                result += p + "\n\n"
            else:
                break

        return result.strip()

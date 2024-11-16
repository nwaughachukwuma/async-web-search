import asyncio
from typing import Any, Coroutine, List

from .arxiv import ArxivSearch
from .config import WebSearchConfig
from .google import GoogleSearch
from .wikipedia import WikipediaSearch


class WebSearch:
    def __init__(self, config: WebSearchConfig | None = None):
        self.config = config if config else WebSearchConfig()

        self.google = GoogleSearch(google_config=self.config.google_config)
        self.arxiv = ArxivSearch(arxiv_config=self.config.arxiv_config)
        self.wikipedia = WikipediaSearch(wiki_config=self.config.wiki_config)

    async def search(self, query: str):
        """
        Search the web for relevant content
        """
        tasks: List[Coroutine[Any, Any, str]] = []

        if "google" in self.config.sources:
            tasks.append(self.google._compile(query))
        if "wikipedia" in self.config.sources:
            tasks.append(self.wikipedia._compile(query))
        if "arxiv" in self.config.sources:
            tasks.append(self.arxiv._compile(query))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return "\n\n".join(item for item in results if isinstance(item, str))

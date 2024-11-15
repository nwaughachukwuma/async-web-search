import asyncio
from typing import Any, Coroutine, List

from .google import GoogleSearch
from .knowledge import KnowledgeSearch
from .config import WebSearchConfig


class WebSearch(GoogleSearch, KnowledgeSearch):
    def __init__(self, config: WebSearchConfig | None = None):
        self.config = config if config else WebSearchConfig()

        self.sources = self.config.sources
        GoogleSearch.__init__(self, self.config.google_config)
        KnowledgeSearch.__init__(self, config=self.config.knowledge_config)

    async def search(self, query: str):
        """
        Search the web for relevant content
        """
        tasks: List[Coroutine[Any, Any, str]] = []

        if "google" in self.sources:
            tasks.append(self._compile_google_search(query))
        if "wikipedia" in self.sources:
            tasks.append(self._compile_wikipedia(query))
        if "arxiv" in self.sources:
            tasks.append(self._compile_arxiv_papers(query))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return "\n\n".join(item for item in results if isinstance(item, str))

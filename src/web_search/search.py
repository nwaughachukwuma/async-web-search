import asyncio
from typing import Any, Coroutine, List

from .config import WebSearchConfig
from .google import GoogleSearch
from .knowledge import KnowledgeSearch


class WebSearch(GoogleSearch, KnowledgeSearch):
    def __init__(self, config: WebSearchConfig | None = None):
        ws_config = config if config else WebSearchConfig()

        GoogleSearch.__init__(self, google_config=ws_config.google_config)
        KnowledgeSearch.__init__(self, knowledge_config=ws_config.knowledge_config)
        self.sources = ws_config.sources

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

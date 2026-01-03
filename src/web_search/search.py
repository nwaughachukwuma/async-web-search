import asyncio
from typing import Any, Coroutine, List

from .arxiv import ArxivSearch
from .base import SearchResult
from .config import WebSearchConfig
from .github import GitHubSearch
from .google import GoogleSearch
from .newsapi import NewsAPISearch
from .pubmed import PubMedSearch
from .wikipedia_ import WikipediaSearch


class WebSearch:
    config: WebSearchConfig

    def __init__(self, config: WebSearchConfig | None = None):
        self.config = config if config else WebSearchConfig()

        self.google = GoogleSearch(google_config=self.config.google_config)
        self.arxiv = ArxivSearch(arxiv_config=self.config.arxiv_config)
        self.wikipedia = WikipediaSearch(wiki_config=self.config.wiki_config)
        self.newsapi = NewsAPISearch(newsapi_config=self.config.newsapi_config)
        self.github = GitHubSearch(github_config=self.config.github_config)
        self.pubmed = PubMedSearch(pubmed_config=self.config.pubmed_config)

    async def compile_search(self, query: str):
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
        if "newsapi" in self.config.sources:
            tasks.append(self.newsapi._compile(query))
        if "github" in self.config.sources:
            tasks.append(self.github._compile(query))
        if "pubmed" in self.config.sources:
            tasks.append(self.pubmed._compile(query))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return "\n\n".join(r for r in results if isinstance(r, str))

    async def search(self, query: str) -> List[SearchResult]:
        """
        Search the web for relevant content and return structured results
        """
        tasks: List[Coroutine[Any, Any, List[SearchResult]]] = []

        if "google" in self.config.sources:
            tasks.append(self.google._handle(query))
        if "wikipedia" in self.config.sources:
            tasks.append(self.wikipedia._handle(query))
        if "arxiv" in self.config.sources:
            tasks.append(self.arxiv._handle(query))
        if "newsapi" in self.config.sources:
            tasks.append(self.newsapi._handle(query))
        if "github" in self.config.sources:
            tasks.append(self.github._handle(query))
        if "pubmed" in self.config.sources:
            tasks.append(self.pubmed._handle(query))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [item for r in results if not isinstance(r, BaseException) for item in r]

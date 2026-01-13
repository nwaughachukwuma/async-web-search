import asyncio
from typing import Dict, Generator, List

from .arxiv import ArxivSearch
from .base import BaseSearch, PluginSearch
from .config import WebSearchConfig
from .github import GitHubSearch
from .google import GoogleSearch
from .newsapi import NewsAPISearch
from .pubmed import PubMedSearch
from .wikipedia_ import WikipediaSearch


class WebSearch:
    config: WebSearchConfig
    plugins: List[PluginSearch] = []

    def __init__(self, config: WebSearchConfig | None = None):
        self.config = config if config else WebSearchConfig()

        # Built-in sources
        self.google = GoogleSearch(google_config=self.config.google_config)
        self.arxiv = ArxivSearch(arxiv_config=self.config.arxiv_config)
        self.wikipedia = WikipediaSearch(wiki_config=self.config.wiki_config)
        self.newsapi = NewsAPISearch(newsapi_config=self.config.newsapi_config)
        self.github = GitHubSearch(github_config=self.config.github_config)
        self.pubmed = PubMedSearch(pubmed_config=self.config.pubmed_config)

        # User-supplied plugins
        self.plugins = [p for p in self.config.plugins if isinstance(p, PluginSearch)]

    def gather(self) -> Generator[BaseSearch]:
        """
        Gather the relevant search tasks/logic and plugin
        """
        if "google" in self.config.sources:
            yield self.google
        if "wikipedia" in self.config.sources:
            yield self.wikipedia
        if "arxiv" in self.config.sources:
            yield self.arxiv
        if "newsapi" in self.config.sources:
            yield self.newsapi
        if "github" in self.config.sources:
            yield self.github
        if "pubmed" in self.config.sources:
            yield self.pubmed

        for plugin in self.plugins:
            yield plugin

    async def search(self, query: str) -> List[Dict[str, str]]:
        """
        Search the web for relevant content and return structured results
        """
        coros = [task._search(query) for task in self.gather()]
        results = await asyncio.gather(*coros, return_exceptions=True)

        return [item.to_dict() for r in results if not isinstance(r, BaseException) for item in r]

    async def compile_search(self, query: str):
        """
        Search the web for relevant content and compile into a string
        """
        coros = [task._compile(query) for task in self.gather()]
        results = await asyncio.gather(*coros, return_exceptions=True)

        return "\n\n".join(r for r in results if isinstance(r, str))

    def add_plugin(self, plugins: List[PluginSearch]):
        """
        Add plugins to the web search instance
        """
        self.plugins.extend(plugins)

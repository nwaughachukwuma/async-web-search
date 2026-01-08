from dataclasses import dataclass

from .config import SearchSources


@dataclass
class SearchResult:
    url: str
    title: str
    preview: str
    source: SearchSources

    def __str__(self):
        return f"Source: {self.source}\nTitle: {self.title}\nPreview: {self.preview}"

    def to_dict(self):
        """Convert SearchResult to a dictionary."""
        return {
            "url": self.url,
            "title": self.title,
            "preview": self.preview,
            "source": str(self.source),
        }


class BaseSearch:
    async def _search(self, _query: str):
        """
        Context based search algorithm and workflow.
        Args:
            query (str): The search query string.
        Return:
            A list of `SearchResult` objects for a query.
        """
        raise NotImplementedError

    async def _compile(self, _query: str) -> str:
        """
        Search and compile the result into a string
        Args:
            query (str): The search query string.
        Return:
            A formatted string representation of search results.
        """
        ...


class PluginSearch(BaseSearch):
    slug: str

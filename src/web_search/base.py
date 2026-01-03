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


class BaseSearch:
    def _handle(self, _query: str):
        """main search handler with json response"""
        pass

    def _compile(self, _query: str):
        """search and compile the result into a string"""
        pass

    def _search(self, _query: str):
        """context based search algorithm and workflow"""
        pass

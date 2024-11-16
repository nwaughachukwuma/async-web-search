from dataclasses import dataclass


@dataclass
class SearchResult:
    url: str
    title: str
    preview: str

    def __str__(self):
        return f"Title: {self.title}\nPreview: {self.preview}"


class BaseSearch:
    def _compile(self, _query: str):
        """search and compile the result into a string"""
        pass

    def _search(self, _query: str):
        """context based search algorithm and workflow"""
        pass

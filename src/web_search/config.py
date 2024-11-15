from dataclasses import dataclass, field
import os
from typing import Literal

SearchSources = Literal["google", "wikipedia", "arxiv"]


@dataclass
class GoogleSearchConfig:
    api_key: str = os.environ["GOOGLE_API_KEY"]
    cse_id: str = os.environ["CSE_ID"]
    max_results: int = 3
    app_domain: str | None = None


@dataclass
class KnowledgeSearchConfig:
    max_results: int = 3
    max_sources: int = 10
    max_preview_chars: int = 1024


@dataclass
class WebSearchConfig:
    sources: list[SearchSources] = field(default_factory=lambda: ["google"])
    google_config: GoogleSearchConfig | None = None
    knowledge_config: KnowledgeSearchConfig | None = None


@dataclass
class SearchResult:
    url: str
    title: str
    preview: str

    def __str__(self):
        return f"Title: {self.title}\nPreview: {self.preview}"

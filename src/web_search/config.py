import os
from dataclasses import dataclass, field
from typing import Literal

SearchSources = Literal["google", "wikipedia", "arxiv", "newsapi", "github", "pubmed"]


@dataclass
class BaseConfig:
    max_results: int = 3
    max_preview_chars: int = 1024
    timeout: float | None = None


@dataclass
class GoogleSearchConfig(BaseConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("GOOGLE_API_KEY", ""))
    cse_id: str = field(default_factory=lambda: os.environ.get("CSE_ID", ""))
    app_domain: str | None = None


@dataclass
class NewsAPISearchConfig(BaseConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("NEWSAPI_KEY", ""))


@dataclass
class WebSearchConfig:
    sources: list[SearchSources] = field(default_factory=lambda: ["google"])
    google_config: GoogleSearchConfig | None = None
    wiki_config: BaseConfig | None = None
    arxiv_config: BaseConfig | None = None
    newsapi_config: NewsAPISearchConfig | None = None
    github_config: BaseConfig | None = None
    pubmed_config: BaseConfig | None = None

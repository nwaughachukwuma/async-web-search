import os
from dataclasses import dataclass, field
from typing import Literal, List

SearchSources = Literal["google", "wikipedia", "arxiv", "newsapi", "github", "pubmed"]


@dataclass
class BaseConfig:
    max_results: int = 3
    timeout: float | None = None


@dataclass
class GoogleSearchConfig(BaseConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("GOOGLE_API_KEY", ""))
    cse_id: str = field(default_factory=lambda: os.environ.get("CSE_ID", ""))
    app_domain: str | None = None


@dataclass
class NewsAPISearchConfig(BaseConfig):
    api_key: str = field(default_factory=lambda: os.environ.get("NEWS_API_KEY", ""))


@dataclass
class WebSearchConfig:
    sources: List[SearchSources] = field(default_factory=lambda: ["google"])
    google_config: GoogleSearchConfig | None = None
    wiki_config: BaseConfig | None = None
    arxiv_config: BaseConfig | None = None
    newsapi_config: NewsAPISearchConfig | None = None
    github_config: BaseConfig | None = None
    pubmed_config: BaseConfig | None = None

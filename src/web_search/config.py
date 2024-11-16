import os
from dataclasses import dataclass, field
from typing import Literal

SearchSources = Literal["google", "wikipedia", "arxiv"]


@dataclass
class BaseConfig:
    max_results: int = 3
    max_preview_chars: int = 1024


@dataclass
class GoogleSearchConfig(BaseConfig):
    api_key: str = os.environ["GOOGLE_API_KEY"]
    cse_id: str = os.environ["CSE_ID"]
    app_domain: str | None = None


@dataclass
class WebSearchConfig:
    sources: list[SearchSources] = field(default_factory=lambda: ["google"])
    google_config: GoogleSearchConfig | None = None
    wiki_config: BaseConfig | None = None
    arxiv_config: BaseConfig | None = None

import os
from typing import List

from fastapi import HTTPException

from web_search import SearchSources


def validate_api_keys(sources: List[SearchSources]):
    if "google" in sources:
        if not os.environ.get("GOOGLE_API_KEY", "") or not os.environ.get("CSE_ID", ""):
            raise HTTPException(500, "GOOGLE_API_KEY or CSE_ID is missing")

    if "newsapi" in sources:
        if not os.environ.get("NEWS_API_KEY", ""):
            raise HTTPException(500, "NEWS_API_KEY is missing")

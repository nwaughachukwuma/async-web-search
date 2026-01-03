from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from web_search import BaseConfig, GoogleSearchConfig, NewsAPISearchConfig, SearchSources, WebSearch, WebSearchConfig

app = FastAPI(title="Async WebSearch Demo", description="Production-scale async web search API")


class SearchRequest(BaseModel):
    query: str
    sources: List[SearchSources] = ["google"]
    max_results: int = 3
    max_preview_chars: int = 1024
    timeout: Optional[float] = None
    google_api_key: Optional[str] = None
    cse_id: Optional[str] = None
    app_domain: Optional[str] = None
    newsapi_key: Optional[str] = None


@app.get("/")
def root():
    return {
        "message": "Async WebSearch Demo API",
        "docs": "/docs",
    }


@app.post("/search")
async def search(request: SearchRequest):
    """
    Perform async web search across multiple sources.

    - **query**: Search query string
    - **sources**: List of sources to search (google, wikipedia, arxiv, newsapi, github, pubmed)
    - **max_results**: Maximum results per source (default: 3)
    - **max_preview_chars**: Maximum characters in preview (default: 1024)
    - **timeout**: Request timeout in seconds (optional)
    - **google_api_key**: Google API key (required if using google source)
    - **cse_id**: Google Custom Search Engine ID (required if using google source)
    - **app_domain**: Google app domain (optional)
    - **newsapi_key**: NewsAPI key (required if using newsapi source)
    """
    # Build configs
    base_config = BaseConfig(
        max_results=request.max_results, max_preview_chars=request.max_preview_chars, timeout=request.timeout
    )

    google_config = None
    if "google" in request.sources:
        if not request.google_api_key or not request.cse_id:
            raise HTTPException(
                status_code=400, detail="google_api_key and cse_id are required when using google source"
            )
        google_config = GoogleSearchConfig(
            api_key=request.google_api_key, cse_id=request.cse_id, app_domain=request.app_domain
        )

    newsapi_config = None
    if "newsapi" in request.sources:
        if not request.newsapi_key:
            raise HTTPException(status_code=400, detail="newsapi_key is required when using newsapi source")
        newsapi_config = NewsAPISearchConfig(api_key=request.newsapi_key)

    # Create WebSearch config
    config = WebSearchConfig(
        sources=request.sources,
        google_config=google_config,
        wiki_config=base_config,
        arxiv_config=base_config,
        newsapi_config=newsapi_config,
        github_config=base_config,
        pubmed_config=base_config,
    )

    # Perform search
    web_search = WebSearch(config)
    results = await web_search.search(request.query)

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from web_search import BaseConfig, GoogleSearchConfig, NewsAPISearchConfig, SearchSources, WebSearch, WebSearchConfig

from .utils import validate_api_keys

app = FastAPI(title="Async WebSearch Demo", description="Production-scale async web search API")


class SearchRequest(BaseModel):
    query: str
    sources: List[SearchSources] = ["google"]
    max_results: int = 3
    max_preview_chars: int = 1024
    timeout: Optional[float] = None


@app.get("/")
def root():
    return {
        "message": "Async WebSearch Demo API",
        "docs": "/docs",
    }


@app.get("/demo", response_class=HTMLResponse)
def demo():
    template_path = os.path.join(os.path.dirname(__file__), "templates", "demo.html")
    with open(template_path, "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.post("/search")
async def search(request: SearchRequest):
    """
    Perform async web search across multiple sources.

    - **query**: Search query string
    - **sources**: List of sources to search (google, wikipedia, arxiv, newsapi, github, pubmed)
    - **max_results**: Maximum results per source (default: 3)
    - **max_preview_chars**: Maximum characters in preview (default: 1024)
    - **timeout**: Request timeout in seconds (optional)
    """
    validate_api_keys(request.sources)

    # Build configs
    base_config = BaseConfig(
        max_results=request.max_results,
        max_preview_chars=request.max_preview_chars,
        timeout=request.timeout,
    )

    google_config: GoogleSearchConfig | None = None
    if "google" in request.sources:
        google_config = GoogleSearchConfig(
            api_key=os.environ["GOOGLE_API_KEY"],
            cse_id=os.environ["CSE_ID"],
            app_domain=os.environ.get("GOOGLE_APP_DOMAIN"),
            max_preview_chars=base_config.max_preview_chars,
            max_results=base_config.max_results,
            timeout=base_config.timeout,
        )

    newsapi_config: NewsAPISearchConfig | None = None
    if "newsapi" in request.sources:
        newsapi_config = NewsAPISearchConfig(
            api_key=os.environ["NEWS_API_KEY"],
            max_preview_chars=base_config.max_preview_chars,
            max_results=base_config.max_results,
            timeout=base_config.timeout,
        )

    # Create WebSearch config
    config = WebSearchConfig(
        sources=request.sources,
        google_config=google_config,
        newsapi_config=newsapi_config,
        wiki_config=base_config,
        arxiv_config=base_config,
        github_config=base_config,
        pubmed_config=base_config,
    )

    # Perform search
    try:
        results = await WebSearch(config).search(request.query)  # type: ignore
        return {"results": results}
    except Exception as e:
        raise HTTPException(500, f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

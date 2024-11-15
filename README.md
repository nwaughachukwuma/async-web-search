# Web Search

Async web search library supporting Google Custom Search, Wikipedia, and arXiv APIs.

## Installation

```bash
pip install async-web-search
```

## Usage

```python
from web_search import WebSearch, WebSearchConfig, GoogleSearchConfig

config = WebSearchConfig(
    sources=["google", "wikipedia"],
    google_config=GoogleSearchConfig(
        api_key="your_google_api_key",
        cse_id="your_cse_id"
    )
)

search = WebSearch(config)
results = await search.search("quantum computing")
print(results)
```

## Features

- Async/concurrent searching
- Multiple source support (Google, Wikipedia, arXiv)
- Content extraction and cleaning
- Configurable search parameters

## License

MIT

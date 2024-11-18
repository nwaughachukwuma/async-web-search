# Web Search

Async web search library supporting Google Custom Search, Wikipedia, and arXiv APIs.

> You can search across multiple sources and retrieve relevant, clean, and formatted results efficiently.

## 🌟 Features

- ⚡ Asynchronous Searching: Perform searches concurrently across multiple sources
- 🔗 Multi-Source Support: Query Google Custom Search, Wikipedia, and arXiv
- 🧹 Content extraction and cleaning
- 🔧 Configurable Search Parameters: Adjust maximum results, preview length, and sources.

## 📋 Prerequisites

- 🐍 Python 3.8 or newer
- 🔑 API keys and configuration:
  - Google Search: Requires a Google API key and a Custom Search Engine (CSE) ID.
  - arXiv: No API key required.
  - Wikipedia: No API key required.

Set environment variables for Google API:

```bash
export GOOGLE_API_KEY="your_google_api_key"
export CSE_ID="your_cse_id"
```

## 📦 Installation

```bash
pip install async-web-search
```

## 🛠️ Usage

### Example 1: Search across multiple sources

```python
from web_search import WebSearch, WebSearchConfig

config = WebSearchConfig(sources=["google", "arxiv"])
results = await WebSearch(config).search("quantum computing")

print(results)
```

### Example 2: Google Search

```python
from web_search import GoogleSearchConfig
from web_search.google import GoogleSearch

config = GoogleSearchConfig(
    api_key="your_google_api_key",
    cse_id="your_cse_id",
    max_results=5
)
results = await GoogleSearch(config)._search("quantum computing")

for result in results:
    print(result)
```

### Example 3: Wikipedia Search

```python
from web_search import BaseConfig
from web_search.wikipedia import WikipediaSearch

wiki_config = BaseConfig(max_results=5, max_preview_chars=500)
results = await WikipediaSearch(wiki_config)._search("deep learning")

for result in results:
    print(result)
```

### Example 4: ArXiv Search

```python
from web_search import BaseConfig
from web_search.arxiv import ArxivSearch

arxiv_config = BaseConfig(max_results=3, max_preview_chars=800)
results = await ArxivSearch(arxiv_config)._search("neural networks")

for result in results:
    print(result)
```

## 📘 API Overview

### 🔧 Configuration

- BaseConfig: Shared configuration for all sources (e.g., max_results, max_preview_chars).
- GoogleSearchConfig: Google-specific settings (e.g., api_key, cse_id).
- WebSearchConfig: Configuration for the overall search process (e.g., sources to query).

### 📚 Classes

- WebSearch: Entry point for performing searches across multiple sources.
- GoogleSearch: Handles searches via Google Custom Search Engine API.
- WikipediaSearch: Searches Wikipedia and retrieves article previews.
- ArxivSearch: Queries arXiv for academic papers.

### ⚙️ Methods

- search(query: str): Main search method for WebSearch.
- \_search(query: str): Source-specific search logic for GoogleSearch, WikipediaSearch, and ArxivSearch.

## 🤝 Contributing

We welcome contributions! To contribute:

- Fork the repository.
- Create a new branch (git checkout -b feature-name).
- Commit your changes (git commit -am "Add new feature").
- Push to the branch (git push origin feature-name).
- Open a pull request.

### 🧪 Running Tests

```bash
pytest -v
```

## License

MIT

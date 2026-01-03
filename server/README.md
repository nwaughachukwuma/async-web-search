## 🌐 Async Web Search API Server

A FastAPI-based production server is available at **https://awebs.veedo.ai** for teams that want to use async web search without installing the library.

### API Endpoint

**POST** `https://awebs.veedo.ai/search`

### Request Payload

```json
{
  "query": "machine learning",
  "sources": ["google", "arxiv", "github"],
  "max_results": 3,
  "max_preview_chars": 1024,
  "timeout": 10.0
}
```

### Response

```json
{
  "results": [
    {
      "url": "https://example.com/article",
      "title": "Example Article Title",
      "preview": "This is a preview of the article content...",
      "source": "google"
    },
    {
      "url": "https://arxiv.org/pdf/1234.5678",
      "title": "ArXiv Paper Title",
      "preview": "Abstract: This paper discusses...",
      "source": "arxiv"
    }
  ]
}
```

### Running Locally

To run the server locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (copy from .env.example and fill in your actual API keys)
cp .env.example .env

# Run the server
python index.py
```

The server will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

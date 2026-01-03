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
  "timeout": 10.0,
  "google_api_key": "your_google_api_key",
  "cse_id": "your_cse_id",
  "app_domain": "your_domain.com",
  "newsapi_key": "your_newsapi_key"
}
```

### Response

```json
{
  "results": "Compiled search results from all specified sources..."
}
```

### Running Locally

To run the server locally:

```bash
pip install -r requirements.txt
python server.py
```

The server will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

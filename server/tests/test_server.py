from unittest.mock import AsyncMock, patch

import pytest


def test_root_endpoint(client):
    """Test the root endpoint returns correct response"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert data["message"] == "Async WebSearch Demo API"
    assert data["docs"] == "/docs"


@pytest.mark.asyncio
async def test_search_successful_request(client):
    """Test successful search request with proper payload"""
    payload = {
        "query": "test query",
        "sources": ["google"],
        "max_results": 2,
    }

    # Mock the WebSearch class
    with patch("src.index.WebSearch") as mock_websearch_class:
        mock_websearch_instance = AsyncMock()
        mock_websearch_instance.search = AsyncMock(
            return_value=[
                {"url": "https://example.com", "title": "Test Result", "preview": "Test preview", "source": "google"}
            ]
        )
        mock_websearch_class.return_value = mock_websearch_instance

        response = client.post("/search", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 1
        assert data["results"][0]["title"] == "Test Result"

        # Verify WebSearch was called with correct config
        mock_websearch_class.assert_called_once()
        # Check that search was called
        mock_websearch_instance.search.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_search_missing_google_keys(client, monkeypatch):
    """Test search request fails when Google API keys are missing from environment"""
    payload = {
        "query": "test query",
        "sources": ["google"],
        "max_results": 2,
    }

    # Mock missing environment variables by setting them to empty strings
    monkeypatch.setenv("GOOGLE_API_KEY", "")
    monkeypatch.setenv("CSE_ID", "")

    response = client.post("/search", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "GOOGLE_API_KEY or CSE_ID is missing" in data["detail"]


@pytest.mark.asyncio
async def test_search_missing_newsapi_key(client, monkeypatch):
    """Test search request fails when NewsAPI key is missing from environment"""
    payload = {
        "query": "test query",
        "sources": ["newsapi"],
        "max_results": 2,
    }

    # Mock missing environment variable by setting it to empty string
    monkeypatch.setenv("NEWS_API_KEY", "")

    response = client.post("/search", json=payload)

    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "NEWS_API_KEY is missing" in data["detail"]


@pytest.mark.asyncio
async def test_search_multiple_sources(client):
    """Test search request with multiple sources"""
    payload = {
        "query": "test query",
        "sources": ["google", "arxiv", "github"],
        "max_results": 3,
    }

    with patch("src.index.WebSearch") as mock_websearch_class:
        mock_websearch_instance = AsyncMock()
        mock_websearch_instance.search = AsyncMock(
            return_value=[
                {
                    "url": "https://google.com",
                    "title": "Google Result",
                    "preview": "Google preview",
                    "source": "google",
                },
                {"url": "https://arxiv.com", "title": "ArXiv Result", "preview": "ArXiv preview", "source": "arxiv"},
                {
                    "url": "https://github.com",
                    "title": "GitHub Result",
                    "preview": "GitHub preview",
                    "source": "github",
                },
            ]
        )
        mock_websearch_class.return_value = mock_websearch_instance

        response = client.post("/search", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["results"], list)
        assert len(data["results"]) == 3


@pytest.mark.asyncio
async def test_search_internal_error(client):
    """Test search request handles internal errors gracefully"""
    payload = {
        "query": "test query",
        "sources": ["google"],
    }

    with patch("src.index.WebSearch") as mock_websearch_class:
        mock_websearch_instance = AsyncMock()
        mock_websearch_instance.search = AsyncMock(side_effect=Exception("Internal error"))
        mock_websearch_class.return_value = mock_websearch_instance

        response = client.post("/search", json=payload)

        assert response.status_code == 500
        assert "Internal error" in response.json()["detail"]


def test_search_invalid_json(client):
    """Test search request with invalid JSON"""
    response = client.post("/search", data="invalid json")

    assert response.status_code == 422  # Unprocessable Entity for invalid JSON


def test_search_missing_query(client):
    """Test search request with missing query field"""
    payload = {
        "sources": ["google"],
        "google_api_key": "test_key",
        "cse_id": "test_cse",
        # Missing query
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 422  # Validation error


def test_search_invalid_source(client):
    """Test search request with invalid source name"""
    payload = {"query": "test query", "sources": ["invalid_source"], "max_results": 2}

    response = client.post("/search", json=payload)

    assert response.status_code == 422  # Validation error for invalid literal

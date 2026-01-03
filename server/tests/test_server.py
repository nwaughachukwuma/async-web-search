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
        "max_preview_chars": 500,
        "google_api_key": "test_key",
        "cse_id": "test_cse",
    }

    # Mock the WebSearch class
    with patch("server.index.WebSearch") as mock_websearch_class:
        mock_websearch_instance = AsyncMock()
        mock_websearch_instance.search = AsyncMock(return_value="Mocked search results")
        mock_websearch_class.return_value = mock_websearch_instance

        response = client.post("/search", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert data["results"] == "Mocked search results"

        # Verify WebSearch was called with correct config
        mock_websearch_class.assert_called_once()
        # Check that search was called
        mock_websearch_instance.search.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_search_missing_google_keys(client):
    """Test search request fails when google keys are missing"""
    payload = {
        "query": "test query",
        "sources": ["google"],
        "max_results": 2,
        # Missing google_api_key and cse_id
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "google_api_key and cse_id are required" in data["detail"]


@pytest.mark.asyncio
async def test_search_missing_newsapi_key(client):
    """Test search request fails when newsapi key is missing"""
    payload = {
        "query": "test query",
        "sources": ["newsapi"],
        "max_results": 2,
        # Missing newsapi_key
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "newsapi_key is required" in data["detail"]


@pytest.mark.asyncio
async def test_search_multiple_sources(client):
    """Test search request with multiple sources"""
    payload = {
        "query": "test query",
        "sources": ["google", "arxiv", "github"],
        "max_results": 3,
        "google_api_key": "test_key",
        "cse_id": "test_cse",
    }

    with patch("server.index.WebSearch") as mock_websearch_class:
        mock_websearch_instance = AsyncMock()
        mock_websearch_instance.search = AsyncMock(return_value="Multi-source results")
        mock_websearch_class.return_value = mock_websearch_instance

        response = client.post("/search", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == "Multi-source results"


@pytest.mark.asyncio
async def test_search_internal_error(client):
    """Test search request handles internal errors gracefully"""
    payload = {
        "query": "test query",
        "sources": ["google"],
        "google_api_key": "test_key",
        "cse_id": "test_cse",
    }

    with patch("server.index.WebSearch") as mock_websearch_class:
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

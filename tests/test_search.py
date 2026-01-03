from unittest.mock import AsyncMock, patch

import pytest

from src.web_search.base import SearchResult
from src.web_search.config import WebSearchConfig
from src.web_search.search import WebSearch


@pytest.mark.asyncio
async def test_websearch_with_multiple_sources():
    """
    Test that WebSearch compiles results from specified sources
    """
    config = WebSearchConfig(sources=["google", "arxiv", "github"])

    # Mock the _compile methods
    with patch.object(WebSearch, "__init__", lambda self, config: None):
        search = WebSearch(config)
        search.config = config
        search.google = AsyncMock()
        search.google._compile = AsyncMock(return_value="Google results")
        search.arxiv = AsyncMock()
        search.arxiv._compile = AsyncMock(return_value="ArXiv results")
        search.wikipedia = AsyncMock()
        search.wikipedia._compile = AsyncMock(return_value="Wikipedia results")
        search.github = AsyncMock()
        search.github._compile = AsyncMock(return_value="GitHub results")
        search.newsapi = AsyncMock()
        search.newsapi._compile = AsyncMock(return_value="NewsAPI results")
        search.pubmed = AsyncMock()
        search.pubmed._compile = AsyncMock(return_value="Pubmed results")

        result = await search.compile_search("test query")

        # Check that only specified sources were called
        search.google._compile.assert_called_once_with("test query")
        search.arxiv._compile.assert_called_once_with("test query")
        search.github._compile.assert_called_once_with("test query")

        search.wikipedia._compile.assert_not_called()
        search.newsapi._compile.assert_not_called()
        search.pubmed._compile.assert_not_called()

        # Check the combined result
        expected = "Google results\n\nArXiv results\n\nGitHub results"
        assert result == expected


@pytest.mark.asyncio
async def test_websearch_with_all_sources():
    """
    Test WebSearch with all available sources
    """
    config = WebSearchConfig(sources=["google", "wikipedia", "arxiv", "newsapi", "github", "pubmed"])

    with patch.object(WebSearch, "__init__", lambda self, config: None):
        search = WebSearch(config)
        search.config = config
        search.google = AsyncMock()
        search.google._compile = AsyncMock(return_value="Google")
        search.wikipedia = AsyncMock()
        search.wikipedia._compile = AsyncMock(return_value="Wikipedia")
        search.arxiv = AsyncMock()
        search.arxiv._compile = AsyncMock(return_value="ArXiv")
        search.newsapi = AsyncMock()
        search.newsapi._compile = AsyncMock(return_value="NewsAPI")
        search.github = AsyncMock()
        search.github._compile = AsyncMock(return_value="GitHub")
        search.pubmed = AsyncMock()
        search.pubmed._compile = AsyncMock(return_value="PubMed")

        result = await search.compile_search("test query")

        # All sources should be called
        search.google._compile.assert_called_once_with("test query")
        search.wikipedia._compile.assert_called_once_with("test query")
        search.arxiv._compile.assert_called_once_with("test query")
        search.newsapi._compile.assert_called_once_with("test query")
        search.github._compile.assert_called_once_with("test query")
        search.pubmed._compile.assert_called_once_with("test query")

        expected = "Google\n\nWikipedia\n\nArXiv\n\nNewsAPI\n\nGitHub\n\nPubMed"
        assert result == expected


@pytest.mark.asyncio
async def test_websearch_handles_exceptions():
    """
    Test that WebSearch handles exceptions from sources gracefully
    """
    config = WebSearchConfig(sources=["google", "arxiv"])

    with patch.object(WebSearch, "__init__", lambda self, config: None):
        search = WebSearch(config)
        search.config = config
        search.google = AsyncMock()
        search.google._compile = AsyncMock(return_value="Google results")
        search.arxiv = AsyncMock()
        search.arxiv._compile = AsyncMock(side_effect=Exception("API Error"))
        search.wikipedia = AsyncMock()
        search.github = AsyncMock()
        search.newsapi = AsyncMock()
        search.pubmed = AsyncMock()

        result = await search.compile_search("test query")

        # Should only include successful results
        assert result == "Google results"


@pytest.mark.asyncio
async def test_websearch_search_returns_json():
    """
    Test that WebSearch.search returns JSON-serializable list of dicts
    """
    config = WebSearchConfig(sources=["google", "arxiv"])

    # Mock the _handle methods
    with patch.object(WebSearch, "__init__", lambda self, config: None):
        search = WebSearch(config)
        search.config = config
        search.google = AsyncMock()
        search.google._handle = AsyncMock(
            return_value=[
                SearchResult(url="https://google.com/1", title="Google Result 1", preview="Preview 1", source="google")
            ]
        )
        search.arxiv = AsyncMock()
        search.arxiv._handle = AsyncMock(
            return_value=[
                SearchResult(url="https://arxiv.com/1", title="ArXiv Result 1", preview="Preview 2", source="arxiv")
            ]
        )
        search.wikipedia = AsyncMock()
        search.wikipedia._handle = AsyncMock(return_value=[])
        search.github = AsyncMock()
        search.github._handle = AsyncMock(return_value=[])
        search.newsapi = AsyncMock()
        search.newsapi._handle = AsyncMock(return_value=[])
        search.pubmed = AsyncMock()
        search.pubmed._handle = AsyncMock(return_value=[])

        result = await search.search("test query")

        # Check that only specified sources were called
        search.google._handle.assert_called_once_with("test query")
        search.arxiv._handle.assert_called_once_with("test query")
        search.wikipedia._handle.assert_not_called()
        search.github._handle.assert_not_called()
        search.newsapi._handle.assert_not_called()
        search.pubmed._handle.assert_not_called()

        # Check the result is a list of dicts
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {
            "url": "https://google.com/1",
            "title": "Google Result 1",
            "preview": "Preview 1",
            "source": "google",
        }
        assert result[1] == {
            "url": "https://arxiv.com/1",
            "title": "ArXiv Result 1",
            "preview": "Preview 2",
            "source": "arxiv",
        }


@pytest.mark.asyncio
async def test_websearch_search_handles_exceptions():
    """
    Test that WebSearch.search handles exceptions from sources gracefully
    """
    config = WebSearchConfig(sources=["google", "arxiv"])

    with patch.object(WebSearch, "__init__", lambda self, config: None):
        search = WebSearch(config)
        search.config = config
        search.google = AsyncMock()
        search.google._handle = AsyncMock(
            return_value=[
                SearchResult(url="https://google.com/1", title="Google Result", preview="Preview", source="google")
            ]
        )
        search.arxiv = AsyncMock()
        search.arxiv._handle = AsyncMock(side_effect=Exception("API Error"))
        search.wikipedia = AsyncMock()
        search.github = AsyncMock()
        search.newsapi = AsyncMock()
        search.pubmed = AsyncMock()

        result = await search.search("test query")

        # Should only include successful results
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["title"] == "Google Result"

from unittest.mock import AsyncMock, patch

import pytest

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

        result = await search.search("test query")

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

        result = await search.search("test query")

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

        result = await search.search("test query")

        # Should only include successful results
        assert result == "Google results"

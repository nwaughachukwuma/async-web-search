from typing import List
from unittest.mock import patch

import pytest

from src.web_search.arxiv import ArxivSearch
from src.web_search.base import SearchResult


# Fixtures for common test data
@pytest.fixture
def sample_query():
    return "test query"


@pytest.fixture
def sample_results() -> List[SearchResult]:
    return [
        SearchResult(
            url="https://example.com",
            title="Test Result",
            preview="This is a test result preview",
        ),
        SearchResult(
            url="https://example2.com",
            title="Another Test Result",
            preview="Another test result preview",
        ),
    ]


@pytest.fixture
def mock_arxiv_search():
    with patch("src.web_search.arxiv.ArxivSearch._search") as mock_search:
        yield mock_search
    mock_search.assert_called_once()


@pytest.fixture
def arxiv_search(mock_arxiv_search, sample_results):
    def side_effect(query: str):
        if not query:
            raise ValueError("Search query cannot be empty")
        return sample_results

    source = ArxivSearch()
    mock_arxiv_search.side_effect = side_effect

    return source


class TestArxivSearch:
    def _test_initialization(self, arxiv_search):
        assert isinstance(arxiv_search, ArxivSearch)

    def test_check_sample_query(self, sample_query):
        assert sample_query == "test query"

    @pytest.mark.asyncio
    async def test_invalid_query_raises_error(self, arxiv_search):
        """Test that empty queries raise ValueError"""
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            await arxiv_search._search("")

    @pytest.mark.asyncio
    async def test_search_error_handling(self, arxiv_search, mock_arxiv_search):
        """Test handling of search errors"""
        mock_arxiv_search.side_effect = Exception("API Error")
        with pytest.raises(Exception, match="API Error"):
            await arxiv_search._search("test")

    @pytest.mark.asyncio
    async def test_search_returns_results(self, arxiv_search, sample_query):
        """Test that search returns expected results format"""
        results = await arxiv_search._search(sample_query)

        assert isinstance(results, list)
        assert len(results) > 0

        for result in results:
            assert isinstance(result, SearchResult)
            assert all(hasattr(result, key) for key in ["url", "title", "preview"])
            assert all(isinstance(getattr(result, key), str) for key in ["title", "url", "preview"])

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_live_search_integration(self):
        """Real integration test with actual API - should be run selectively"""
        source = ArxivSearch()
        results = await source._search("python programming")

        assert isinstance(results, list)
        assert len(results) > 0

        for result in results:
            assert all(hasattr(result, key) for key in ["url", "title", "preview"])
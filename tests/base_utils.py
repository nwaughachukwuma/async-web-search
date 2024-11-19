###
# Base test class for all search implementations
###
from typing import Any

import pytest

from src.web_search.base import SearchResult


class BaseSearchTests:
    """Base test class that all search test classes should inherit from"""

    search_class: Any  # Should be set by child classes

    def test_initialization(self, search_instance):
        assert self.search_class is not None
        assert isinstance(search_instance, self.search_class)

    def test_check_sample_query(self, sample_query):
        assert sample_query == "test query"

    @pytest.mark.asyncio
    async def test_mock_search_handler_called(self, search_instance, sample_query, mock_search_handler):
        await search_instance._search(sample_query)

        mock_search_handler.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalid_query_raises_error(self, search_instance):
        """Test that empty queries raise ValueError"""
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            await search_instance._search("")

    @pytest.mark.asyncio
    async def test_search_error_handling(self, search_instance, mock_search_handler):
        """Test handling of search errors"""
        mock_search_handler.side_effect = Exception("API Error")
        with pytest.raises(Exception, match="API Error"):
            await search_instance._search("test")

    @pytest.mark.asyncio
    async def test_search_returns_results(self, search_instance, sample_query):
        """Test that search returns expected results format"""
        results = await search_instance._search(sample_query)

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
        source = self.search_class()
        results = await source._search("python programming")

        assert isinstance(results, list)
        assert len(results) > 0

        for result in results:
            assert all(hasattr(result, key) for key in ["url", "title", "preview"])

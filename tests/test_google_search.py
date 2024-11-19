# check conftest.py for defined reuable fixtures

from unittest.mock import patch

import pytest

from src.web_search.google import GoogleSearch

from .base_utils import BaseSearchTests


@pytest.fixture()
def mock_search_handler():
    with patch("src.web_search.google.GoogleSearch._search") as mock_search:
        yield mock_search


@pytest.fixture
def search_instance(mock_search_handler, sample_results):
    def side_effect(query: str):
        if not query:
            raise ValueError("Search query cannot be empty")
        return sample_results

    source = GoogleSearch()
    mock_search_handler.side_effect = side_effect
    yield source


class TestGoogleSearch(BaseSearchTests):
    search_class = GoogleSearch

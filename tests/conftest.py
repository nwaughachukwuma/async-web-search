from typing import List

import pytest

from src.web_search.base import SearchResult


@pytest.fixture(scope="module")
def sample_query() -> str:
    return "test query"


@pytest.fixture(scope="module")
def sample_results() -> List[SearchResult]:
    return [
        SearchResult(
            url="https://example.com",
            title="Test Result",
            preview="This is a test result preview",
            source="google",
        ),
        SearchResult(
            url="https://example2.com",
            title="Another Test Result",
            preview="Another test result preview",
            source="arxiv",
        ),
    ]

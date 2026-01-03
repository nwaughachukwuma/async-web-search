import pytest

from src.web_search.pubmed import PubMedSearch


@pytest.mark.asyncio
async def test_pubmed_search():
    results = await PubMedSearch()._search(query="cancer immunotherapy")
    assert len(results) > 0
    for result in results:
        print(result)
        assert result.preview is not None

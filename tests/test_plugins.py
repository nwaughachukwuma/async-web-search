from unittest.mock import AsyncMock

import pytest

from src.web_search.base import PluginSearch, SearchResult
from src.web_search.config import WebSearchConfig
from src.web_search.search import WebSearch


class DummyPlugin(PluginSearch):
    slug = "dummy"

    async def _search(self, _query: str):
        return [
            SearchResult(
                url="https://dummy.com/1",
                title="Dummy Result 1",
                preview="Preview text",
                source="plugin",
            )
        ]

    async def _compile(self, _query: str):
        return "Dummy compiled results"


class ErrorPlugin(PluginSearch):
    slug = "error"

    async def _search(self, _query: str):
        raise RuntimeError("Boom")

    async def _compile(self, _query: str):
        raise RuntimeError("Boom")


class NoSearchPlugin(PluginSearch):
    slug = "dummy"

    async def _compile(self, _query: str):
        return ""


class NonPlugin:  # Does not subclass PluginSearch
    ...


@pytest.mark.asyncio
async def test_plugin_search_success():
    """Ensure plugin results are included in search output."""
    cfg = WebSearchConfig(sources=["plugin"], plugins=[DummyPlugin()])
    ws = WebSearch(cfg)

    # Patch out built-in sources so we don't hit network
    ws.google._search = AsyncMock(return_value=[])
    ws.arxiv._search = AsyncMock(return_value=[])
    ws.wikipedia._search = AsyncMock(return_value=[])
    ws.newsapi._search = AsyncMock(return_value=[])
    ws.github._search = AsyncMock(return_value=[])
    ws.pubmed._search = AsyncMock(return_value=[])

    results = await ws.search("quantum")
    assert len(results) == 1
    assert results[0]["source"] == "plugin"


@pytest.mark.asyncio
async def test_plugin_compile_success():
    """Compiled plugin results should appear in output string."""
    cfg = WebSearchConfig(sources=["plugin"], plugins=[DummyPlugin()])
    ws = WebSearch(cfg)
    # Patch built-ins
    ws.google._compile = AsyncMock(return_value="")
    ws.arxiv._compile = AsyncMock(return_value="")
    ws.wikipedia._compile = AsyncMock(return_value="")
    ws.newsapi._compile = AsyncMock(return_value="")
    ws.github._compile = AsyncMock(return_value="")
    ws.pubmed._compile = AsyncMock(return_value="")

    text = await ws.compile_search("quantum")
    assert "Dummy compiled results" in text


@pytest.mark.asyncio
async def test_plugin_error_is_handled():
    """Exceptions in plugin should not crash overall search."""
    cfg = WebSearchConfig(sources=["plugin"], plugins=[DummyPlugin(), ErrorPlugin()])
    ws = WebSearch(cfg)

    # Stub built-ins
    ws.google._search = AsyncMock(return_value=[])
    ws.arxiv._search = AsyncMock(return_value=[])
    ws.wikipedia._search = AsyncMock(return_value=[])
    ws.newsapi._search = AsyncMock(return_value=[])
    ws.github._search = AsyncMock(return_value=[])
    ws.pubmed._search = AsyncMock(return_value=[])

    results = await ws.search("quantum")
    # Should still contain dummy plugin results, error plugin ignored
    assert any(r["source"] == "plugin" for r in results)


@pytest.mark.asyncio
async def test_non_plugin_ignored():
    """Non PluginSearch objects/abstractions are skipped."""
    cfg = WebSearchConfig(plugins=[NonPlugin()])  # type: ignore
    ws = WebSearch(cfg)
    assert ws.plugins == []


@pytest.mark.asyncio
async def test_add_plugin_method():
    """Plugins can be added after WebSearch instantiation."""
    cfg = WebSearchConfig()
    ws = WebSearch(cfg)
    assert ws.plugins == []

    ws.add_plugin([DummyPlugin()])
    assert len(ws.plugins) == 1


@pytest.mark.asyncio
async def test_plugin_missing_search_method():
    """Plugin without `_search` method should raise an error"""
    with pytest.raises(TypeError):
        NoSearchPlugin()  # type: ignore

import pytest
from src.utils.tracing import init_langsmith, is_tracing_enabled
from src.utils.ticker_resolver import TickerResolver
from unittest.mock import MagicMock

def test_tracing(mocker):
    mocker.patch("src.utils.tracing.os.getenv", return_value="true")
    mocker.patch("langsmith.traceable", return_value=lambda x: x, create=True)
    init_langsmith(project="test_proj")
    is_tracing_enabled()

def test_ticker_resolver(mocker):
    mock_tavily = mocker.patch("src.utils.ticker_resolver.TavilyClient").return_value
    mock_tavily.search.return_value = {
        "results": [{"content": "RELIANCE.NS", "title": "Reliance Symbol"}]
    }
    resolver = TickerResolver(api_key="dummy")
    ticker = resolver.resolve("Reliance")
    assert ticker == "RELIANCE.NS"



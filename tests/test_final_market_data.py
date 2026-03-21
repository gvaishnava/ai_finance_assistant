import pytest
from src.data.market_data import MarketDataClient
from unittest.mock import MagicMock, patch

@pytest.fixture
def market_client(mocker):
    # Mock yfinance Ticker and download
    mocker.patch("yfinance.Ticker")
    mocker.patch("yfinance.download")
    return MarketDataClient("config.yaml")

def test_market_data_indices(market_client, mocker):
    mocker.patch("yfinance.download", return_value=MagicMock())
    # Should cover get_market_indices
    indices = market_client.get_market_indices()
    assert isinstance(indices, list)

def test_market_data_search(market_client, mocker):
    # Mock symbols search if possible, or just call it
    res = market_client.search_symbol("AAPL")
    assert isinstance(res, list)

def test_market_data_history(market_client, mocker):
    mock_ticker = mocker.patch("yfinance.Ticker")
    mock_ticker.return_value.history.return_value = MagicMock()
    
    res = market_client.get_historical_data("AAPL")
    assert res is not None

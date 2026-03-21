import pytest
from src.data.market_data import MarketDataClient
import pandas as pd
from unittest.mock import MagicMock

def test_market_data_client(mocker):
    # Mock yfinance
    mock_ticker = mocker.patch("src.data.market_data.yf.Ticker").return_value
    mock_ticker.info = {"regularMarketPrice": 150.0, "longName": "Apple Inc.", "currency": "USD"}
    
    client = MarketDataClient("config.yaml")
    
    quote = client.get_quote("AAPL")
    assert quote['price'] == 150.0
    assert quote['name'] == "Apple Inc."
    
    # mock history
    df = pd.DataFrame({"Close": [150.0, 155.0]}, index=pd.to_datetime(["2023-01-01", "2023-01-02"]))
    mock_ticker.history.return_value = df
    
    hist = client.get_historical_data("AAPL", period="1mo")
    assert len(hist) == 2
    
    # test market indices
    indices = client.get_market_indices()
    assert len(indices) > 0


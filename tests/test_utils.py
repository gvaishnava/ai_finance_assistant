import pytest
from src.utils.formatters import format_currency, format_percentage, format_number, format_market_cap
from src.utils.validators import validate_stock_symbol, sanitize_input, validate_portfolio_data
from src.utils.visualizers import get_portfolio_allocation_chart, get_sector_allocation_chart, get_market_history_chart

def test_formatters():
    assert format_currency(100.5) == "₹100.50"
    assert format_percentage(0.155) == "+15.50%"
    assert format_number(1500) == "1,500.00"
    assert format_market_cap(100000) == "₹1.00 L"

def test_validators():
    assert validate_stock_symbol("AAPL")
    assert not validate_stock_symbol("123!")
    assert sanitize_input("<script>") == "<script>" # since sanitize_input just strips unprintables
    
    port = {"holdings": [{"symbol": "AAPL", "quantity": 10}]}
    val, err = validate_portfolio_data(port)
    assert val is True

def test_visualizers():
    import pandas as pd
    allocations = [{"symbol": "AAPL", "allocation_percentage": 50, "value": 100}]
    chart = get_portfolio_allocation_chart(allocations)
    assert chart["type"] == "pie"
    
    sectors = {"Tech": 100.0}
    chart = get_sector_allocation_chart(sectors)
    assert chart["type"] == "bar"
    
    df = pd.DataFrame({"Close": [100.0, 110.0]}, index=pd.to_datetime(["2023-01-01", "2023-01-02"]))
    chart = get_market_history_chart(df, "AAPL")
    assert chart["title"] == "AAPL Price History"

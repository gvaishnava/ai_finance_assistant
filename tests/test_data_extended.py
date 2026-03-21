import pytest
from src.data.portfolio import Portfolio, Holding
from unittest.mock import MagicMock

def test_portfolio_extended(mocker):
    mock_mc = mocker.patch("src.data.portfolio.get_market_client").return_value
    mock_mc.get_quote.return_value = None
    p = Portfolio()
    h = Holding(symbol="AAPL", quantity=10, average_price=150.0)
    p.add_holding(h)
    assert p.get_current_value() == 0 # no prices yet
    
    mock_mc.get_quote.return_value = {"price": 160.0}
    assert p.get_current_value() == 1600.0
    pl = p.get_profit_loss()
    assert pl["absolute"] == 100.0


def test_user_profile(mocker):
    from src.data.user_profile import UserProfile, RiskTolerance
    data = {
        "user_id": "test_user",
        "risk_tolerance": "moderate",
        "investment_goals": [],
        "knowledge_level": "beginner",
        "preferences": {}
    }
    profile = UserProfile.from_dict(data)
    assert profile.user_id == "test_user"
    assert profile.risk_tolerance == RiskTolerance.MODERATE
    
    d = profile.to_dict()
    assert d["user_id"] == "test_user"


import pytest
from fastapi.testclient import TestClient
from src.web_app.api import app
from unittest.mock import MagicMock, patch

client = TestClient(app)

def test_market_routes(mocker):
    # Mock Market Data Client
    mock_mc = mocker.patch("src.web_app.routes.market.market_client")
    mock_mc.get_market_indices.return_value = [{
        "symbol": "^NSEI", "name": "NIFTY 50", "price": 22000, "change_percent": 0.5, "change": 100
    }]
    
    response = client.get("/api/market/trends")
    assert response.status_code == 200
    assert response.json()["indices"][0]["symbol"] == "^NSEI"

def test_user_routes(mocker):
    # Mock Session Manager instance
    mock_sm = mocker.patch("src.web_app.routes.user.session_manager")
    mock_session = MagicMock()
    mock_session.user_profile = {"user_id": "test"}
    mock_session.portfolio = {"holdings": []}
    mock_session.goals = []
    import datetime
    mock_session.last_accessed = datetime.datetime.now()
    
    mock_sm.get_session.return_value = mock_session
    
    # Test profile
    response = client.get("/api/user/profile/test_sess")
    assert response.status_code == 200
    assert response.json()["profile"]["user_id"] == "test"
    
    # Test full session
    response = client.get("/api/user/session/test_sess")
    assert response.status_code == 200
    assert response.json()["session_id"] == "test_sess"



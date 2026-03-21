import pytest
from src.agents.market_agent import MarketAgent, format_number
from src.core.session import SessionManager
from unittest.mock import MagicMock, AsyncMock
import pandas as pd

def test_format_number():
    assert format_number(10000000) == "1.00 Cr"
    assert format_number(100000) == "1.00 L"
    assert format_number(5000) == "5,000"

def test_market_analyze_stocks_sync(mocker):
    m = MarketAgent("config.yaml")
    m.llm_client = MagicMock()
    m.llm_client.generate_with_context.return_value = "Analysis"
    m.market_client = MagicMock()
    m.market_client.get_quote.return_value = {
        "symbol": "TCS", "name": "TCS", "price": 4000, "sector": "IT", "volume": 1000000
    }
    
    res = m._analyze_stocks("query", ["TCS"])
    assert "TCS" in res["response"]
    assert "10.00 L" in res["response"] # Volume formatted


@pytest.mark.asyncio
async def test_session_manager_basics(mocker):
    sm = SessionManager()
    sess = sm.create_session("s1")
    assert sess.session_id == "s1"
    
    # Conversation history filtering
    sess.add_message("user", "Hello", source="chat")
    sess.add_message("assistant", "Hi", agent="finance_qa", source="chat")
    sess.add_message("user", "My tax?", source="tax")
    sess.add_message("assistant", "Tax info", agent="tax", source="tax")
    
    assert len(sess.get_conversation_history(source_filter="tax")) == 2
    assert len(sess.get_conversation_history(source_filter="chat")) == 2
    
    sm.save_session(sess)
    loaded = sm.get_session("s1")
    assert loaded.session_id == "s1"
    
    # Expiry
    mocker.patch("src.core.session.datetime")
    import datetime as dt
    from src.core.session import datetime
    datetime.now.return_value = dt.datetime.now() + dt.timedelta(days=2)
    assert sm._is_expired(sess) == True
    
    sm.delete_session("s1")
    assert sm.get_session("s1") is None



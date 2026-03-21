import pytest
from src.agents.goal_planning_agent import GoalPlanningAgent
from src.agents.market_agent import MarketAgent
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def goal_agent(mocker):
    mocker.patch("src.agents.base_agent.get_llm_client")
    mocker.patch("src.agents.base_agent.Retriever")
    return GoalPlanningAgent("config.yaml")

@pytest.fixture
def market_agent(mocker):
    mocker.patch("src.agents.base_agent.get_llm_client")
    mocker.patch("src.agents.base_agent.Retriever")
    mocker.patch("src.agents.market_agent.get_market_client")
    return MarketAgent("config.yaml")

@pytest.mark.asyncio
async def test_goal_agent_specific(goal_agent):
    goal_agent.llm_client = AsyncMock()
    goal_agent.llm_client.agenerate_with_context.return_value = "Advice"
    
    # Test date parsing and zero balance
    goal = {
        "name": "Save for House", 
        "target_amount": 10000, 
        "current_amount": 0.0,
        "target_date": "2030-01-01"
    }
    context = {"user_profile": {"investment_goals": [goal]}}
    
    result = await goal_agent.async_process(query="Tell me about Save for House", context=context)
    assert "Advice" in result["response"]
    assert "0.0%" in result["response"]
    # assert "Note:" in result["response"] # This is in prompt


@pytest.mark.asyncio
async def test_goal_agent_review(goal_agent):
    goal_agent.llm_client = AsyncMock()
    goal_agent.llm_client.agenerate_with_context.return_value = "Review"
    
    goals = [{"name": "G1", "target_amount": 100, "current_amount": 50}]
    context = {"goals": goals}
    
    result = await goal_agent.async_process(query="Review my goals", context=context)
    assert "Review" in result["response"]
    assert "G1" in result["response"]

@pytest.mark.asyncio
async def test_market_agent_stocks(market_agent):
    market_agent.llm_client = AsyncMock()
    market_agent.llm_client.agenerate_with_context.return_value = "Stock Analysis"
    market_agent.market_client.get_quote.return_value = {
        "symbol": "AAPL", "name": "Apple", "price": 150, "change_percent": 1.0, "sector": "Tech"
    }
    market_agent.market_client.get_historical_data.return_value = MagicMock(empty=True)
    
    result = await market_agent.async_process(query="Analyze AAPL", symbols=["AAPL"])
    assert "Stock Analysis" in result["response"]
    assert "Apple" in result["response"]

def test_market_agent_sync(market_agent):
    market_agent.llm_client = MagicMock()
    market_agent.llm_client.generate_with_context.return_value = "Sync Analysis"
    market_agent.market_client.get_quote.return_value = {
        "symbol": "AAPL", "name": "Apple", "price": 150, "change_percent": 1.0, "sector": "Tech"
    }
    
    result = market_agent.process(query="Analyze Apple", symbols=["AAPL"])
    assert "Sync Analysis" in result["response"]




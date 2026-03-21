import pytest
from src.agents.goal_planning_agent import GoalPlanningAgent
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def goal_agent(mocker):
    mocker.patch("src.agents.base_agent.get_llm_client")
    mocker.patch("src.agents.base_agent.Retriever")
    return GoalPlanningAgent("config.yaml")

def test_goal_fuzzy_match(goal_agent):
    goal_agent.llm_client = MagicMock()
    goal_agent.llm_client.generate_with_context.return_value = "Advice"
    
    goal = {"name": "Retirement", "target_amount": 10000, "current_amount": 1000}
    context = {"user_profile": {"investment_goals": [goal]}}
    
    # Fuzzy match in query
    result = goal_agent.process(query="What about my Retirement?", context=context)
    assert "Advice" in result["response"]
    assert "Retirement" in result["response"]

def test_goal_date_formats(goal_agent):
    goal_agent.llm_client = MagicMock()
    goal_agent.llm_client.generate_with_context.return_value = "Advice"
    
    # ISO format with T
    goal = {"name": "G", "target_amount": 100, "current_amount": 0, "target_date": "2030-01-01T00:00:00"}
    goal_agent._analyze_specific_goal("query", goal, {})
    
    # Slash format
    goal["target_date"] = "2030/01/01"
    goal_agent._analyze_specific_goal("query", goal, {})

def test_goal_review_sync(goal_agent):
    goal_agent.llm_client = MagicMock()
    goal_agent.llm_client.generate_with_context.return_value = "Review"
    
    result = goal_agent._review_existing_goals("query", [{"name": "G1", "target_amount": 100}], {})
    assert "Review" in result["response"]

@pytest.mark.asyncio
async def test_goal_async_fuzzy(goal_agent):
    goal_agent.llm_client = AsyncMock()
    goal_agent.llm_client.agenerate_with_context.return_value = "Advice"
    
    goal = {"name": "Retirement", "target_amount": 10000, "current_amount": 1000}
    context = {"user_profile": {"investment_goals": [goal]}}
    
    # Fuzzy match
    result = await goal_agent.async_process("How is retirement?", context)
    assert "Advice" in result["response"]

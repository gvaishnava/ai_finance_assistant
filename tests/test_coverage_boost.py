import pytest
from unittest.mock import MagicMock
from src.agents.finance_qa_agent import FinanceQAAgent
from src.agents.goal_planning_agent import GoalPlanningAgent
from src.agents.market_agent import MarketAgent
from src.agents.news_agent import NewsSynthesizerAgent
from src.agents.portfolio_agent import PortfolioAgent
from src.agents.tax_agent import TaxEducationAgent
from src.agents.ticker_resolver_agent import TickerResolverAgent
from src.workflow.graph import create_workflow_graph

# Reusing fixtures locally since they apply well here
@pytest.fixture
def mock_llm_client(mocker):
    mock = MagicMock()
    mock.generate.return_value = "Mocked response"
    mock.generate_with_context.return_value = "Mocked context response"
    
    async def mock_agenerate(*args, **kwargs):
        return "Mocked async response"
    async def mock_agenerate_context(*args, **kwargs):
        return "Mocked async context response"
        
    mock.agenerate = mock_agenerate
    mock.agenerate_with_context = mock_agenerate_context
    
    mocker.patch("src.agents.base_agent.get_llm_client", return_value=mock)
    mocker.patch("src.core.llm.get_llm_client", return_value=mock)
    
    return mock

@pytest.fixture
def mock_retriever(mocker):
    mock = MagicMock()
    mock.get_context.return_value = ["Context 1", "Context 2"]
    mocker.patch("src.agents.base_agent.Retriever", return_value=mock)
    return mock

@pytest.mark.asyncio
async def test_async_agents(mock_llm_client, mock_retriever, mocker):
    qa = FinanceQAAgent(config_path="config.yaml")
    res = await qa.async_process("What is inflation?")
    assert "response" in res
    
    goal = GoalPlanningAgent(config_path="config.yaml")
    res = await goal.async_process("I want a car")
    assert "response" in res

    market = MarketAgent(config_path="config.yaml")
    mocker.patch("src.agents.market_agent.get_market_client", autospec=True)
    res = await market.async_process("How is AAPL?")
    assert "response" in res

    news = NewsSynthesizerAgent(config_path="config.yaml")
    res = await news.async_process("AAPL news")
    assert "response" in res

    port = PortfolioAgent(config_path="config.yaml")
    mock_port = mocker.MagicMock()
    mock_port.get_allocation.return_value = [{"name": "AAPL", "allocation_percentage": 100, "value": 1000}]
    mock_port.get_sector_allocation.return_value = {"Tech": 100}
    mock_port.get_profit_loss.return_value = {"current_value": 1000, "invested_value": 800, "absolute": 200, "percentage": 25}
    res = await port.async_process("Analyze portfolio", context={"portfolio": mock_port})
    assert "response" in res

    tax = TaxEducationAgent(config_path="config.yaml")
    res = await tax.async_process("Tax rules for stocks")
    assert "response" in res

def test_workflow_graph_creation(mocker):
    # Mock langgraph components to prevent actual imports/calls if needed
    graph = create_workflow_graph(config_path="config.yaml")
    assert graph is not None

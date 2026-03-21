import pytest
from unittest.mock import MagicMock
from src.agents.finance_qa_agent import FinanceQAAgent
from src.agents.goal_planning_agent import GoalPlanningAgent
from src.agents.market_agent import MarketAgent
from src.agents.news_agent import NewsSynthesizerAgent
from src.agents.portfolio_agent import PortfolioAgent
from src.agents.tax_agent import TaxEducationAgent
from src.agents.ticker_resolver_agent import TickerResolverAgent

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

def test_finance_qa_agent(mock_llm_client, mock_retriever):
    agent = FinanceQAAgent(config_path="config.yaml")
    res = agent.process("What is inflation?")
    assert "response" in res

def test_goal_planning_agent(mock_llm_client, mock_retriever):
    agent = GoalPlanningAgent(config_path="config.yaml")
    res = agent.process("I want to buy a house")
    assert "response" in res

def test_market_agent(mock_llm_client, mock_retriever, mocker):
    mock_market_client = mocker.MagicMock()
    mock_market_client.get_market_indices.return_value = [{"symbol": "^GSPC", "price": 5000}]
    mocker.patch("src.agents.market_agent.get_market_client", return_value=mock_market_client)
    agent = MarketAgent(config_path="config.yaml")
    res = agent.process("How is the market doing?")
    assert "response" in res

def test_news_agent(mock_llm_client, mock_retriever, mocker):
    mocker.patch("src.agents.news_agent.TavilyClient", autospec=True)
    agent = NewsSynthesizerAgent(config_path="config.yaml")
    
    # Needs to mock the search_news method as TavilyClient fails without real keys
    mocker.patch.object(agent, "search_news", return_value=[{"title": "News 1", "url": "abc", "content": "xyz"}])
    res = agent.process("AAPL news")
    assert "response" in res

def test_portfolio_agent(mock_llm_client, mock_retriever, mocker):
    agent = PortfolioAgent(config_path="config.yaml")
    mock_portfolio = mocker.MagicMock()
    mock_portfolio.get_allocation.return_value = [{"name": "AAPL", "allocation_percentage": 100, "value": 1000}]
    mock_portfolio.get_sector_allocation.return_value = {"Tech": 100}
    mock_portfolio.get_profit_loss.return_value = {"current_value": 1000, "invested_value": 800, "absolute": 200, "percentage": 25}
    
    res = agent.process("Analyze portfolio", context={"portfolio": mock_portfolio})
    assert "response" in res

def test_tax_agent(mock_llm_client, mock_retriever):
    agent = TaxEducationAgent(config_path="config.yaml")
    res = agent.process("Tax rules for stocks")
    assert "response" in res

def test_ticker_resolver_agent(mock_llm_client):
    agent = TickerResolverAgent(config_path="config.yaml")
    mock_llm_client.generate.return_value = '{"symbols": ["AAPL"]}'
    res = agent.process("Apple")
    assert "symbols" in res.get("metadata", {})

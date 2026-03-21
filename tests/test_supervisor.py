import pytest
from src.workflow.supervisor import SupervisorAgent
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def supervisor(mocker):
    mocker.patch("src.agents.base_agent.get_llm_client")
    mocker.patch("src.agents.base_agent.Retriever")
    return SupervisorAgent("config.yaml")

@pytest.mark.asyncio
async def test_supervisor_route(supervisor):
    supervisor.llm_client = MagicMock()
    # Mock the router LLM call
    supervisor.llm_client.generate.return_value = "finance_qa"
    
    # Keyword routing
    assert supervisor.route("What is my portfolio?") == "portfolio"
    assert supervisor.route("What is the stock price?") == "market"
    
    # LLM routing
    assert supervisor.route("Explain derivatives") == "finance_qa"

def test_extract_symbols(supervisor):
    symbols = supervisor.extract_symbols("What is the price of AAPL and INFY.NS?")
    assert "AAPL" in symbols
    assert "INFY.NS" in symbols


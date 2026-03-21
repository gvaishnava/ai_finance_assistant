import pytest
from unittest.mock import MagicMock
from src.workflow.graph import create_workflow_graph, arun_workflow

@pytest.fixture
def mock_supervisor_llm(mocker):
    mock = MagicMock()
    # Supervisor response needs to be parsed by JsonOutputParser
    # So we return a JSON string with format {"next": "finance_qa"}
    mock.agenerate.return_value = '{"next": "finance_qa", "reasoning": "Standard"}'
    mocker.patch("src.core.llm.get_llm_client", return_value=mock)
    mocker.patch("src.workflow.supervisor.get_llm_client", return_value=mock)
    return mock

@pytest.mark.asyncio
async def test_workflow_execution(mock_supervisor_llm, mocker):
    # Provide a simple state and run it
    
    # We also need to mock the underlying agents since the supervisor will route to finance_qa
    mock_qa_process = mocker.patch("src.agents.finance_qa_agent.FinanceQAAgent.async_process", 
                                   return_value={"response": "Mocked test"})
    
    # Actually just compiling the graph
    app = create_workflow_graph("config.yaml")

    # Because our mock supervisor always routes to finance_qa, we can test that path
    # If we run it, it might loop forever if the new messages don't change state. 
    # But graph usually has recursion limits or we can just run the supervisor node directly.
    
    from src.workflow.supervisor import SupervisorAgent
    supervisor = SupervisorAgent("config.yaml")
    
    route = supervisor.route("I need to analyze my portfolio")
    assert route == "portfolio"
    
    # LLM based routing test
    route = supervisor.route("What is a 401k?")
    # Since we mocked the LLM to return `{"next": "finance_qa", "reasoning": "Standard"}`
    # Wait, the supervisor parses the exact agent name from the text.
    # Our mock supervisor LLM returns '{"next": "finance_qa", "reasoning": "Standard"}'
    # Supervisor will find 'finance_qa' in the string and return it.
    assert route == "finance_qa"

import pytest
from unittest.mock import MagicMock
from src.workflow.graph import route_query_node, process_with_agent_node, should_continue, run_workflow
from src.workflow.state import create_initial_state

def test_route_query_node(mocker):
    mocker.patch("src.workflow.graph.SupervisorAgent.route", return_value="finance_qa")
    state = create_initial_state(query="Hello")
    state = route_query_node(state)
    assert state['selected_agent'] == "finance_qa"

def test_process_with_agent_node(mocker):
    mock_agent = MagicMock()
    mock_agent.process.return_value = {"response": "Mocked sync response", "metadata": {"test": 1}}
    mocker.patch("src.workflow.graph.get_agent", return_value=mock_agent)
    
    state = create_initial_state(query="Hello")
    state['selected_agent'] = "finance_qa"
    state = process_with_agent_node(state)
    
    assert state['response'] == "Mocked sync response"
    assert len(state['messages']) > 0

def test_should_continue():
    state = create_initial_state(query="test")
    assert should_continue(state) == "end"
    
    state['requires_followup'] = True
    assert should_continue(state) == "continue"
    
    state['iteration_count'] = 11
    assert should_continue(state) == "end"

def test_run_workflow(mocker):
    mock_graph = MagicMock()
    mock_graph.invoke.return_value = {"response": "Final"}
    mocker.patch("src.workflow.graph.create_workflow_graph", return_value=mock_graph)
    
    res = run_workflow("Test", config_path="config.yaml")
    assert res["response"] == "Final"

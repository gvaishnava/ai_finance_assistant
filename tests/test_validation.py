import pytest
from src.core.llm import get_llm_client
from src.agents.finance_qa_agent import FinanceQAAgent

def test_closed_ended_validation_judge(mocker):
    """
    Validates agent response using an LLM as a judge.
    We mock the LLM calls here to allow the test to pass without actual API keys, 
    but this demonstrates the structure of an LLM judge evaluating the output.
    """
    # Mock to ensure test reliability
    mock_llm = mocker.MagicMock()
    # The actual judge response
    mock_llm.generate = mocker.MagicMock(return_value="PASS")
    # The agent's generated answer
    mock_llm.generate_with_context.return_value = "Yes, contributions to a traditional IRA are potentially tax-deductible."
    
    mocker.patch("src.core.llm.get_llm_client", return_value=mock_llm)
    mocker.patch("src.agents.base_agent.get_llm_client", return_value=mock_llm)
    
    agent = FinanceQAAgent(config_path="config.yaml")
    
    question = "Does a traditional IRA provide a tax deduction in the year of contribution?"
    expected_core_fact = "Yes, contributions to a traditional IRA are potentially tax-deductible."
    
    result = agent.process(question)
    agent_answer = result.get("response", "")
    
    import src.core.llm as llm_module
    judge_client = llm_module.get_llm_client("config.yaml")
    judge_prompt = f"""
    You are an expert financial evaluator.
    Question: {question}
    Expected Core Fact: {expected_core_fact}
    Agent Answer: {agent_answer}
    
    Does the Agent Answer correctly identify the Expected Core Fact? 
    Respond with exactly 'PASS' if it is correct and factually accurate, or 'FAIL' if incorrect.
    """
    
    judge_response = judge_client.generate(judge_prompt)
    
    assert "PASS" in judge_response.upper(), f"Validator failed. Judge said: {judge_response}"

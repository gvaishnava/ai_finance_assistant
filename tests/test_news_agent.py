import pytest
from src.agents.news_agent import NewsSynthesizerAgent
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def news_agent(mocker):
    mocker.patch("os.getenv", side_effect=lambda k, d=None: "dummy" if "TAVILY" in k else d)
    mocker.patch("src.agents.news_agent.TavilyClient")
    mocker.patch("src.agents.base_agent.get_llm_client")
    mocker.patch("src.agents.base_agent.Retriever")
    return NewsSynthesizerAgent("config.yaml")


@pytest.mark.asyncio
async def test_news_agent_process(news_agent, mocker):
    news_agent.tavily_client.search.return_value = {
        "results": [{"content": "Market is up", "title": "News 1", "url": "url1"}]
    }
    news_agent.llm_client = AsyncMock()
    news_agent.llm_client.agenerate_with_context.return_value = "News Summary"
    
    result = await news_agent.async_process(query="What is the news for AAPL?")
    assert "response" in result
    assert "News Summary" in result["response"]

def test_news_agent_sync(news_agent, mocker):
    news_agent.tavily_client.search.return_value = {"results": []}
    news_agent.llm_client = MagicMock()
    news_agent.llm_client.generate_with_context.return_value = "No news found"
    news_agent.llm_client.generate.return_value = "No news found"
    
    result = news_agent.process(query="Hi")
    assert "No news found" in result["response"]




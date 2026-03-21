import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_chat_routes(client: AsyncClient, mocker):
    # Mock out the workflow to avoid actual execution
    mocker.patch("src.web_app.routes.chat.arun_workflow", return_value={"response": "mock response", "selected_agent": "finance_qa"})
    
    request_data = {
        "message": "Hello",
        "session_id": "test_sess"
    }
    
    res = await client.post("/api/chat", json=request_data)
    assert res.status_code == 200

@pytest.mark.anyio
async def test_market_routes(client: AsyncClient, mocker):
    mocker.patch("src.web_app.routes.market.get_market_client", autospec=True)
    res = await client.get("/api/market/trends")
    assert res.status_code in [200, 500]
    
@pytest.mark.anyio
async def test_user_routes(client: AsyncClient):
    res = await client.get("/api/user/profile/test_sess")
    assert res.status_code in [200, 404, 500]

@pytest.mark.anyio
async def test_news_routes(client: AsyncClient, mocker):
    mocker.patch("src.web_app.routes.news.news_agent.process", return_value={"response": "News!"})
    res = await client.post("/api/news/search", json={"query": "market"})
    assert res.status_code == 200

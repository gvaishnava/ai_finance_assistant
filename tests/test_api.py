
import pytest

@pytest.mark.anyio
async def test_health_check(client):
    """Test the health check endpoint returns 200 OK."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()

@pytest.mark.anyio
async def test_api_docs_accessible(client):
    """Test that the API documentation is accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200

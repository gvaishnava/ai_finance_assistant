import pytest
from fastapi.testclient import TestClient
from src.web_app.api import app
from unittest.mock import patch, AsyncMock

client = TestClient(app)

def test_portfolio_chat_endpoint_success():
    """Test that /api/chat/portfolio works with correctly structured request"""
    # Mock the workflow to avoid actual LLM calls
    with patch('src.web_app.routes.chat.arun_workflow', new_callable=AsyncMock) as mock_workflow:
        mock_workflow.return_value = {
            'response': 'Analysis complete',
            'selected_agent': 'portfolio',
            'agent_responses': [{'agent_display_name': 'Portfolio Agent', 'metadata': {}}]
        }
        
        payload = {
            "holdings": [
                {"symbol": "RELIANCE.NS", "quantity": 10, "average_price": 2500.0}
            ],
            "message": "Analyze my portfolio",
            "metadata": {"source": "test"}
        }
        
        response = client.post("/api/chat/portfolio", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data['response'] == 'Analysis complete'
        assert data['agent'] == 'portfolio'

def test_portfolio_chat_endpoint_no_metadata():
    """Test that /api/chat/portfolio works even if metadata is missing in request"""
    with patch('src.web_app.routes.chat.arun_workflow', new_callable=AsyncMock) as mock_workflow:
        mock_workflow.return_value = {
            'response': 'Analysis complete',
            'selected_agent': 'portfolio',
            'agent_responses': [{'agent_display_name': 'Portfolio Agent', 'metadata': {}}]
        }
        
        # Payload without metadata field
        payload = {
            "holdings": [
                {"symbol": "TCS.NS", "quantity": 5}
            ]
        }
        
        response = client.post("/api/chat/portfolio", json=payload)
        
        assert response.status_code == 200
        assert response.json()['response'] == 'Analysis complete'

if __name__ == "__main__":
    pytest.main([__file__])

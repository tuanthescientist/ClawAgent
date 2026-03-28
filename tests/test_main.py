"""Test for main FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    assert "version" in response.json()


@pytest.mark.asyncio
async def test_chat_endpoint_with_message(client):
    """Test chat endpoint with valid message."""
    with patch('src.main.agent.process', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = "Test response"
        
        response = client.post(
            "/api/v1/chat",
            json={"message": "Hello", "chat_id": "test-123"}
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"


def test_chat_endpoint_empty_message(client):
    """Test chat endpoint with empty message."""
    response = client.post(
        "/api/v1/chat",
        json={"message": "", "chat_id": "test-123"}
    )
    
    assert response.status_code == 400

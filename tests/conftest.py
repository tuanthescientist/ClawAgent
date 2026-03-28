"""Test configuration and fixtures."""

import pytest
import asyncio
from src.agents.openai_agent import OpenAIAgent
from src.integrations.whatsapp import WhatsAppManager


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openai_key():
    """Mock OpenAI API key for testing."""
    return "sk-test-mock-key-12345"


@pytest.fixture
def mock_twilio_creds():
    """Mock Twilio credentials."""
    return {
        "account_sid": "AC-test-mock-sid",
        "auth_token": "test-mock-auth-token",
        "whatsapp_number": "whatsapp:+15551234567",
        "webhook_token": "test-webhook-token"
    }

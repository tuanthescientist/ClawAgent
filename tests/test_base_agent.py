"""Tests for base agent."""

import pytest
from src.agents.base import BaseAgent, Message


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""
    
    async def process(self, user_input: str) -> str:
        """Simple echo implementation for testing."""
        self.add_message("user", user_input)
        response = f"Echo: {user_input}"
        self.add_message("assistant", response)
        return response


def test_message_creation():
    """Test Message object creation."""
    msg = Message(role="user", content="Hello", metadata={"id": "123"})
    
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.metadata["id"] == "123"


def test_message_to_dict():
    """Test Message.to_dict() conversion."""
    msg = Message(role="assistant", content="Hi there")
    msg_dict = msg.to_dict()
    
    assert msg_dict["role"] == "assistant"
    assert msg_dict["content"] == "Hi there"
    assert "timestamp" in msg_dict


def test_agent_creation():
    """Test agent initialization."""
    agent = ConcreteAgent(name="TestAgent", model="gpt-4")
    
    assert agent.name == "TestAgent"
    assert agent.model == "gpt-4"
    assert len(agent.conversation_history) == 0


@pytest.mark.asyncio
async def test_agent_process():
    """Test agent message processing."""
    agent = ConcreteAgent(name="TestAgent")
    response = await agent.process("Hello")
    
    assert response == "Echo: Hello"
    assert len(agent.conversation_history) == 2


def test_agent_add_message():
    """Test adding messages to history."""
    agent = ConcreteAgent(name="TestAgent")
    
    agent.add_message("user", "Test message")
    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0].role == "user"


def test_agent_conversation_history():
    """Test getting conversation history."""
    agent = ConcreteAgent(name="TestAgent")
    
    agent.add_message("user", "Message 1")
    agent.add_message("assistant", "Response 1")
    
    history = agent.get_conversation_history()
    
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"


def test_agent_clear_history():
    """Test clearing conversation history."""
    agent = ConcreteAgent(name="TestAgent")
    
    agent.add_message("user", "Message")
    assert len(agent.conversation_history) == 1
    
    agent.clear_history()
    assert len(agent.conversation_history) == 0

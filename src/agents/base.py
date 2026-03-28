"""Base Agent class for ClawAgent."""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class Message:
    """Represents a single message in conversation."""
    
    def __init__(self, role: str, content: str, metadata: Optional[Dict] = None):
        self.role = role  # "user", "assistant", "system"
        self.content = content
        self.timestamp = datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str, model: str = "gpt-4"):
        self.name = name
        self.model = model
        self.conversation_history: List[Message] = []
        self.system_prompt = self._get_system_prompt()
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent."""
        return f"""You are {self.name}, a helpful AI assistant. 
Be concise, accurate, and helpful in your responses.
When you don't know something, say so clearly."""
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to conversation history."""
        message = Message(role=role, content=content, metadata=metadata)
        self.conversation_history.append(message)
        logger.debug(f"Added {role} message: {content[:50]}...")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history in OpenAI format."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []
        logger.info(f"Cleared conversation history for {self.name}")
    
    @abstractmethod
    async def process(self, user_input: str) -> str:
        """Process user input and return response.
        
        Args:
            user_input: The user's message
            
        Returns:
            The agent's response
        """
        pass
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, model={self.model})>"

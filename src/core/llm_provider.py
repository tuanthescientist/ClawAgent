"""
Abstract base class for LLM providers.

Supports:
- OpenAI, Ollama, vLLM, Groq, LM Studio
- Streaming and non-streaming responses
- Health checks and timeout handling
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, AsyncGenerator
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
import logging


class Message(BaseModel):
    """Chat message"""
    role: str = Field(..., description="'user', 'assistant', 'system'")
    content: str = Field(..., description="Message content")


class LLMResponse(BaseModel):
    """LLM completion response"""
    content: str
    model: str
    tokens_used: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    stop_reason: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: float = 0.0


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Subclasses must implement:
    - complete(): Generate completion from messages
    - embed(): Generate embeddings
    - health_check(): Check provider health
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.
        
        Args:
            config: Provider-specific configuration
                - model (required)
                - temperature
                - max_tokens
                - timeout
                - etc.
        """
        self.config = config
        self.model = config.get("model")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 2000)
        self.timeout = config.get("timeout", 30)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from messages.
        
        Args:
            messages: Chat message history
            temperature: Optional override
            max_tokens: Optional override
            **kwargs: Provider-specific parameters
            
        Returns:
            LLMResponse with completion and metadata
            
        Raises:
            RuntimeError: If provider request fails
        """
        pass

    @abstractmethod
    async def complete_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate completion with streaming.
        
        Args:
            messages: Chat message history
            temperature: Optional override
            max_tokens: Optional override
            **kwargs: Provider-specific parameters
            
        Yields:
            Streaming text chunks
        """
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        Generate embeddings for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            RuntimeError: If embedding generation fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check provider health status.
        
        Returns:
            Dict with:
            - healthy: bool
            - latency_ms: float
            - details: str
            - model: str
        """
        pass

    async def with_timeout(
        self,
        coro,
        timeout: Optional[int] = None
    ) -> Any:
        """
        Execute coroutine with timeout.
        
        Args:
            coro: Coroutine to execute
            timeout: Timeout in seconds (uses self.timeout if None)
            
        Returns:
            Coroutine result
            
        Raises:
            TimeoutError: If timeout exceeded
        """
        timeout = timeout or self.timeout
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"{self.__class__.__name__} request timed out after {timeout}s"
            )

    @staticmethod
    def count_tokens(text: str, model: str = None) -> int:
        """
        Estimate token count for text.
        
        Simple approximation: ~4 characters per token
        
        Args:
            text: Text to count
            model: Model name (optional, for better estimation)
            
        Returns:
            Estimated token count
        """
        # Rough approximation
        return len(text) // 4

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model})"

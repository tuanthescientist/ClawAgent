"""
Groq LLM Provider implementation for ClawAgent v3.0

Provides fast inference via Groq's API using OpenAI-compatible format.

Supported models:
- mixtral-8x7b-32768
- llama2-70b-4096
- gemma-7b-it
"""

from typing import Optional, List, AsyncGenerator, Dict, Any
from datetime import datetime
import logging

from ..core.llm_provider import BaseLLMProvider, LLMResponse, Message

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class GroqProvider(BaseLLMProvider):
    """Groq LLM Provider - Fast inference, OpenAI-compatible API"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Groq provider.

        Config should include:
        - api_key: Groq API key
        - model: Model name (mixtral-8x7b-32768, llama2-70b, etc.)
        - temperature: 0-2, default 0.7
        - max_tokens: Max output tokens
        - timeout: Request timeout
        """
        if not GROQ_AVAILABLE:
            raise ImportError(
                "Groq SDK not installed. "
                "Install with: pip install groq"
            )

        super().__init__(config)

        self.api_key = config.get("api_key")
        if not self.api_key:
            raise ValueError("api_key is required in config")

        self.client = AsyncGroq(api_key=self.api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Groq"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[m.model_dump() for m in messages],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )

            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                tokens_input=response.usage.prompt_tokens,
                tokens_output=response.usage.completion_tokens,
                stop_reason=response.choices[0].finish_reason,
                metadata={
                    "provider": "groq",
                    "model": response.model,
                }
            )

        except Exception as e:
            self.logger.error(f"Groq completion failed: {e}")
            raise

    async def complete_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate completion with streaming using Groq"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[m.model_dump() for m in messages],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True,
                **kwargs
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            self.logger.error(f"Groq streaming failed: {e}")
            raise

    async def embed(self, text: str) -> List[float]:
        """
        Groq doesn't provide embeddings API.
        Use OpenAI or local embeddings instead.
        """
        raise NotImplementedError(
            "Groq doesn't provide embeddings. "
            "Use OpenAI embeddings or local models."
        )

    async def health_check(self) -> Dict[str, Any]:
        """Check Groq API health"""
        try:
            start = datetime.now()

            # Simple test request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=10,
            )

            latency_ms = (datetime.now() - start).total_seconds() * 1000

            return {
                "healthy": True,
                "model": self.model,
                "latency_ms": latency_ms,
                "provider": "groq",
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "provider": "groq",
            }

    def __repr__(self) -> str:
        return f"GroqProvider(model={self.model})"

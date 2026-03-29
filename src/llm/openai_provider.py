"""
OpenAI LLM Provider implementation for ClawAgent v3.0

Provides:
- Streaming and non-streaming completions
- Embedding generation
- Health checks
"""

from typing import Optional, List, AsyncGenerator, Dict, Any
from datetime import datetime
import logging

from ..core.llm_provider import BaseLLMProvider, LLMResponse, Message

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM Provider using gpt-4-turbo and similar models"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI provider.

        Config should include:
        - api_key: OpenAI API key
        - model: Model name (gpt-4-turbo, gpt-4, gpt-3.5-turbo)
        - base_url: Optional custom base URL
        - org_id: Optional organization ID
        - temperature: 0-2, default 0.7
        - max_tokens: Max output tokens
        - timeout: Request timeout
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI SDK not installed. "
                "Install with: pip install openai"
            )

        super().__init__(config)
        
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.org_id = config.get("org_id")

        if not self.api_key:
            raise ValueError("api_key is required in config")

        # Initialize async client
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            organization=self.org_id,
            timeout=self.timeout,
        )

        self.logger = logging.getLogger(self.__class__.__name__)

    async def complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion"""
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
                metadata={"provider": "openai"}
            )
        except Exception as e:
            self.logger.error(f"OpenAI completion failed: {e}")
            raise

    async def complete_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate completion with streaming"""
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
            self.logger.error(f"OpenAI streaming failed: {e}")
            raise

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI API"""
        try:
            response = await self.client.embeddings.create(
                model=self.config.get("embedding_model", "text-embedding-3-small"),
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"OpenAI embedding failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI API health"""
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
                "provider": "openai",
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "provider": "openai",
            }

    def __repr__(self) -> str:
        return f"OpenAIProvider(model={self.model}, base_url={self.base_url})"

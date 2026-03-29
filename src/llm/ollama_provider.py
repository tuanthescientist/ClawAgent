"""
Ollama LLM Provider implementation for ClawAgent v3.0

Provides local LLM support via Ollama API.

Supports models:
- qwen2.5:14b, qwen2.5:32b
- deepseek-r1
- llama2, llama3, llama3.3
- mistral, mixtral
- gemma2
- neural-chat
- etc.
"""

from typing import Optional, List, AsyncGenerator, Dict, Any
from datetime import datetime
import logging
import aiohttp

from ..core.llm_provider import BaseLLMProvider, LLMResponse, Message


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM Provider for local models"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama provider.

        Config should include:
        - host: Ollama API host (default: http://localhost:11434)
        - model: Model name (qwen2.5:14b, llama2, etc.)
        - temperature: 0-2, default 0.7
        - max_tokens: Max output tokens
        - timeout: Request timeout
        """
        super().__init__(config)
        
        self.host = config.get("host", "http://localhost:11434")
        self.api_endpoint = f"{self.host}/api"
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(self.__class__.__name__)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def complete(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate completion using Ollama"""
        try:
            session = await self._get_session()

            # Convert messages to chat format
            chat_messages = [
                {
                    "role": m.role,
                    "content": m.content
                }
                for m in messages
            ]

            payload = {
                "model": self.model,
                "messages": chat_messages,
                "temperature": temperature or self.temperature,
                "stream": False,
            }

            async with session.post(
                f"{self.api_endpoint}/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama error: {error_text}")

                data = await response.json()

                return LLMResponse(
                    content=data["message"]["content"],
                    model=self.model,
                    tokens_used=data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
                    tokens_input=data.get("prompt_eval_count", 0),
                    tokens_output=data.get("eval_count", 0),
                    metadata={
                        "provider": "ollama",
                        "eval_duration_ms": data.get("eval_duration", 0) / 1_000_000,
                    }
                )

        except Exception as e:
            self.logger.error(f"Ollama completion failed: {e}")
            raise

    async def complete_stream(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate completion with streaming using Ollama"""
        try:
            session = await self._get_session()

            chat_messages = [
                {
                    "role": m.role,
                    "content": m.content
                }
                for m in messages
            ]

            payload = {
                "model": self.model,
                "messages": chat_messages,
                "temperature": temperature or self.temperature,
                "stream": True,
            }

            async with session.post(
                f"{self.api_endpoint}/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama error: {error_text}")

                async for line in response.content:
                    if line:
                        data = eval(line.decode())  # Note: using eval for simplicity
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]

        except Exception as e:
            self.logger.error(f"Ollama streaming failed: {e}")
            raise

    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using Ollama"""
        try:
            session = await self._get_session()

            payload = {
                "model": self.model,
                "prompt": text,
            }

            async with session.post(
                f"{self.api_endpoint}/embeddings",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(f"Ollama embeddings error: {error_text}")

                data = await response.json()
                return data["embedding"]

        except Exception as e:
            self.logger.error(f"Ollama embedding failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama API health"""
        try:
            session = await self._get_session()
            start = datetime.now()

            # Check if model is available
            async with session.get(
                f"{self.host}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status != 200:
                    return {
                        "healthy": False,
                        "error": f"HTTP {response.status}",
                        "provider": "ollama",
                    }

                data = await response.json()
                latency_ms = (datetime.now() - start).total_seconds() * 1000

                # Check if our model is available
                models = [m["name"].split(":")[0] for m in data.get("models", [])]
                model_available = any(self.model.startswith(m) for m in models)

                return {
                    "healthy": model_available,
                    "model": self.model,
                    "latency_ms": latency_ms,
                    "available_models": models[:5],  # Top 5
                    "provider": "ollama",
                }

        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "provider": "ollama",
            }

    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

    def __repr__(self) -> str:
        return f"OllamaProvider(model={self.model}, host={self.host})"

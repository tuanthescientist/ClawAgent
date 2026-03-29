"""Local LLM providers - Ollama, vLLM, LM Studio."""

import logging
from typing import Optional, List, Dict, Any
import aiohttp
import json
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LocalLLMProvider(ABC):
    """Base class for local LLM providers."""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = 0.7
        self.max_tokens = 2000
    
    @abstractmethod
    async def generate(self, messages: List[Dict], tools: Optional[List] = None) -> Dict[str, Any]:
        """Generate response from local LLM.
        
        Args:
            messages: Message history
            tools: Optional tool definitions
            
        Returns:
            dict: Response with content and finish_reason
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available."""
        pass


class OllamaProvider(LocalLLMProvider):
    """Ollama local LLM provider."""
    
    async def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {str(e)}")
            return False
    
    async def generate(self, messages: List[Dict], tools: Optional[List] = None) -> Dict[str, Any]:
        """Generate response using Ollama.
        
        Args:
            messages: Message history
            tools: Optional tool definitions (not yet supported by Ollama)
            
        Returns:
            dict: Response
        """
        try:
            # Format messages for Ollama
            prompt = self._format_messages(messages)
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "content": data.get("response", "").strip(),
                            "tool_calls": None,
                            "finish_reason": "stop",
                            "provider": "ollama"
                        }
                    else:
                        error = await resp.text()
                        logger.error(f"Ollama error: {error}")
                        return {
                            "content": f"Ollama error: {resp.status}",
                            "tool_calls": None,
                            "finish_reason": "error"
                        }
        
        except asyncio.TimeoutError:
            logger.error("Ollama request timeout")
            return {
                "content": "Request timeout - Ollama may be busy",
                "tool_calls": None,
                "finish_reason": "error"
            }
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": None,
                "finish_reason": "error"
            }
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Format messages for Ollama chat format.
        
        Args:
            messages: List of messages
            
        Returns:
            str: Formatted prompt
        """
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                prompt += f"[SYSTEM]\n{content}\n\n"
            elif role == "user":
                prompt += f"[USER]\n{content}\n\n"
            elif role == "assistant":
                prompt += f"[ASSISTANT]\n{content}\n\n"
        
        prompt += "[ASSISTANT]\n"
        return prompt


class VLLMProvider(LocalLLMProvider):
    """vLLM local LLM provider."""
    
    async def is_available(self) -> bool:
        """Check if vLLM is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v1/models", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.warning(f"vLLM not available: {str(e)}")
            return False
    
    async def generate(self, messages: List[Dict], tools: Optional[List] = None) -> Dict[str, Any]:
        """Generate response using vLLM (OpenAI-compatible API).
        
        Args:
            messages: Message history
            tools: Optional tool definitions
            
        Returns:
            dict: Response
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": 0.9
            }
            
            # Add tools if provided
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        choice = data["choices"][0]
                        
                        return {
                            "content": choice.get("message", {}).get("content", ""),
                            "tool_calls": choice.get("message", {}).get("tool_calls"),
                            "finish_reason": choice.get("finish_reason", "stop"),
                            "provider": "vllm"
                        }
                    else:
                        error = await resp.text()
                        logger.error(f"vLLM error: {error}")
                        return {
                            "content": f"vLLM error: {resp.status}",
                            "tool_calls": None,
                            "finish_reason": "error"
                        }
        
        except asyncio.TimeoutError:
            logger.error("vLLM request timeout")
            return {
                "content": "Request timeout - vLLM may be busy",
                "tool_calls": None,
                "finish_reason": "error"
            }
        except Exception as e:
            logger.error(f"vLLM generation error: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": None,
                "finish_reason": "error"
            }


class LMStudioProvider(LocalLLMProvider):
    """LM Studio local LLM provider."""
    
    async def is_available(self) -> bool:
        """Check if LM Studio is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v1/models", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    return resp.status == 200
        except Exception as e:
            logger.warning(f"LM Studio not available: {str(e)}")
            return False
    
    async def generate(self, messages: List[Dict], tools: Optional[List] = None) -> Dict[str, Any]:
        """Generate response using LM Studio (OpenAI-compatible API).
        
        Args:
            messages: Message history
            tools: Optional tool definitions
            
        Returns:
            dict: Response
        """
        try:
            payload = {
                "model": self.model or "local-model",
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "top_p": 0.9
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        choice = data["choices"][0]
                        
                        return {
                            "content": choice.get("message", {}).get("content", ""),
                            "tool_calls": None,
                            "finish_reason": choice.get("finish_reason", "stop"),
                            "provider": "lm_studio"
                        }
                    else:
                        error = await resp.text()
                        logger.error(f"LM Studio error: {error}")
                        return {
                            "content": f"LM Studio error: {resp.status}",
                            "tool_calls": None,
                            "finish_reason": "error"
                        }
        
        except asyncio.TimeoutError:
            logger.error("LM Studio request timeout")
            return {
                "content": "Request timeout - LM Studio may be busy",
                "tool_calls": None,
                "finish_reason": "error"
            }
        except Exception as e:
            logger.error(f"LM Studio generation error: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": None,
                "finish_reason": "error"
            }


class LocalLLMFactory:
    """Factory for creating local LLM providers."""
    
    PROVIDERS = {
        "ollama": OllamaProvider,
        "vllm": VLLMProvider,
        "lm_studio": LMStudioProvider,
    }
    
    @classmethod
    async def create(
        cls,
        provider: str,
        base_url: str,
        model: str
    ) -> Optional[LocalLLMProvider]:
        """Create a local LLM provider instance.
        
        Args:
            provider: Provider name (ollama, vllm, lm_studio)
            base_url: API base URL
            model: Model name
            
        Returns:
            LocalLLMProvider instance or None if not available
        """
        if provider.lower() not in cls.PROVIDERS:
            logger.error(f"Unknown provider: {provider}")
            return None
        
        provider_class = cls.PROVIDERS[provider.lower()]
        instance = provider_class(base_url, model)
        
        # Check availability
        if await instance.is_available():
            logger.info(f"Initialized {provider} provider at {base_url}")
            return instance
        else:
            logger.error(f"{provider} not available at {base_url}")
            return None
    
    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names."""
        return list(cls.PROVIDERS.keys())


import asyncio

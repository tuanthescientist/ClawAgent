"""OpenAI and alternative LLM integrations."""

import logging
from typing import Optional
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAILLMClient:
    """OpenAI API client."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model name (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.temperature = 0.7
    
    async def get_response(self,
                          messages: list,
                          tools: Optional[list] = None,
                          tool_choice: Optional[str] = None) -> dict:
        """Get response from OpenAI API with optional tool calling.
        
        Args:
            messages: Message history
            tools: Available tools schema
            tool_choice: Tool choice strategy ("auto", "required", etc.)
            
        Returns:
            dict with response and any tool calls
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": 2000
            }
            
            if tools:
                kwargs["tools"] = tools
                if tool_choice:
                    kwargs["tool_choice"] = tool_choice
            
            response = await self.client.chat.completions.create(**kwargs)
            
            return {
                "content": response.choices[0].message.content,
                "tool_calls": getattr(response.choices[0].message, "tool_calls", None),
                "finish_reason": response.choices[0].finish_reason
            }
        
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": None,
                "finish_reason": "error"
            }


class LocalLLMClient:
    """Local LLM via Ollama or similar."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        """Initialize Local LLM client.
        
        Args:
            base_url: Ollama server URL
            model: Model name
        """
        self.base_url = base_url
        self.model = model
        import aiohttp
        self.session = aiohttp.ClientSession()
    
    async def get_response(self, messages: list) -> dict:
        """Get response from local LLM."""
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "stream": False
            }
            
            async with self.session.post(
                f"{self.base_url}/api/chat",
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "content": data.get("message", {}).get("content", ""),
                        "tool_calls": None,
                        "finish_reason": "stop"
                    }
                else:
                    return {
                        "content": f"Local LLM error: {resp.status}",
                        "tool_calls": None,
                        "finish_reason": "error"
                    }
        except Exception as e:
            logger.error(f"Local LLM error: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "tool_calls": None,
                "finish_reason": "error"
            }

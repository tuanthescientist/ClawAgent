"""ChatGPT via browser/unofficial API."""

import aiohttp
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ChatGPTBrowserAPI:
    """ChatGPT API using browser/unofficial method."""
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize ChatGPT Browser API.
        
        Args:
            access_token: ChatGPT web session token (from browser cookies)
                         Get from: https://chat.openai.com/api/auth/session
        """
        self.access_token = access_token
        self.base_url = "https://api.chatgpt.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}" if access_token else "",
            "Content-Type": "application/json"
        }
    
    async def send_message(self, message: str, conversation_history: Optional[List] = None) -> str:
        """Send message to ChatGPT."""
        try:
            if not self.access_token:
                raise ValueError("ChatGPT access token not configured")
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "messages": conversation_history or [
                        {"role": "user", "content": message}
                    ],
                    "model": "text-davinci-002-render-sha",
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{self.base_url}/conversation",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("message", {}).get("content", "")
                    else:
                        error_msg = await resp.text()
                        logger.error(f"ChatGPT API error: {resp.status} - {error_msg}")
                        return f"ChatGPT API error: {resp.status}"
        
        except Exception as e:
            logger.error(f"ChatGPT error: {str(e)}")
            return f"Error: {str(e)}"


class DualLLMClient:
    """Unified client for both OpenAI and ChatGPT."""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 chatgpt_access_token: Optional[str] = None):
        """Initialize dual LLM client.
        
        Args:
            openai_api_key: OpenAI API key
            chatgpt_access_token: ChatGPT session token
        """
        self.openai_available = bool(openai_api_key)
        self.chatgpt_available = bool(chatgpt_access_token)
        
        if not (self.openai_available or self.chatgpt_available):
            raise ValueError("At least one API key must be provided")
        
        self.openai_api_key = openai_api_key
        self.chatgpt_access_token = chatgpt_access_token
        self.chatgpt_client = ChatGPTBrowserAPI(chatgpt_access_token) if chatgpt_access_token else None
    
    async def get_response(self,
                          message: str,
                          history: Optional[List] = None,
                          prefer_chatgpt: bool = False) -> tuple[str, str]:
        """Get response from available LLM.
        
        Args:
            message: User message
            history: Conversation history
            prefer_chatgpt: Prefer ChatGPT over OpenAI if both available
            
        Returns:
            (response, source) - response text and which API was used
        """
        if prefer_chatgpt and self.chatgpt_available:
            response = await self.chatgpt_client.send_message(message, history)
            return response, "chatgpt"
        elif self.openai_available:
            # Will use OpenAI in the agent
            return "", "openai"
        elif self.chatgpt_available:
            response = await self.chatgpt_client.send_message(message, history)
            return response, "chatgpt"
        else:
            return "No LLM available", "none"

"""OpenAI-powered ClawAgent implementation."""

import logging
from typing import Optional
from openai import AsyncOpenAI

from .base import BaseAgent

logger = logging.getLogger(__name__)


class OpenAIAgent(BaseAgent):
    """Agent powered by OpenAI's API."""
    
    def __init__(self, name: str, api_key: str, model: str = "gpt-4"):
        super().__init__(name, model)
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def process(self, user_input: str) -> str:
        """Process user input using OpenAI API."""
        try:
            # Add user message to history
            self.add_message("user", user_input)
            
            # Prepare messages for API call
            messages = [
                {"role": "system", "content": self.system_prompt},
                *self.get_conversation_history()
            ]
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract response
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.add_message("assistant", assistant_message)
            
            logger.info(f"Successfully processed message from {self.name}")
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            error_message = f"I encountered an error: {str(e)}"
            self.add_message("assistant", error_message)
            return error_message

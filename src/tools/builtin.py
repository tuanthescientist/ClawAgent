"""Built-in tools for agent use."""

import asyncio
import json
from typing import Any, Dict
from datetime import datetime
import math

from .base import Tool


class WebSearchTool(Tool):
    """Simulated web search tool."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information"
        )
    
    async def execute(self, query: str) -> str:
        """Execute web search."""
        # Simulated search - replace with real API
        return f"Search results for '{query}': [Simulated results]"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        }


class CalculatorTool(Tool):
    """Calculator tool for mathematical operations."""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations"
        )
    
    async def execute(self, expression: str) -> str:
        """Execute mathematical expression."""
        try:
            # Safe evaluation using math library
            result = eval(expression, {"__builtins__": {}}, {
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "log": math.log,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e
            })
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Perform mathematical calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression (e.g., '2*3+4')"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }


class GetTimeTool(Tool):
    """Get current time and date."""
    
    def __init__(self):
        super().__init__(
            name="get_time",
            description="Get current time and date"
        )
    
    async def execute(self) -> str:
        """Get current time."""
        now = datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_time",
                "description": "Get current time and date",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }


class JsonParserTool(Tool):
    """Parse and validate JSON."""
    
    def __init__(self):
        super().__init__(
            name="json_parser",
            description="Parse and validate JSON data"
        )
    
    async def execute(self, json_string: str) -> str:
        """Parse JSON."""
        try:
            data = json.loads(json_string)
            return f"Valid JSON: {json.dumps(data, indent=2)}"
        except json.JSONDecodeError as e:
            return f"Invalid JSON: {str(e)}"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "json_parser",
                "description": "Parse and validate JSON data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "json_string": {
                            "type": "string",
                            "description": "JSON string to parse"
                        }
                    },
                    "required": ["json_string"]
                }
            }
        }


class FillerTool(Tool):
    """Placeholder tool for demonstration."""
    
    def __init__(self, name: str, description: str):
        super().__init__(name, description)
    
    async def execute(self, **kwargs) -> str:
        """Execute placeholder tool."""
        return f"{self.name} executed with: {kwargs}"
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }


def get_default_tools():
    """Get default built-in tools."""
    return [
        WebSearchTool(),
        CalculatorTool(),
        GetTimeTool(),
        JsonParserTool(),
    ]

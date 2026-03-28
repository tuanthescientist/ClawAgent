"""Base Tool class and Tool Registry."""

import json
import inspect
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel


class ToolParameter(BaseModel):
    """Tool parameter definition."""
    name: str
    type: str  # "string", "integer", "number", "boolean", "array", "object"
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None


class Tool(ABC):
    """Base class for all tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """Execute the tool.
        
        Returns:
            str: Result of tool execution
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """Get OpenAI function schema for tool."""
        pass


class ToolRegistry:
    """Registry for managing tools."""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self.tools.values())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get schemas for all tools."""
        return [tool.get_schema() for tool in self.tools.values()]
    
    async def execute_tool(self, name: str, **kwargs) -> str:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return f"Error: Tool '{name}' not found"
        
        try:
            result = await tool.execute(**kwargs)
            return str(result)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"


def create_tool_from_function(func: Callable, name: Optional[str] = None) -> Tool:
    """Create a Tool wrapper from a Python function."""
    
    tool_name = name or func.__name__
    tool_desc = func.__doc__ or "No description"
    
    sig = inspect.signature(func)
    
    class FunctionTool(Tool):
        async def execute(self, **kwargs) -> str:
            if inspect.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                result = func(**kwargs)
            return str(result)
        
        def get_schema(self) -> Dict[str, Any]:
            parameters = {}
            for param_name, param in sig.parameters.items():
                param_type = "string"
                if param.annotation != inspect.Parameter.empty:
                    type_name = param.annotation.__name__ if hasattr(param.annotation, '__name__') else str(param.annotation)
                    if type_name == "int":
                        param_type = "integer"
                    elif type_name == "float":
                        param_type = "number"
                    elif type_name == "bool":
                        param_type = "boolean"
                
                parameters[param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}"
                }
            
            return {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_desc,
                    "parameters": {
                        "type": "object",
                        "properties": parameters,
                        "required": list(sig.parameters.keys())
                    }
                }
            }
    
    return FunctionTool(tool_name, tool_desc)

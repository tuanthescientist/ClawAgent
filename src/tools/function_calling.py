"""Enhanced function calling system for agents."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ParameterType(str, Enum):
    """Parameter type definitions."""
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class Parameter(BaseModel):
    """Tool parameter definition."""
    name: str
    type: ParameterType
    description: str
    required: bool = True
    enum: Optional[List[Any]] = None
    default: Optional[Any] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    items: Optional[Dict[str, Any]] = None  # For array types


class ToolCall(BaseModel):
    """A tool call from the agent."""
    id: str
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    """Result from tool execution."""
    tool_call_id: str
    name: str
    result: str
    success: bool = True
    error: Optional[str] = None


class EnhancedTool(ABC):
    """Enhanced base class for tools with full function calling support."""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: List[Parameter],
        category: str = "general",
        requires_context: bool = False
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.category = category
        self.requires_context = requires_context
        self._execution_count = 0
        self._last_result = None
    
    async def execute(self, **kwargs) -> str:
        """Execute the tool with arguments.
        
        Args:
            **kwargs: Tool arguments
            
        Returns:
            str: Tool execution result
        """
        try:
            # Validate arguments
            validated_args = self._validate_arguments(kwargs)
            
            # Execute tool
            result = await self._execute_impl(**validated_args)
            
            # Track execution
            self._execution_count += 1
            self._last_result = result
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {str(e)}")
            return f"Tool execution error: {str(e)}"
    
    @abstractmethod
    async def _execute_impl(self, **kwargs) -> str:
        """Implementation of tool execution. Must be overridden."""
        pass
    
    def _validate_arguments(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean arguments.
        
        Args:
            kwargs: Arguments to validate
            
        Returns:
            dict: Validated arguments
            
        Raises:
            ValueError: If required arguments missing or invalid
        """
        validated = {}
        
        for param in self.parameters:
            if param.name not in kwargs:
                if param.required and param.default is None:
                    raise ValueError(f"Missing required parameter: {param.name}")
                validated[param.name] = param.default
            else:
                value = kwargs[param.name]
                
                # Type validation
                if param.type == ParameterType.STRING and not isinstance(value, str):
                    value = str(value)
                elif param.type == ParameterType.INTEGER and not isinstance(value, int):
                    value = int(value)
                elif param.type == ParameterType.NUMBER and not isinstance(value, (int, float)):
                    value = float(value)
                
                # Enum validation
                if param.enum and value not in param.enum:
                    raise ValueError(f"Invalid value for {param.name}: {value}")
                
                # Range validation
                if param.min_value is not None and value < param.min_value:
                    raise ValueError(f"{param.name} below minimum: {param.min_value}")
                if param.max_value is not None and value > param.max_value:
                    raise ValueError(f"{param.name} exceeds maximum: {param.max_value}")
                
                validated[param.name] = value
        
        return validated
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """Get OpenAI function schema.
        
        Returns:
            dict: OpenAI compatible schema
        """
        properties = {}
        required = []
        
        for param in self.parameters:
            schema = {
                "type": param.type.value,
                "description": param.description
            }
            
            if param.enum:
                schema["enum"] = param.enum
            if param.min_value is not None:
                schema["minimum"] = param.min_value
            if param.max_value is not None:
                schema["maximum"] = param.max_value
            if param.pattern:
                schema["pattern"] = param.pattern
            if param.items:
                schema["items"] = param.items
            
            properties[param.name] = schema
            
            if param.required:
                required.append(param.name)
        
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
    
    def get_anthropic_schema(self) -> Dict[str, Any]:
        """Get Anthropic (Claude) compatible schema."""
        properties = {}
        required = []
        
        for param in self.parameters:
            schema = {
                "type": param.type.value,
                "description": param.description
            }
            
            if param.enum:
                schema["enum"] = param.enum
            if param.min_value is not None:
                schema["minimum"] = param.min_value
            if param.max_value is not None:
                schema["maximum"] = param.max_value
            
            properties[param.name] = schema
            
            if param.required:
                required.append(param.name)
        
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name}, params={len(self.parameters)})>"


class FunctionCallingAgent:
    """Agent with function calling support."""
    
    def __init__(self, name: str = "FunctionCallingAgent"):
        self.name = name
        self.tools: Dict[str, EnhancedTool] = {}
        self.call_history: List[ToolCall] = []
        self.result_history: List[ToolResult] = []
    
    def register_tool(self, tool: EnhancedTool) -> None:
        """Register a tool.
        
        Args:
            tool: EnhancedTool instance to register
        """
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def register_tools(self, tools: List[EnhancedTool]) -> None:
        """Register multiple tools.
        
        Args:
            tools: List of EnhancedTool instances
        """
        for tool in tools:
            self.register_tool(tool)
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call.
        
        Args:
            tool_call: ToolCall to execute
            
        Returns:
            ToolResult with execution result
        """
        self.call_history.append(tool_call)
        
        if tool_call.name not in self.tools:
            result = ToolResult(
                tool_call_id=tool_call.id,
                name=tool_call.name,
                result=f"Tool not found: {tool_call.name}",
                success=False,
                error="Tool not registered"
            )
            self.result_history.append(result)
            return result
        
        try:
            tool = self.tools[tool_call.name]
            result_str = await tool.execute(**tool_call.arguments)
            
            result = ToolResult(
                tool_call_id=tool_call.id,
                name=tool_call.name,
                result=result_str,
                success=True
            )
            self.result_history.append(result)
            
            logger.info(f"Tool execution successful: {tool_call.name}")
            return result
        
        except Exception as e:
            error = str(e)
            logger.error(f"Tool execution failed: {error}")
            result = ToolResult(
                tool_call_id=tool_call.id,
                name=tool_call.name,
                result=str(e),
                success=False,
                error=error
            )
            self.result_history.append(result)
            return result
    
    def get_tools_schema(self, format: str = "openai") -> List[Dict[str, Any]]:
        """Get schemas for all registered tools.
        
        Args:
            format: Schema format ("openai", "anthropic")
            
        Returns:
            list: Tool schemas
        """
        schemas = []
        for tool in self.tools.values():
            if format == "anthropic":
                schemas.append(tool.get_anthropic_schema())
            else:
                schemas.append(tool.get_openai_schema())
        
        return schemas
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about all registered tools.
        
        Returns:
            dict: Tool information
        """
        info = {}
        for name, tool in self.tools.items():
            params = [
                {
                    "name": p.name,
                    "type": p.type.value,
                    "required": p.required,
                    "description": p.description
                }
                for p in tool.parameters
            ]
            
            info[name] = {
                "description": tool.description,
                "category": tool.category,
                "parameters": params,
                "execution_count": tool._execution_count
            }
        
        return info
    
    def clear_history(self) -> None:
        """Clear call and result history."""
        self.call_history = []
        self.result_history = []
        logger.info("Cleared function calling history")

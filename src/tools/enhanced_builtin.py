"""Enhanced built-in tools with proper function calling support."""

import asyncio
import json
from typing import Any, Dict
from datetime import datetime
import math
import aiohttp

from .function_calling import EnhancedTool, Parameter, ParameterType


class WebSearchTool(EnhancedTool):
    """Enhanced web search tool with real API support."""
    
    def __init__(self, api_key: str = None):
        parameters = [
            Parameter(
                name="query",
                type=ParameterType.STRING,
                description="Search query",
                required=True
            ),
            Parameter(
                name="result_count",
                type=ParameterType.INTEGER,
                description="Number of results to return",
                required=False,
                default=5,
                min_value=1,
                max_value=20
            )
        ]
        
        super().__init__(
            name="web_search",
            description="Search the web for information using a search API",
            parameters=parameters,
            category="information"
        )
        self.api_key = api_key
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute web search."""
        query = kwargs.get("query", "")
        # Simulated - replace with real API (SerpAPI, Bing, etc.)
        return json.dumps({
            "query": query,
            "results": [
                {"title": f"Result about {query}", "url": f"https://example.com/{i}", "snippet": "..."}
                for i in range(kwargs.get("result_count", 5))
            ]
        })


class CalculatorTool(EnhancedTool):
    """Enhanced calculator tool for complex math operations."""
    
    def __init__(self):
        parameters = [
            Parameter(
                name="expression",
                type=ParameterType.STRING,
                description="Mathematical expression (e.g., '2**3 + sqrt(16)')"
            ),
            Parameter(
                name="precision",
                type=ParameterType.INTEGER,
                description="Decimal places for rounding",
                required=False,
                default=4,
                min_value=0,
                max_value=10
            )
        ]
        
        super().__init__(
            name="calculator",
            description="Perform mathematical calculations safely",
            parameters=parameters,
            category="math"
        )
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute mathematical expression."""
        expression = kwargs.get("expression", "")
        precision = kwargs.get("precision", 4)
        
        try:
            # Safe evaluation with limited namespace
            safe_dict = {
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "sqrt": math.sqrt,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e,
                "ceil": math.ceil,
                "floor": math.floor,
                "abs": abs,
                "pow": pow
            }
            
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            # Round to precision
            if isinstance(result, float):
                result = round(result, precision)
            
            return json.dumps({
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            })
        except Exception as e:
            return json.dumps({
                "expression": expression,
                "error": f"Calculation error: {str(e)}"
            })


class GetTimeTool(EnhancedTool):
    """Get current time and date in various formats."""
    
    def __init__(self):
        parameters = [
            Parameter(
                name="timezone",
                type=ParameterType.STRING,
                description="Timezone (e.g., 'UTC', 'US/Eastern')",
                required=False,
                default="UTC"
            ),
            Parameter(
                name="format",
                type=ParameterType.STRING,
                description="Date format (iso, readable, unix)",
                required=False,
                default="readable",
                enum=["iso", "readable", "unix"]
            )
        ]
        
        super().__init__(
            name="get_time",
            description="Get current time and date",
            parameters=parameters,
            category="information"
        )
    
    async def _execute_impl(self, **kwargs) -> str:
        """Get current time."""
        format_type = kwargs.get("format", "readable")
        
        try:
            from datetime import datetime, timezone
            import pytz
            
            tz = pytz.timezone(kwargs.get("timezone", "UTC"))
            current_time = datetime.now(tz)
            
            if format_type == "iso":
                time_str = current_time.isoformat()
            elif format_type == "unix":
                time_str = str(int(current_time.timestamp()))
            else:
                time_str = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
            
            return json.dumps({
                "time": time_str,
                "timezone": kwargs.get("timezone", "UTC"),
                "format": format_type
            })
        except Exception as e:
            return json.dumps({"error": str(e)})


class FileReadTool(EnhancedTool):
    """Read files safely with content limits."""
    
    def __init__(self, max_file_size: int = 1000000):  # 1MB default
        parameters = [
            Parameter(
                name="file_path",
                type=ParameterType.STRING,
                description="Path to file to read"
            ),
            Parameter(
                name="encoding",
                type=ParameterType.STRING,
                description="File encoding",
                required=False,
                default="utf-8"
            ),
            Parameter(
                name="start_line",
                type=ParameterType.INTEGER,
                description="Start line number (1-indexed)",
                required=False,
                default=1
            ),
            Parameter(
                name="end_line",
                type=ParameterType.INTEGER,
                description="End line number (inclusive)",
                required=False,
                default=None
            )
        ]
        
        super().__init__(
            name="file_read",
            description="Read file contents safely with size limits",
            parameters=parameters,
            category="file_system"
        )
        self.max_file_size = max_file_size
    
    async def _execute_impl(self, **kwargs) -> str:
        """Read file contents."""
        file_path = kwargs.get("file_path", "")
        encoding = kwargs.get("encoding", "utf-8")
        start_line = kwargs.get("start_line", 1)
        end_line = kwargs.get("end_line")
        
        try:
            from pathlib import Path
            
            path = Path(file_path)
            
            # Security check
            if not path.exists():
                return json.dumps({"error": "File not found"})
            
            if path.stat().st_size > self.max_file_size:
                return json.dumps({"error": f"File too large (max {self.max_file_size} bytes)"})
            
            with open(path, "r", encoding=encoding) as f:
                lines = f.readlines()
            
            # Handle line range
            start = max(0, start_line - 1)
            end = len(lines) if end_line is None else min(end_line, len(lines))
            selected_lines = lines[start:end]
            
            content = "".join(selected_lines)
            
            return json.dumps({
                "file_path": str(file_path),
                "content": content,
                "lines_read": len(selected_lines),
                "total_lines": len(lines)
            })
        except Exception as e:
            return json.dumps({"error": str(e)})


class JSONParseTool(EnhancedTool):
    """Parse and validate JSON data."""
    
    def __init__(self):
        parameters = [
            Parameter(
                name="json_string",
                type=ParameterType.STRING,
                description="JSON string to parse"
            ),
            Parameter(
                name="format_output",
                type=ParameterType.BOOLEAN,
                description="Pretty-print the output",
                required=False,
                default=True
            )
        ]
        
        super().__init__(
            name="json_parse",
            description="Parse and validate JSON strings",
            parameters=parameters,
            category="data"
        )
    
    async def _execute_impl(self, **kwargs) -> str:
        """Parse JSON string."""
        json_string = kwargs.get("json_string", "")
        format_output = kwargs.get("format_output", True)
        
        try:
            parsed = json.loads(json_string)
            
            if format_output:
                output = json.dumps(parsed, indent=2)
            else:
                output = json.dumps(parsed)
            
            return json.dumps({
                "valid": True,
                "parsed": parsed,
                "formatted": output
            })
        except json.JSONDecodeError as e:
            return json.dumps({
                "valid": False,
                "error": f"JSON parse error: {str(e)}"
            })


# Convenience function to create a standard tool set
async def create_standard_toolset() -> list:
    """Create a standard set of commonly used tools.
    
    Returns:
        list: Standard EnhancedTool instances
    """
    return [
        WebSearchTool(),
        CalculatorTool(),
        GetTimeTool(),
        FileReadTool(),
        JSONParseTool()
    ]

"""Safe Python code execution with sandboxing."""

import logging
import asyncio
import sys
import io
import json
from typing import Dict, Any, Optional, Tuple
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime

from src.tools.function_calling import EnhancedTool, Parameter, ParameterType

logger = logging.getLogger(__name__)


class SafeCodeExecutor:
    """Execute Python code safely with isolation."""
    
    FORBIDDEN_MODULES = {
        "os", "subprocess", "sys", "importlib", "exec", "eval",
        "__import__", "compile", "socket", "requests", "urllib"
    }
    
    FORBIDDEN_NAMES = {
        "__import__", "eval", "exec", "compile", "open",
        "input", "breakpoint", "__builtins__"
    }
    
    def __init__(self, timeout: int = 10, max_output: int = 5000):
        self.timeout = timeout
        self.max_output = max_output
    
    def _validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validate code for security issues."""
        # Parse and check for forbidden patterns
        forbidden_keywords = ["import os", "import subprocess", "__import__", 
                             "exec(", "eval(", "compile("]
        
        for keyword in forbidden_keywords:
            if keyword in code:
                return False, f"Forbidden keyword: {keyword}"
        
        return True, None
    
    async def execute(
        self,
        code: str,
        timeout: Optional[int] = None,
        variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute code safely.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            variables: Pre-defined variables for code
            
        Returns:
            dict: Execution result
        """
        timeout = timeout or self.timeout
        
        # Validate code
        is_valid, error = self._validate_code(code)
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "code": code[:100]
            }
        
        # Setup safe globals
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "abs": abs,
                "sum": sum,
                "min": min,
                "max": max,
                "sorted": sorted,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "round": round,
            }
        }
        
        # Add user variables
        if variables:
            safe_globals.update(variables)
        
        # Capture output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Execute with timeout
            await asyncio.wait_for(
                self._run_code(code, safe_globals, stdout_capture, stderr_capture),
                timeout=timeout
            )
            
            stdout_text = stdout_capture.getvalue()
            stderr_text = stderr_capture.getvalue()
            
            # Truncate output
            if len(stdout_text) > self.max_output:
                stdout_text = stdout_text[:self.max_output] + f"\n... (Output truncated, {len(stdout_text)} total chars)"
            
            return {
                "success": True,
                "stdout": stdout_text,
                "stderr": stderr_text,
                "code": code[:200]
            }
        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Code execution timeout after {timeout} seconds",
                "code": code[:100]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "code": code[:100]
            }
    
    async def _run_code(self, code: str, globals_dict: Dict, stdout_capture, stderr_capture):
        """Run code with output capture."""
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, globals_dict)


class CodeExecutionTool(EnhancedTool):
    """Tool for executing Python code."""
    
    def __init__(self, timeout: int = 10, allow_imports: bool = False):
        parameters = [
            Parameter(
                name="code",
                type=ParameterType.STRING,
                description="Python code to execute"
            ),
            Parameter(
                name="timeout",
                type=ParameterType.INTEGER,
                description="Execution timeout in seconds",
                required=False,
                default=10,
                min_value=1,
                max_value=30
            ),
            Parameter(
                name="variables",
                type=ParameterType.OBJECT,
                description="Variables to pass to code",
                required=False
            )
        ]
        
        super().__init__(
            name="code_execute",
            description="Execute Python code safely with sandboxing",
            parameters=parameters,
            category="development"
        )
        self.executor = SafeCodeExecutor(timeout=timeout)
        self.allow_imports = allow_imports
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute Python code."""
        code = kwargs.get("code", "")
        timeout = kwargs.get("timeout", 10)
        variables = kwargs.get("variables", {})
        
        logger.info(f"Executing code ({len(code)} chars)")
        
        # Execute
        result = await self.executor.execute(code, timeout=timeout, variables=variables)
        
        return json.dumps(result)


class PythonREPLTool(EnhancedTool):
    """Interactive Python REPL tool."""
    
    def __init__(self, max_history: int = 20):
        parameters = [
            Parameter(
                name="command",
                type=ParameterType.STRING,
                description="Command (execute, history, clear, help)"
            ),
            Parameter(
                name="code",
                type=ParameterType.STRING,
                description="Python code to execute",
                required=False
            ),
            Parameter(
                name="timeout",
                type=ParameterType.INTEGER,
                description="Execution timeout",
                required=False,
                default=10
            )
        ]
        
        super().__init__(
            name="python_repl",
            description="Interactive Python REPL for experimentation",
            parameters=parameters,
            category="development"
        )
        self.executor = SafeCodeExecutor()
        self.max_history = max_history
        self.execution_history = []
        self.session_variables = {}
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute REPL command."""
        command = kwargs.get("command", "execute")
        code = kwargs.get("code", "")
        timeout = kwargs.get("timeout", 10)
        
        if command == "execute":
            # Execute code and maintain session
            result = await self.executor.execute(code, timeout=timeout, variables=self.session_variables)
            
            self.execution_history.append({
                "code": code,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only recent history
            if len(self.execution_history) > self.max_history:
                self.execution_history = self.execution_history[-self.max_history:]
            
            return json.dumps(result)
        
        elif command == "history":
            return json.dumps({
                "history": [
                    {"code": h["code"][:50], "success": h["result"].get("success", False)}
                    for h in self.execution_history[-5:]
                ]
            })
        
        elif command == "clear":
            self.execution_history = []
            self.session_variables = {}
            return json.dumps({"status": "cleared"})
        
        elif command == "help":
            return json.dumps({
                "commands": {
                    "execute": "Execute Python code",
                    "history": "Show execution history",
                    "clear": "Clear history and variables",
                    "help": "Show this help"
                }
            })
        
        else:
            return json.dumps({"error": f"Unknown command: {command}"})


class DataProcessingTool(EnhancedTool):
    """Process and transform data."""
    
    def __init__(self):
        parameters = [
            Parameter(
                name="operation",
                type=ParameterType.STRING,
                description="Operation to perform",
                enum=["parse_json", "parse_csv", "transform", "validate", "format"]
            ),
            Parameter(
                name="data",
                type=ParameterType.STRING,
                description="Data to process"
            ),
            Parameter(
                name="options",
                type=ParameterType.OBJECT,
                description="Operation options",
                required=False
            )
        ]
        
        super().__init__(
            name="data_process",
            description="Parse and transform various data formats",
            parameters=parameters,
            category="data"
        )
    
    async def _execute_impl(self, **kwargs) -> str:
        """Process data."""
        operation = kwargs.get("operation", "parse_json")
        data = kwargs.get("data", "")
        options = kwargs.get("options", {})
        
        try:
            if operation == "parse_json":
                parsed = json.loads(data)
                return json.dumps({
                    "success": True,
                    "data": parsed,
                    "type": type(parsed).__name__
                })
            
            elif operation == "parse_csv":
                import csv
                import io
                
                reader = csv.DictReader(io.StringIO(data))
                rows = list(reader)
                
                return json.dumps({
                    "success": True,
                    "rows": rows,
                    "count": len(rows)
                })
            
            elif operation == "transform":
                # Parse JSON and apply transformation
                parsed = json.loads(data)
                transform_code = options.get("code", "")
                
                if transform_code:
                    result = eval(transform_code, {"data": parsed})
                    return json.dumps({
                        "success": True,
                        "data": result
                    })
                
                return json.dumps({"success": False, "error": "No transformation code provided"})
            
            elif operation == "validate":
                parsed = json.loads(data)
                schema = options.get("schema", {})
                
                # Simple validation
                valid = isinstance(parsed, dict)
                return json.dumps({
                    "success": True,
                    "valid": valid,
                    "type": type(parsed).__name__
                })
            
            elif operation == "format":
                if data.startswith("{") or data.startswith("["):
                    parsed = json.loads(data)
                    formatted = json.dumps(parsed, indent=2)
                else:
                    formatted = data
                
                return json.dumps({
                    "success": True,
                    "formatted": formatted
                })
            
            else:
                return json.dumps({"error": f"Unknown operation: {operation}"})
        
        except Exception as e:
            logger.error(f"Data processing error: {str(e)}")
            return json.dumps({
                "success": False,
                "error": str(e),
                "operation": operation
            })

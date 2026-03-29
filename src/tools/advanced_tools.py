"""Powerful advanced tools for sophisticated agent tasks."""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, Optional, List
from pathlib import Path
import aiohttp
import base64

from src.tools.function_calling import EnhancedTool, Parameter, ParameterType

logger = logging.getLogger(__name__)


class WebSearchTool(EnhancedTool):
    """Advanced web search with multiple API support."""
    
    def __init__(self, api_key: Optional[str] = None, provider: str = "duckduckgo"):
        parameters = [
            Parameter(
                name="query",
                type=ParameterType.STRING,
                description="Search query",
                required=True
            ),
            Parameter(
                name="num_results",
                type=ParameterType.INTEGER,
                description="Number of results",
                required=False,
                default=5,
                min_value=1,
                max_value=20
            ),
            Parameter(
                name="max_attempts",
                type=ParameterType.INTEGER,
                description="Max retry attempts",
                required=False,
                default=3,
                min_value=1,
                max_value=5
            )
        ]
        
        super().__init__(
            name="web_search",
            description="Search the web with advanced options (DuckDuckGo, SerpAPI, Bing)",
            parameters=parameters,
            category="research"
        )
        self.api_key = api_key
        self.provider = provider
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute web search."""
        query = kwargs.get("query", "")
        num_results = kwargs.get("num_results", 5)
        max_attempts = kwargs.get("max_attempts", 3)
        
        logger.info(f"Searching: {query} (provider: {self.provider})")
        
        for attempt in range(max_attempts):
            try:
                if self.provider == "duckduckgo":
                    return await self._search_duckduckgo(query, num_results)
                elif self.provider == "serpapi" and self.api_key:
                    return await self._search_serpapi(query, num_results)
                else:
                    return await self._search_duckduckgo(query, num_results)
            except Exception as e:
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)
                    continue
                logger.error(f"Search failed: {str(e)}")
                return json.dumps({
                    "error": f"Search failed after {max_attempts} attempts: {str(e)}",
                    "query": query
                })
        
        return json.dumps({"error": "Search exhausted all attempts"})
    
    async def _search_duckduckgo(self, query: str, limit: int) -> str:
        """Search using DuckDuckGo instant API (no key needed)."""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "t": "clawagent"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        results = []
                        
                        # Add definition if available
                        if data.get("Definition"):
                            results.append({
                                "title": "Definition",
                                "snippet": data["Definition"]
                            })
                        
                        # Add related topics
                        for topic in data.get("RelatedTopics", [])[:limit-1]:
                            if isinstance(topic, dict) and "Text" in topic:
                                results.append({
                                    "title": topic.get("FirstURL", ""),
                                    "snippet": topic["Text"][:200]
                                })
                        
                        return json.dumps({
                            "query": query,
                            "results": results[:limit],
                            "count": len(results),
                            "provider": "duckduckgo"
                        })
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
        
        return json.dumps({"error": str(e), "query": query})
    
    async def _search_serpapi(self, query: str, limit: int) -> str:
        """Search using SerpAPI (requires API key)."""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        results = data.get("organic_results", [])
                        
                        formatted = [
                            {
                                "title": r.get("title", ""),
                                "url": r.get("link", ""),
                                "snippet": r.get("snippet", "")
                            }
                            for r in results[:limit]
                        ]
                        
                        return json.dumps({
                            "query": query,
                            "results": formatted,
                            "count": len(formatted),
                            "provider": "serpapi"
                        })
        except Exception as e:
            logger.error(f"SerpAPI error: {str(e)}")
        
        return json.dumps({"error": str(e), "query": query})


class FileSystemTool(EnhancedTool):
    """Advanced file system operations."""
    
    def __init__(self, safe_root: str = "./", allow_write: bool = True):
        parameters = [
            Parameter(
                name="operation",
                type=ParameterType.STRING,
                description="Operation to perform",
                required=True,
                enum=["read", "write", "list", "delete", "create_dir", "exists"]
            ),
            Parameter(
                name="path",
                type=ParameterType.STRING,
                description="File or directory path",
                required=True
            ),
            Parameter(
                name="content",
                type=ParameterType.STRING,
                description="Content to write (for write operation)",
                required=False
            ),
            Parameter(
                name="encoding",
                type=ParameterType.STRING,
                description="File encoding",
                required=False,
                default="utf-8"
            ),
            Parameter(
                name="max_size",
                type=ParameterType.INTEGER,
                description="Max file size in bytes",
                required=False,
                default=1000000,
                min_value=1000
            )
        ]
        
        super().__init__(
            name="filesystem",
            description="Advanced file system operations with safety checks",
            parameters=parameters,
            category="system"
        )
        self.safe_root = Path(safe_root)
        self.allow_write = allow_write
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute file system operation."""
        operation = kwargs.get("operation", "")
        path_str = kwargs.get("path", "")
        
        try:
            path = self._validate_path(path_str)
            
            if operation == "read":
                return await self._read_file(path, kwargs.get("encoding", "utf-8"), 
                                           kwargs.get("max_size", 1000000))
            
            elif operation == "write":
                if not self.allow_write:
                    return json.dumps({"error": "Write operations disabled"})
                
                content = kwargs.get("content", "")
                return await self._write_file(path, content, kwargs.get("encoding", "utf-8"))
            
            elif operation == "list":
                return await self._list_directory(path)
            
            elif operation == "delete":
                if not self.allow_write:
                    return json.dumps({"error": "Delete operations disabled"})
                
                return await self._delete(path)
            
            elif operation == "create_dir":
                if not self.allow_write:
                    return json.dumps({"error": "Create operations disabled"})
                
                return await self._create_directory(path)
            
            elif operation == "exists":
                return json.dumps({"exists": path.exists(), "path": str(path)})
            
            else:
                return json.dumps({"error": f"Unknown operation: {operation}"})
        
        except Exception as e:
            logger.error(f"File system operation error: {str(e)}")
            return json.dumps({"error": str(e), "operation": operation})
    
    def _validate_path(self, path_str: str) -> Path:
        """Validate path is within safe root."""
        path = Path(path_str).resolve()
        
        # Security check: ensure path is within safe root
        try:
            path.relative_to(self.safe_root.resolve())
        except ValueError:
            raise ValueError(f"Path {path} is outside safe root")
        
        return path
    
    async def _read_file(self, path: Path, encoding: str, max_size: int) -> str:
        """Read file with size limit."""
        if not path.exists():
            return json.dumps({"error": "File not found"})
        
        if path.stat().st_size > max_size:
            return json.dumps({"error": f"File too large (max {max_size} bytes)"})
        
        try:
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
            
            return json.dumps({
                "path": str(path),
                "content": content,
                "size": len(content),
                "encoding": encoding
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _write_file(self, path: Path, content: str, encoding: str) -> str:
        """Write file safely."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, "w", encoding=encoding) as f:
                f.write(content)
            
            logger.info(f"Written {len(content)} bytes to {path}")
            
            return json.dumps({
                "status": "success",
                "path": str(path),
                "size": len(content)
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _list_directory(self, path: Path) -> str:
        """List directory contents."""
        if not path.is_dir():
            return json.dumps({"error": "Not a directory"})
        
        try:
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return json.dumps({
                "path": str(path),
                "items": items,
                "count": len(items)
            })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _delete(self, path: Path) -> str:
        """Delete file or empty directory."""
        try:
            if path.is_file():
                path.unlink()
                return json.dumps({"status": "deleted", "path": str(path)})
            elif path.is_dir():
                if list(path.iterdir()):
                    return json.dumps({"error": "Directory not empty"})
                path.rmdir()
                return json.dumps({"status": "deleted", "path": str(path)})
            else:
                return json.dumps({"error": "Path not found"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    async def _create_directory(self, path: Path) -> str:
        """Create directory."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return json.dumps({"status": "created", "path": str(path)})
        except Exception as e:
            return json.dumps({"error": str(e)})


class DataAnalysisTool(EnhancedTool):
    """Data analysis and processing tool."""
    
    def __init__(self):
        parameters = [
            Parameter(
                name="operation",
                type=ParameterType.STRING,
                description="Analysis operation",
                required=True,
                enum=["describe", "correlate", "aggregate", "filter", "sort"]
            ),
            Parameter(
                name="data",
                type=ParameterType.OBJECT,
                description="Data to analyze"
            ),
            Parameter(
                name="column",
                type=ParameterType.STRING,
                description="Column to analyze"
            ),
            Parameter(
                name="operation_params",
                type=ParameterType.OBJECT,
                description="Operation specific parameters",
                required=False
            )
        ]
        
        super().__init__(
            name="data_analysis",
            description="Statistical analysis and data processing",
            parameters=parameters,
            category="analysis"
        )
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute data analysis."""
        try:
            import numpy as np
            from scipy import stats
            
            operation = kwargs.get("operation", "")
            data = kwargs.get("data", [])
            
            if isinstance(data, dict):
                data = list(data.values())[0] if data else []
            
            if operation == "describe":
                return json.dumps({
                    "count": len(data),
                    "mean": float(np.mean(data)) if data else 0,
                    "median": float(np.median(data)) if data else 0,
                    "std": float(np.std(data)) if data else 0,
                    "min": float(np.min(data)) if data else 0,
                    "max": float(np.max(data)) if data else 0
                })
            
            elif operation == "filter":
                params = kwargs.get("operation_params", {})
                threshold = params.get("threshold", 0)
                filtered = [x for x in data if x > threshold]
                return json.dumps({"filtered": filtered, "count": len(filtered)})
            
            else:
                return json.dumps({"error": f"Unknown operation: {operation}"})
        
        except ImportError:
            return json.dumps({"error": "NumPy/SciPy not available"})
        except Exception as e:
            return json.dumps({"error": str(e)})


class CommandExecutionTool(EnhancedTool):
    """Execute system commands safely."""
    
    def __init__(self, timeout: int = 30, allowed_commands: Optional[List[str]] = None):
        parameters = [
            Parameter(
                name="command",
                type=ParameterType.STRING,
                description="Command to execute"
            ),
            Parameter(
                name="timeout",
                type=ParameterType.INTEGER,
                description="Execution timeout in seconds",
                required=False,
                default=10,
                min_value=1,
                max_value=60
            ),
            Parameter(
                name="cwd",
                type=ParameterType.STRING,
                description="Current working directory",
                required=False
            )
        ]
        
        super().__init__(
            name="cmd_execute",
            description="Execute system commands with timeout and access control",
            parameters=parameters,
            category="system"
        )
        self.timeout = timeout
        self.allowed_commands = allowed_commands
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute command."""
        command = kwargs.get("command", "")
        timeout = kwargs.get("timeout", 10)
        cwd = kwargs.get("cwd")
        
        # Security: check if command is allowed
        if self.allowed_commands:
            cmd_name = command.split()[0] if command else ""
            if cmd_name not in self.allowed_commands:
                return json.dumps({
                    "error": f"Command '{cmd_name}' not allowed",
                    "allowed": self.allowed_commands
                })
        
        try:
            logger.info(f"Executing command: {command}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                return json.dumps({
                    "error": f"Command timed out after {timeout} seconds",
                    "command": command
                })
            
            return json.dumps({
                "command": command,
                "returncode": process.returncode,
                "stdout": stdout.decode("utf-8", errors="ignore"),
                "stderr": stderr.decode("utf-8", errors="ignore")
            })
        
        except Exception as e:
            logger.error(f"Command execution error: {str(e)}")
            return json.dumps({"error": str(e), "command": command})


class APICallTool(EnhancedTool):
    """Make HTTP API calls."""
    
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type=ParameterType.STRING,
                description="API endpoint URL"
            ),
            Parameter(
                name="method",
                type=ParameterType.STRING,
                description="HTTP method",
                required=False,
                default="GET",
                enum=["GET", "POST", "PUT", "DELETE", "PATCH"]
            ),
            Parameter(
                name="data",
                type=ParameterType.OBJECT,
                description="Request body/parameters"
            ),
            Parameter(
                name="headers",
                type=ParameterType.OBJECT,
                description="HTTP headers",
                required=False
            ),
            Parameter(
                name="timeout",
                type=ParameterType.INTEGER,
                description="Request timeout in seconds",
                required=False,
                default=10
            )
        ]
        
        super().__init__(
            name="api_call",
            description="Make HTTP API requests",
            parameters=parameters,
            category="api"
        )
    
    async def _execute_impl(self, **kwargs) -> str:
        """Execute API call."""
        url = kwargs.get("url", "")
        method = kwargs.get("method", "GET")
        data = kwargs.get("data", {})
        headers = kwargs.get("headers", {})
        timeout = kwargs.get("timeout", 10)
        
        try:
            logger.info(f"API call: {method} {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data if method != "GET" else None,
                    params=data if method == "GET" else None,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    response_text = await resp.text()
                    
                    try:
                        json_data = json.loads(response_text)
                    except:
                        json_data = None
                    
                    return json.dumps({
                        "status_code": resp.status,
                        "url": url,
                        "method": method,
                        "data": json_data or response_text[:500],
                        "headers": dict(resp.headers)
                    })
        
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            return json.dumps({"error": str(e), "url": url})

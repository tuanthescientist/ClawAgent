# ClawAgent v3.0 - Tools System Architecture

## Overview

ClawAgent v3.0 provides a flexible tool system with 6-8 powerful built-in tools, expandable to unlimited custom tools.

## Built-in Tools

### 1. Web Browser Tool 🌐

**Purpose**: Browse websites, extract content, take screenshots

**Implementation**: `src/tools/web_browser.py` (200 lines)
**Dependencies**: Playwright, BeautifulSoup4

**Usage**:
```python
web_browser = WebBrowserTool(
    headless=True,
    timeout=30,
    max_tabs=5,
)

# Navigate and scrape
content = await web_browser.navigate("https://example.com")
content = await web_browser.extract_text()
screenshot = await web_browser.take_screenshot()
```

**API**:
```
- navigate(url: str) -> str  # Load page, return HTML
- extract_text() -> str      # Get page text
- take_screenshot() -> bytes # PNG screenshot
- find_element(selector: str) -> str
- click_element(selector: str) -> bool
- fill_input(selector: str, text: str) -> bool
- submit_form(selector: str) -> bool
```

**Example**:
```python
# Search and scrape results
await tool.navigate("https://www.google.com")
await tool.fill_input('input[name="q"]', "machine learning")
await tool.click_element('input[value="Google Search"]')
results = await tool.extract_text()
```

---

### 2. Image Generation Tool 🎨

**Purpose**: Generate images with local models (Flux.1, Stable Diffusion)

**Implementation**: `src/tools/image_generation.py` (200 lines)
**Dependencies**: Pillow, torch (optional), diffusers

**Usage**:
```python
image_gen = ImageGenerationTool(
    model="stable-diffusion-v2",  # or flux.1, sd-xl
    device="cuda",  # or cpu
    output_dir="./outputs/images",
)

# Generate image
image_path = await image_gen.generate(
    prompt="A beautiful sunset over mountains",
    num_inference_steps=50,
    guidance_scale=7.5,
)

# Edit image
edited = await image_gen.edit(
    image_path=image_path,
    prompt="Make it more vibrant",
)
```

**API**:
```
- generate(prompt: str, num_steps: int, guidance: float) -> str
- edit(image_path: str, prompt: str, mask: str) -> str
- vary(image_path: str) -> str
- set_seed(seed: int) -> None
```

**Example**:
```python
# Create multiple variations
paths = []
for i in range(3):
    path = await tool.generate("A robot painting")
    paths.append(path)
```

---

### 3. Database Query Tool 🗄️

**Purpose**: Execute SQL queries against databases

**Implementation**: `src/tools/database_query.py` (250 lines)
**Dependencies**: SQLAlchemy, psycopg2 (PostgreSQL)

**Usage**:
```python
db_tool = DatabaseQueryTool(
    database_url="postgresql://user:pass@localhost/dbname",
    readonly=True,  # Restrict to SELECT only
    max_result_rows=1000,
)

# Query
results = await db_tool.query("SELECT * FROM users WHERE age > 25")

# Safe parameterized query
results = await db_tool.query_safe(
    "SELECT * FROM users WHERE name = ?",
    params=["John"]
)
```

**API**:
```
- query(sql: str) -> List[Dict]        # Execute query
- query_safe(sql: str, params) -> List[Dict]  # Parameterized
- insert(table: str, data: Dict) -> int
- update(table: str, data: Dict, where: str) -> int
- delete(table: str, where: str) -> int
- list_tables() -> List[str]
- get_schema(table: str) -> Dict
```

**Example**:
```python
# Get user data
results = await tool.query_safe(
    "SELECT id, name, email FROM users WHERE active = ?",
    params=[True]
)

# Count results
for row in results:
    print(f"{row['name']}: {row['email']}")
```

---

### 4. Advanced Filesystem Tool 📁

**Purpose**: Safe file system operations with restrictions

**Implementation**: `src/tools/advanced_filesystem.py` (250 lines)

**Usage**:
```python
fs_tool = AdvancedFilesystemTool(
    root_dir="./workspace",
    restricted=True,  # Can't escape root
    max_file_size=10*1024*1024,  # 10MB
    allowed_extensions=[".txt", ".md", ".py", ".json"],
)

# Read file
content = await fs_tool.read_file("data.json")

# Write file
await fs_tool.write_file("output.txt", "Hello world")

# Search files
files = await fs_tool.find_files("*.py", contains="import")
```

**API**:
```
- read_file(path: str) -> str
- write_file(path: str, content: str) -> bool
- append_file(path: str, content: str) -> bool
- delete_file(path: str) -> bool
- list_directory(path: str) -> List[Dict]
- find_files(pattern: str, contains: str) -> List[str]
- get_file_info(path: str) -> Dict
- create_directory(path: str) -> bool
```

**Example**:
```python
# Find all Python files
py_files = await tool.find_files("*.py")

# Read and process
for file in py_files:
    content = await tool.read_file(file)
    if "def main" in content:
        print(f"Found main in {file}")
```

---

### 5. Sandbox Shell Tool 🔧

**Purpose**: Execute shell commands safely in sandbox

**Implementation**: `src/tools/sandbox_shell.py` (300 lines)
**Dependencies**: Docker or restricted Python environment

**Usage**:
```python
shell_tool = SandboxShellTool(
    sandbox_type="docker",  # or "restricted"
    timeout=30,
    max_memory_mb=512,
    allowed_commands=["python", "node", "grep", "find"],
)

# Execute command
result = await shell_tool.execute(
    command="python script.py --output json",
    input_file="data.csv",
)

output = result['stdout']
error = result['stderr']
exit_code = result['returncode']
```

**API**:
```
- execute(command: str) -> Dict
- execute_python(code: str) -> Dict
- execute_in_dir(command: str, dir: str) -> Dict
- list_allowed_commands() -> List[str]
- get_system_info() -> Dict
```

**Example**:
```python
# Run Python script
result = await tool.execute_python("""
import json
data = {"hello": "world"}
print(json.dumps(data))
""")

output = json.loads(result['stdout'])
```

---

### 6. API Orchestration Tool 🔗

**Purpose**: Chain multiple API calls with data transformation

**Implementation**: `src/tools/api_orchestration.py` (250 lines)
**Dependencies**: aiohttp, requests

**Usage**:
```python
api_tool = APIOrchestrationTool(
    timeout=30,
    max_parallel_requests=5,
    cache_ttl=3600,
)

# Call API
result = await api_tool.call(
    method="GET",
    url="https://api.example.com/users/1",
    headers={"Authorization": "Bearer token"},
)

# Chain APIs
chain_result = await api_tool.chain([
    {
        "name": "fetch_user",
        "method": "GET",
        "url": "https://api.example.com/users/1",
    },
    {
        "name": "fetch_posts",
        "method": "GET",
        "url": "https://api.example.com/users/1/posts",
    }
])
```

**API**:
```
- call(method, url, params, data, headers) -> Dict
- chain(requests: List[Dict]) -> Dict
- batch(requests: List[Dict]) -> List[Dict]
- transform(data, transformation: str) -> Any
- validate(data, schema: Dict) -> bool
```

**Example**:
```python
# Orchestrate complex flow
result = await tool.chain([
    {
        "name": "auth",
        "method": "POST",
        "url": "https://api.example.com/auth",
        "data": {"username": "user", "password": "pass"}
    },
    {
        "name": "get_data",
        "method": "GET",
        "url": "https://api.example.com/data",
        "headers": {
            "Authorization": f"Bearer {$.auth.token}"
        }
    }
])
```

---

### 7. Code Executor Tool ⚙️

**Purpose**: Safely execute Python code

**Implementation**: `src/tools/code_executor.py` (updated, 300 lines)

**Features**:
- Restricted execution (no file access by default)
- Docker sandbox support
- Time and memory limits
- Disabled by default (enable with `CODE_EXECUTION_ENABLED=true`)

**Usage** (⚠️ Requires explicit enable):
```python
code_executor = CodeExecutorTool(
    sandbox="docker",
    enabled=True,  # Only if explicitly enabled
    timeout=30,
    max_memory_mb=512,
)

result = await code_executor.execute("""
import json
numbers = [1, 2, 3, 4, 5]
print(json.dumps({
    "mean": sum(numbers) / len(numbers),
    "max": max(numbers)
}))
""")
```

---

### 8. Data Processing Tool 📊

**Purpose**: Transform and analyze data

**Implementation**: `src/tools/data_processing.py` (200 lines)
**Dependencies**: pandas, numpy, scikit-learn

**Usage**:
```python
data_tool = DataProcessingTool()

# Parse data
df = await data_tool.parse_data(
    path="data.csv",
    format="csv",
)

# Transform
df = await data_tool.transform(df, [
    {"op": "filter", "column": "age", "value": 18, "condition": ">"},
    {"op": "select", "columns": ["id", "name", "age"]},
    {"op": "groupby", "by": "city", "agg": {"age": "mean"}},
])

# Analyze
stats = await data_tool.analyze(df)
```

**API**:
```
- parse_data(path, format) -> DataFrame
- transform(df, operations) -> DataFrame
- analyze(df) -> Dict
- aggregate(df, column, by, func) -> Dict
- normalize(df, columns) -> DataFrame
```

---

## Tool Registry System

### How Tools Work

```python
from src.tools.registry import ToolsRegistry

# Create registry
registry = ToolsRegistry()

# Register built-in tools
registry.register_builtin_tools()

# Get tool
web_browser = registry.get_tool("web_browser")

# List available
tools = registry.list_tools()
```

### Create Custom Tool

```python
from src.tools.base import BaseTool

class MyCustomTool(BaseTool):
    """I do something custom"""
    
    def __init__(self, config=None):
        super().__init__("my_tool", config)
    
    async def execute(self, **kwargs):
        # Your implementation
        return {"result": "success"}

# Register
registry.register(MyCustomTool({"param": "value"}))
```

### Tool Schema for Function Calling

```python
tool_schema = registry.get_tool_schema("web_browser")
# {
#   "name": "web_browser",
#   "description": "Browse websites and extract content",
#   "parameters": {
#     "type": "object",
#     "properties": {
#       "url": {"type": "string"},
#       "action": {"type": "string", "enum": ["navigate", "extract", "screenshot"]}
#     },
#     "required": ["url"]
#   }
# }
```

---

## Integration with Agent

```python
from src.agents.advanced_claw_agent import AdvancedClawAgent
from src.tools.registry import ToolsRegistry

# Setup agent with tools
registry = ToolsRegistry()
registry.register_builtin_tools()

agent = AdvancedClawAgent(
    llm_provider=provider,
    memory=memory,
    tools=registry,
    enable_all_tools=True,
)

# Agent automatically uses tools during reasoning
response = await agent.run("What does example.com show?")
# Will use web_browser tool automatically
```

---

## Security

### Safety by Default

✅ All tools are safe:
- File access restricted to workspace
- Database queries read-only by default
- Shell commands in Docker sandbox
- API calls timeout after 30s
- Code execution disabled by default

### Enable at Risk Level

```
SAFE (Production):
- Web browser, Data processing, API orchestration
- CSV/JSON parsing, basic file reading

MEDIUM (Staging):
- Database queries, Image generation
- Advanced file system operations

RISKY (Dev Only - Disabled by default):
- Shell command execution
- Python code execution
```

---

## Performance Tips

1. **Web Browser**: Reuse same session for multiple requests
2. **Database**: Use connection pooling
3. **API**: Batch requests, use caching
4. **Filesystem**: Use async operations
5. **Code Execution**: Set reasonable timeouts

---

## Examples

See [examples/](../../examples/) for:
- `web_scraping_example.py` - Browse and extract data
- `data_analysis_example.py` - Process and analyze data
- `api_orchestration_example.py` - Chain API calls
- `image_generation_example.py` - Generate and edit images
- `database_query_example.py` - Query databases safely

---

## Contributing New Tools

To add a tool:

1. Create `src/tools/my_tool.py`
2. Inherit from `BaseTool`
3. Implement `execute()` method
4. Add schema for function calling
5. Write tests
6. Submit PR

---

## Roadmap

Future tools:
- Email sender/reader
- Slack integration
- GitHub API wrapper
- PDF processing
- Audio transcription
- Video analysis



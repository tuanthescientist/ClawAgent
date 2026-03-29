# Advanced ClawAgent Integration Guide

The ClawAgent now features a powerful **Advanced ReAct Framework** with cutting-edge tools, vector memory, and a skill system.

## 🚀 Quick Start

### Installation

```bash
# Install advanced dependencies
pip install -r requirements-advanced.txt

# Verify installation
python -c "from src.agents.advanced_claw_agent import AdvancedClawAgent; print('✓ Installation OK')"
```

### Basic Usage

```python
import asyncio
from src.agents.advanced_claw_agent import AdvancedClawAgent

async def main():
    # Create advanced agent
    agent = AdvancedClawAgent(
        name="MasterAgent",
        api_key="your-api-key",
        enable_advanced_react=True,
        enable_powerful_tools=True,
        enable_memory=True,
        verbose=True
    )
    
    # Process complex task
    result = await agent.process(
        "Analyze the sentiment of these tweets and suggest marketing strategies"
    )
    
    print(result)

asyncio.run(main())
```

## 🧠 Advanced ReAct Framework

### What is ReAct?

**ReAct** (Reasoning + Acting) is a paradigm that enables LLMs to produce reasoning trajectory and task-specific actions.

### Advanced Features

| Feature | Description |
|---------|-------------|
| **Dynamic Planning** | Agent generates plan before execution and adapts based on results |
| **Tool Integration** | Seamlessly chain multiple tools with automatic orchestration |
| **Error Recovery** | Intelligent fallback mechanisms for failed operations |
| **State Management** | Sophisticated tracking of reasoning steps and results |
| **Reasoning Traces** | Export detailed traces for analysis and debugging |

### Usage Example

```python
# For complex reasoning tasks
agent = AdvancedClawAgent(
    name="ResearchBot",
    enable_advanced_react=True,
    max_iterations=20
)

# Automatically uses Advanced ReAct for complex queries
response = await agent.process("""
    Design a comprehensive marketing strategy for a SaaS product.
    Break down the analysis into:
    1. Market research
    2. Competitive analysis
    3. Target audience identification
    4. Channel strategy
    5. Metrics for success
""")
```

## 🛠️ Powerful Tools

### Available Tools

```
Tool Name              Description                        Security
─────────────────────────────────────────────────────────────────────────
WebSearchTool         Search web with DuckDuckGo          ✓ Safe
FileSystemTool        Read/write files (sandboxed)        ⚠️ Use carefully
DataAnalysisTool      Pandas/statistical analysis         ✓ Safe
APICallTool           Make HTTP requests                  ⚠️ Validate URLs
CommandExecutionTool  Run approved shell commands         ⚠️ Restricted list
PythonREPLTool        Execute Python interactively        ⚠️ Use carefully
CodeExecutionTool     Execute Python code (DANGER!)       ⚠️ DISABLED by default
```

### Using Tools

```python
# Tools are automatically available in ReAct
# Agent will call them when needed

agent = AdvancedClawAgent(
    name="DataEngineer",
    enable_powerful_tools=True,
    enable_code_execution=False  # Keep disabled!
)

# Agent will automatically use tools for:
# - Data analysis (DataAnalysisTool)
# - File operations (FileSystemTool)
# - API calls (APICallTool)
response = await agent.process(
    "Fetch stock prices from the NYSE API and analyze trends"
)
```

### Custom Tool Integration

```python
from src.tools.advanced_tools import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="What this tool does",
            parameters={"query": {"type": "string"}}
        )
    
    async def execute(self, **kwargs):
        # Implementation
        return result

# Register with agent
agent.tools_agent.register_tool(CustomTool())
```

## 💾 Vector Memory System

### Capabilities

- **Semantic Search**: Find relevant past experiences using embeddings
- **Persistent Storage**: Long-term memory across sessions
- **Contextual Retrieval**: Automatically provide relevant context to LLM

### Usage

```python
# Enable memory (automatic retrieval & storage)
agent = AdvancedClawAgent(
    enable_memory=True
)

# Memory automatically:
# 1. Stores learning from each interaction
# 2. Retrieves relevant context for new queries
# 3. Improves responses over time

# Manual memory operations
if agent.vector_memory:
    # Add memory
    await agent.vector_memory.add_memory(
        content="User prefers JSON output format",
        memory_type="preference",
        metadata={"user": "john"}
    )
    
    # Query memory
    context = await agent.vector_memory.get_context(
        "output format preferences",
        max_results=3
    )
    
    # Stats
    stats = agent.vector_memory.get_stats()
```

## 🎓 Skill System

### Built-in Skills

Skills enhance system prompts with domain-specific expertise:

```
Skill Category          Description
──────────────────────────────────────────────────────
code_generation        Best practices for writing code
data_analysis           Data science techniques
writing                 Professional writing guidelines
problem_solving        Systematic problem-solving approach
research               Information synthesis methodology
```

### Adding Custom Skills

```python
from src.agents.skill_system import Skill

skill = Skill(
    name="financial_analysis",
    category="analysis",
    system_prompt="""You are a financial analyst expert...
    - Consider market conditions
    - Analyze historical trends
    - Evaluate risk factors
    """,
    keywords=["finance", "investment", "portfolio"]
)

if agent.skill_library:
    agent.skill_library.add_skill(skill)
```

### Skill Activation

Skills are automatically activated based on query relevance:

```python
# This query will activate coding and problem-solving skills
response = await agent.process(
    "Write an efficient algorithm to solve the two-sum problem"
)
```

## 📊 Monitoring & Statistics

### Getting Agent Statistics

```python
stats = agent.get_statistics()

print(f"Messages processed: {stats['messages_processed']}")
print(f"Reasoning loops: {stats['reasoning_loops']}")
print(f"Tools executed: {stats['tools_executed']}")
print(f"Available tools: {stats['available_tools']}")
```

### Analyzing Reasoning Traces

```python
# View last reasoning loop
if agent.reasoning_loops:
    last_loop = agent.reasoning_loops[-1]
    
    # Get visual trace
    print(last_loop.get_visual_trace())
    
    # Get summary
    summary = last_loop.get_summary()
    print(f"Steps: {summary['total_steps']}")
    print(f"Tools used: {summary['tools_used']}")
    print(f"Reasoning time: {summary['total_time']}ms")
    
    # Export trace
    last_loop.export_trace("trace.json", format="json")
    last_loop.export_trace("trace.md", format="markdown")

# Export all traces
agent.export_reasoning_traces("./traces")
```

## ⚠️ Security Considerations

### Code Execution (DISABLED BY DEFAULT)

```python
# ⚠️ DISABLE FOR UNTRUSTED INPUTS
agent = AdvancedClawAgent(
    enable_code_execution=False  # Default: False
)

# Only enable for trusted environments
# agent = AdvancedClawAgent(enable_code_execution=True)
```

### Safe FileSystem Access

```python
# FileSystemTool is sandboxed to safe_root
from src.tools.advanced_tools import FileSystemTool

tool = FileSystemTool(
    safe_root="./data",        # Only access files here
    allow_write=True,          # Allow write operations
    blocked_paths=["/etc", "/sys"]
)
```

### API Call Validation

```python
# APICallTool validates URLs
from src.tools.advanced_tools import APICallTool

tool = APICallTool(
    timeout=10,
    allowed_domains=["api.example.com", "data.openai.com"],
    max_response_size=100000
)
```

## 🔄 Architecture Overview

```
User Input
    ↓
[Should use Advanced ReAct?]
    ├─→ YES → Advanced ReAct Loop
    │         ├→ Understand
    │         ├→ Plan
    │         ├→ Execute Tools
    │         ├→ Observe
    │         ├→ Reason
    │         └→ Repeat until solution
    │
    └─→ NO  → Simple Processing
              ├→ Retrieve Memory Context
              ├→ Activate Relevant Skills
              ├→ Call LLM with tools
              └→ Return response

Response → Store in Memory → Return to User
```

## 📁 File Structure

```
src/agents/
├── advanced_claw_agent.py      # Main advanced agent
├── react_advanced.py            # Advanced ReAct implementation
├── skill_system.py              # Skill library
└── function_calling.py          # Tool orchestration

src/tools/
├── advanced_tools.py            # Powerful tools
├── code_executor.py             # Code execution
└── function_calling.py          # Function calling

src/utils/
├── vector_memory.py             # Vector memory system
└── embeddings/                  # Embedding models
```

## 🧪 Examples

See `examples_advanced_react_tools.py` for:

- Marketing strategy analysis
- Data pipeline design
- Code review and optimization
- Research paper summarization
- System architecture design
- Multi-tool orchestration

## 🐛 Troubleshooting

### Tools Not Available

```python
# Verify tools initialization
if agent.tools_agent:
    print("Available tools:", list(agent.tools_agent.tools.keys()))
else:
    print("Tools not initialized - enable_powerful_tools=True")
```

### Memory Not Working

```python
# Check if vector memory initialized
try:
    if agent.vector_memory:
        stats = agent.vector_memory.get_stats()
        print(f"Memory stats: {stats}")
except Exception as e:
    print(f"Memory error: {e}")
```

### Advanced ReAct Not Used

```python
# Check reasoning determination
user_input = "Your query here"
should_use = agent._should_use_advanced_react(user_input)
print(f"Should use Advanced ReAct: {should_use}")

# Indicators for triggering Advanced ReAct:
# - Contains keywords: analyze, break down, design, plan, etc.
# - Query longer than 150 characters
# - Multiple questions (>1 question mark)
```

## 📚 Advanced Configuration

### Full Configuration Example

```python
agent = AdvancedClawAgent(
    name="AdvancedBot",
    api_key="your-key",
    model="gpt-4",
    
    # Feature flags
    enable_advanced_react=True,
    enable_powerful_tools=True,
    enable_code_execution=False,  # ⚠️ Dangerous
    enable_memory=True,
    enable_skills=True,
    
    # Performance
    max_iterations=20,
    
    # Logging
    verbose=True
)
```

### Using Local LLMs

```python
agent = AdvancedClawAgent(
    name="LocalBot",
    enable_local_llm=True,
    local_llm_url="http://localhost:11434",
    enable_advanced_react=True
)
```

## 🎯 Best Practices

1. **Start Simple**: Enable features incrementally
2. **Monitor Resources**: Watch memory and CPU usage
3. **Test Tools**: Verify tool execution in sandbox first
4. **Limit Iterations**: Keep max_iterations reasonable (10-20)
5. **Check Traces**: Export reasoning traces for analysis
6. **Validate Memory**: Periodically review stored memories
7. **Update Skills**: Add skills for your use cases
8. **Security First**: Keep code_execution disabled

## 📖 Next Steps

1. Try [examples_advanced_react_tools.py](examples_advanced_react_tools.py)
2. Customize skills for your domain
3. Add custom tools
4. Monitor reasoning traces
5. Optimize with performance profiling

---

**Advanced ClawAgent** - Enterprise-grade AI agents with human-like reasoning.

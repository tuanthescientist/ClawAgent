# 🚀 Advanced ClawAgent v2.0 - Quick Reference

**Last Updated**: 2024-01-16  
**Status**: Production Ready ✅

## ⚡ 30-Second Start

```python
from src.agents.advanced_claw_agent import AdvancedClawAgent
import asyncio

async def main():
    agent = AdvancedClawAgent(name="Bot", api_key="sk-...")
    result = await agent.process("Your question here")
    print(result)

asyncio.run(main())
```

## 📦 Installation

```bash
pip install -r requirements-advanced.txt
```

## 🎯 Three Usage Modes

### Mode 1: Simple (Default)
Best for: Quick answers, simple queries
```python
agent = AdvancedClawAgent(name="SimpleBot")
result = await agent.process("What is AI?")
```

### Mode 2: Advanced ReAct (Auto)
Best for: Complex queries, multi-step reasoning
```python
agent = AdvancedClawAgent(
    name="ReasoningBot",
    enable_advanced_react=True
)
# Automatically routes complex queries to ReAct
result = await agent.process("Design a complete marketing strategy...")
```

### Mode 3: Full Power
Best for: Data analysis, system design, research
```python
agent = AdvancedClawAgent(
    name="MasterBot",
    enable_advanced_react=True,
    enable_powerful_tools=True,
    enable_memory=True,
    enable_skills=True
)
result = await agent.process("Analyze this dataset and optimize...")
```

## 🛠️ Available Tools

| Tool | When to Use | Example |
|------|------------|---------|
| **WebSearch** | Find information | "Search for latest AI trends" |
| **FileSystem** | Read/write files | "Load and analyze data.csv" |
| **DataAnalysis** | Statistics | "Calculate correlation matrix" |
| **APICall** | External data | "Fetch from REST API" |
| **Command** | Run scripts | "Install python package" |
| **CodeRun** | Execute Python | "Run Python code snippet" |

## 💾 Enable/Disable Features

```python
agent = AdvancedClawAgent(
    name="Bot",
    enable_advanced_react=True,      # Complex reasoning (default: True)
    enable_powerful_tools=True,       # All tools (default: True)
    enable_code_execution=False,      # ⚠️ Python code (default: False)
    enable_memory=True,               # Remember context (default: True)
    enable_skills=True,               # Domain expertise (default: True)
)
```

## 📊 Monitor Performance

```python
# Get statistics
stats = agent.get_statistics()
print(f"Messages: {stats['messages_processed']}")
print(f"Tools used: {stats['available_tools']}")

# Export reasoning
if agent.reasoning_loops:
    agent.export_reasoning_traces("./traces")
```

## 🧠 What Triggers Advanced ReAct?

Query gets Advanced ReAct if it:
- ✅ Contains keywords: "analyze", "design", "break down", "step by step"
- ✅ Is longer than 150 characters
- ✅ Has multiple questions (>1 question mark)

Example: "Analyze market trends and suggest 3 strategies" → ReAct

## 🎓 Adding Custom Skills

```python
from src.agents.skill_system import Skill

my_skill = Skill(
    name="finance",
    category="analysis",
    system_prompt="You are a financial expert...",
    keywords=["finance", "investment"]
)

if agent.skill_library:
    agent.skill_library.add_skill(my_skill)
```

## 💡 5-Minute Examples

See `examples_advanced_react_tools.py`:
1. Marketing strategy analysis
2. Data pipeline design
3. Code review workflow
4. Research summarization
5. System architecture design

Run: `python examples_advanced_react_tools.py`

## ⚠️ Security Notes

✅ DO:
- Keep code execution DISABLED
- Monitor memory usage
- Validate external inputs
- Use environment variables for secrets

❌ DON'T:
- Enable code execution for untrusted input
- Store sensitive data in memory
- Expose API keys in code
- Run untrusted tool commands

## 🐛 Quick Troubleshooting

### Tools not available?
```python
if agent.tools_agent:
    print(list(agent.tools_agent.tools.keys()))
```

### Memory not working?
```python
try:
    stats = agent.vector_memory.get_stats()
except:
    print("Memory disabled or initialization failed")
```

### Not using Advanced ReAct?
```python
query = "Your query"
print(agent._should_use_advanced_react(query))
# Should be True for complex queries
```

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Overview |
| `ADVANCED_REACT_INTEGRATION.md` | Deep dive |
| `ADVANCED_STATUS.md` | Features & security |
| `examples_advanced_react_tools.py` | Working examples |
| `requirements-advanced.txt` | Dependencies |

## 🎯 Common Tasks

### Data Analysis
```python
agent = AdvancedClawAgent(enable_advanced_react=True)
result = await agent.process(
    "Analyze this CSV file and identify trends"
)
```

### Research
```python
result = await agent.process(
    "Research the latest developments in quantum computing"
)
```

### Code Review
```python
result = await agent.process(
    "Review this Python code for optimization opportunities"
)
```

### System Design
```python
result = await agent.process(
    "Design a microservices architecture for e-commerce"
)
```

## ⚙️ Configuration Examples

### Minimal
```python
agent = AdvancedClawAgent(name="Bot")
```

### Development
```python
agent = AdvancedClawAgent(
    name="DevBot",
    enable_advanced_react=True,
    verbose=True,
    max_iterations=20
)
```

### Production
```python
agent = AdvancedClawAgent(
    name="ProdBot",
    api_key="sk-...",
    enable_advanced_react=True,
    enable_powerful_tools=True,
    enable_memory=True,
    enable_skills=True,
    max_iterations=15,
    verbose=False
)
```

## 📞 Getting Help

1. **Quick Start**: See section above ⬆️
2. **Features**: Read `ADVANCED_STATUS.md`
3. **How-To**: Read `ADVANCED_REACT_INTEGRATION.md`
4. **Examples**: Run `examples_advanced_react_tools.py`
5. **API**: Check docstrings in code
6. **Troubleshooting**: See section above ⬆️

## 🚀 Next Steps

1. **Install**: `pip install -r requirements-advanced.txt`
2. **Try**: Run the examples
3. **Customize**: Add your own skills
4. **Monitor**: Watch statistics & traces
5. **Deploy**: Use in production

---

**Advanced ClawAgent v2.0** - Enterprise AI Ready! ✨

Quick links:
- [Full Integration Guide](ADVANCED_REACT_INTEGRATION.md)
- [Live Examples](examples_advanced_react_tools.py)
- [Feature Status](ADVANCED_STATUS.md)

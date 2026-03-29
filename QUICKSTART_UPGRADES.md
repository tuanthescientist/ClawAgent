# ClawAgent Upgrades - Quick Start Guide

## What Got Upgraded?

Your ClawAgent now has 5 powerful new features:

1. ✅ **Tool Calling** - Agents can use tools with proper function calling
2. ✅ **Local LLM** - Run models locally (Ollama, vLLM, LM Studio)
3. ✅ **ReAct Framework** - Reasoning loops for complex problem solving
4. ✅ **Vector Memory** - Long-term memory with semantic search
5. ✅ **Skill System** - Dynamic agent capabilities

---

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Choose Your LLM

**Option A: Use OpenAI (easiest to start)**
```bash
export OPENAI_API_KEY=sk-your-key-here
```

**Option B: Use Local LLM (Ollama)**
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Run a model
ollama run mistral
```

### Step 3: Run Examples

```bash
python examples_new_features.py
```

This will show you:
- Tool calling in action
- LLM provider support
- Skill system
- Vector memory
- ReAct framework

### Step 4: Use Enhanced Agent

```python
import asyncio
from src.agents.enhanced_openai_agent import EnhancedOpenAIAgent

async def main():
    # Create agent with all features enabled
    agent = EnhancedOpenAIAgent(
        name="SuperAgent",
        api_key="sk-...",  # or use local LLM
        enable_tools=True,
        enable_memory=True,
        enable_skills=True,
        enable_react=True  # For complex queries
    )
    
    # Use it!
    response = await agent.process(
        "Solve this complex problem: ..."
    )
    print(response)
    
    # See stats
    print(agent.get_statistics())

asyncio.run(main())
```

---

## 📚 Feature Highlights

### Tool Calling
```python
# Tools are automatically available
# When asking complex questions, the agent uses tools

response = await agent.process("Calculate 2^10 and search for facts about it")
# Agent will automatically:
# 1. Use calculator tool for 2^10
# 2. Use web search tool for facts
# 3. Combine results
```

### Vector Memory
```python
# Memory persists between sessions
# Agents learn from past conversations

response1 = await agent.process("I'm a Python developer")
# Memory learns: "User is a Python developer"

response2 = await agent.process("What's best for me?")
# Agent remembers and uses this context
```

### ReAct (Complex Reasoning)
```python
# For complex questions, agent uses reasoning loop
# Shows: Thought → Action → Observation → Reflection

response = await agent.process(
    "Break down this complex system architecture and propose improvements"
)
# Agent will show full reasoning process
```

### Skill System
```python
# Agent learns and uses skills dynamically

from src.agents.skill_system import Skill, SkillLibrary

lib = SkillLibrary()

# Add custom skill
skill = Skill(
    name="customer_support",
    description="Handle customer support tickets",
    instructions="1. Understand issue\n2. Provide solution\n3. Follow up"
)

lib.add_skill(skill)

# Agent now has this skill!
response = await agent.process("Help me with my issue")
```

---

## 🔧 Configuration (.env)

```env
# LLM Choice
OPENAI_API_KEY=sk-...              # For OpenAI
# OR
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=mistral

# Agent Features
ENABLE_REACT=true                  # Complex reasoning
ENABLE_MEMORY=true                 # Long-term memory
ENABLE_SKILLS=true                 # Skill library
ENABLE_TOOLS=true                  # Function calling

# Performance
MAX_ITERATIONS=10                  # Reasoning loop limit
TEMPERATURE=0.7                    # Creativity level
```

---

## 📊 Expected Output

When you run the agent, you'll see:

```
User: Calculate 2^10 and tell me about the number

Agent Thinking Process (ReAct):
Step 1:
Thought: User wants calculation and information
Action: Use calculator tool

Step 2:
Thought: Now get interesting facts
Action: Use web search

Step 3:
Thought: Combine results
Action: Generate response

Response: 2^10 = 1024. This is a power of 2, commonly used in computing...
```

---

## 🎯 Real-World Examples

### Example 1: Data Analysis Assistant
```python
agent = EnhancedOpenAIAgent(
    name="DataAnalyst",
    enable_tools=True,           # Use file_read, calculator
    enable_memory=True,          # Remember previous analyses
    enable_skills=True           # Use data_analysis skill
)

response = await agent.process("""
Analyze this CSV file for trends.
Look at customer data and find patterns.
""")
```

### Example 2: Code Review Assistant
```python
agent = EnhancedOpenAIAgent(
    name="CodeReviewer",
    enable_react=True,            # Complex reasoning
    enable_skills=True,           # Use code_generation skill
    enable_tools=True             # Read code files
)

response = await agent.process("""
Review my Python code for:
1. Performance issues
2. Security vulnerabilities
3. Code quality
""")
```

### Example 3: Research Assistant
```python
agent = EnhancedOpenAIAgent(
    name="Researcher",
    enable_tools=True,            # web_search tool
    enable_memory=True,           # Remember research progress
    enable_react=True             # Complex analysis
)

response = await agent.process(
    "Research the latest trends in AI and summarize findings"
)
```

---

## ⚡ Performance Tips

### For Fast Responses (Local LLM)
- Use smaller models: `mistral`, `neural-chat`
- Reduce max_iterations: `5-7`
- Disable expensive features if not needed

### For Better Quality (OpenAI)
- Use `gpt-4` model
- Enable all features: tools, memory, react, skills
- Increase max_iterations: `10-15`

### Memory Management
```python
# Get memory stats
stats = agent.vector_memory.get_stats()
print(f"Stored {stats['total_memories']} memories")

# Clear old memories if needed
if stats['total_memories'] > 1000:
    agent.vector_memory.clear()
```

---

## 🐛 Troubleshooting

### "ImportError: No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```

### "Connection refused - Ollama not running"
```bash
# Start Ollama
ollama serve

# In another terminal
ollama run mistral
```

### "OPENAI_API_KEY not found"
```bash
# Create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### Agent responses are slow
- Reduce `max_iterations`
- Use smaller local model
- Disable unnecessary features

---

## 📖 More Documentation

- **Detailed Guide**: See `UPGRADE_GUIDE.md`
- **Examples**: `examples_new_features.py`
- **API Docs**: In-code docstrings

---

## 🎓 Learning Path

1. **Start Simple**: Run examples with OpenAI
2. **Understand Tools**: Play with calculator and web search
3. **Add Memory**: See how agent learns over time
4. **Try Local LLM**: Setup Ollama and test
5. **Enable ReAct**: Watch reasoning process
6. **Master Skills**: Create custom skills
7. **Integrate All**: Build production agent

---

## 📊 Component Overview

```
EnhancedOpenAIAgent
├── Tools (FunctionCallingAgent)
│   ├── Calculator
│   ├── WebSearch
│   ├── FileRead
│   └── JSONParse
├── Memory (VectorMemory)
│   ├── Embeddings
│   └── Semantic Search
├── Skills (SkillLibrary)
│   ├── Reasoning
│   ├── WebSearch
│   └── Custom...
└── ReAct (ReActAgent)
    ├── Thought
    ├── Action
    ├── Observation
    └── Reflection
```

---

## ✅ Checklist

- [ ] Installed requirements.txt
- [ ] Set OPENAI_API_KEY OR started Ollama
- [ ] Ran examples_new_features.py
- [ ] Tried EnhancedOpenAIAgent
- [ ] Tested tool calling
- [ ] Explored memory system
- [ ] Reviewed UPGRADE_GUIDE.md
- [ ] Created first custom skill
- [ ] Enabled ReAct

---

## 🆘 Need Help?

1. Check `UPGRADE_GUIDE.md` for detailed documentation
2. Review code comments in `/src` directory
3. Run `examples_new_features.py` for working examples
4. Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🚀 Next: Integrate Into Your App

Update your existing `main.py` or FastAPI app:

```python
from src.agents.enhanced_openai_agent import EnhancedOpenAIAgent

agent = EnhancedOpenAIAgent(
    name="ClawAgent",
    api_key=settings.OPENAI_API_KEY,
    enable_tools=True,
    enable_memory=True,
    enable_skills=True,
    enable_react=False  # Enable for complex queries
)

response = await agent.process(user_message)
```

Enjoy your upgraded ClawAgent! 🎉

# ClawAgent Upgrade Guide - Complete Feature Documentation

## Overview

This guide covers all the major upgrades to ClawAgent:

1. **Enhanced Tool Calling** - Professional function calling with schemas
2. **Local LLM Support** - Ollama, vLLM, LM Studio integration
3. **ReAct Framework** - Reasoning + Acting loops for complex tasks
4. **Vector Memory** - Long-term memory with semantic search
5. **Skill System** - Dynamic agent capabilities with learning

---

## 1. Enhanced Tool Calling System

### What's New

The tool calling system has been completely redesigned with:
- Professional OpenAI and Anthropic compatible schemas
- Full parameter validation and type checking
- Tool execution tracking and statistics
- Support for tool chaining and sequential execution

### Key Components

**Files:**
- `src/tools/function_calling.py` - Core tool calling engine
- `src/tools/enhanced_builtin.py` - Built-in tools (Calculator, WebSearch, etc.)

### Usage Example

```python
from src.tools.function_calling import FunctionCallingAgent, ToolCall
from src.tools.enhanced_builtin import CalculatorTool, WebSearchTool

# Create agent with function calling
agent = FunctionCallingAgent(name="ToolAgent")

# Register tools
agent.register_tools([
    CalculatorTool(),
    WebSearchTool(),
])

# Get OpenAI compatible schemas for API
schemas = agent.get_tools_schema(format="openai")

# Execute a tool
tool_call = ToolCall(
    id="calc_1",
    name="calculator",
    arguments={"expression": "2**10 + sqrt(16)", "precision": 2}
)

result = await agent.execute_tool(tool_call)
print(result.result)  # "1028.0"
```

### Built-in Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `calculator` | Math operations with safe evaluation | expression, precision |
| `web_search` | Search for information | query, result_count |
| `get_time` | Get current time/date | timezone, format |
| `file_read` | Read files safely | file_path, encoding, line_range |
| `json_parse` | Parse and validate JSON | json_string, format_output |

### Creating Custom Tools

```python
from src.tools.function_calling import EnhancedTool, Parameter, ParameterType

class CustomTool(EnhancedTool):
    def __init__(self):
        parameters = [
            Parameter(
                name="input_text",
                type=ParameterType.STRING,
                description="Text to process"
            ),
            Parameter(
                name="threshold",
                type=ParameterType.NUMBER,
                description="Processing threshold",
                required=False,
                default=0.5,
                min_value=0.0,
                max_value=1.0
            )
        ]
        
        super().__init__(
            name="custom_tool",
            description="My custom tool",
            parameters=parameters,
            category="custom"
        )
    
    async def _execute_impl(self, **kwargs) -> str:
        input_text = kwargs.get("input_text", "")
        threshold = kwargs.get("threshold", 0.5)
        
        # Your implementation here
        result = f"Processed: {input_text}"
        return result
```

---

## 2. Local LLM Support (Ollama / vLLM / LM Studio)

### Why Local LLMs?

✅ Privacy - No data sent to external APIs  
✅ Cost - No API fees  
✅ Customization - Fine-tune models  
✅ Speed - Latency optimized for local hardware  
✅ Offline capability - Works without internet  

### Supported Providers

#### Ollama (Easiest to setup)

```bash
# Install
curl https://ollama.ai/install.sh | sh

# Run a model
ollama run mistral          # 7B model, fast
ollama run neural-chat      # 7B model, optimized
ollama run llama2:13b       # 13B model, more capable

# Check models
curl http://localhost:11434/api/tags
```

**Pros:** Easy setup, good for CPU-only  
**Cons:** Slower than vLLM on GPU  

#### vLLM (Best performance on GPU)

```bash
# Install
pip install vllm

# Run server
python -m vllm.entrypoints.openai.api_server \
    --model mistralai/Mistral-7B-v0.1 \
    --tensor-parallel-size 2  # GPU count
```

**Pros:** Fast on GPU, high throughput  
**Cons:** Requires GPU, more complex  

#### LM Studio (GUI-friendly)

```
1. Download from https://lmstudio.ai/
2. Install and run
3. Download a model through the UI
4. Setup local server
```

**Pros:** User-friendly, good for beginners  
**Cons:** Less flexible than vLLM  

### Usage

```python
from src.llm.local_providers import LocalLLMFactory

# Auto-detect and create provider
provider = await LocalLLMFactory.create(
    provider="ollama",          # or "vllm", "lm_studio"
    base_url="http://localhost:11434",
    model="mistral"
)

if provider:
    messages = [
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "What is AI?"}
    ]
    
    response = await provider.generate(messages)
    print(response["content"])
```

### Configuration (.env)

```env
# Local LLM Settings
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=mistral

# Or keep OpenAI as fallback
OPENAI_API_KEY=sk-...
```

### Model Recommendations

| Use Case | Model | Size | Memory |
|----------|-------|------|--------|
| Fast chat | Mistral | 7B | 4GB |
| Better quality | Neural Chat | 7B | 4GB |
| High capability | LLaMA 2 | 13B | 8GB |
| Best quality | Mixtral 8x7B | 47GB (sparse) | 20GB |

---

## 3. ReAct Framework (Reasoning + Acting)

### Concept

ReAct combines reasoning and acting in an agentic loop:

1. **THOUGHT** - Agent analyzes the problem
2. **ACTION** - Agent chooses: Tool use, Memory search, Continue reasoning
3. **OBSERVATION** - Agent observes the results
4. **REFLECTION** - Agent learns and adapts

### Visual Flow

```
User Input
    ↓
THOUGHT: Break down problem → ACTION: Choose action
    ↓
    ├→ TOOL_USE: Execute tool
    │   ├→ OBSERVATION: Tool result
    │   └→ REFLECTION: Learn from result → Plan next step
    │
    ├→ KNOWLEDGE_RETRIEVAL: Search memory
    │   └→ OBSERVATION: Retrieved facts
    │
    ├→ REASONING: Continue thinking
    │
    └→ RESPONSE: Provide answer to user
    ↓
Conversation history updated
    ↓
Return response + reasoning trace
```

### Usage

```python
from src.agents.react_agent import ReActAgent, ActionType
from src.llm.openai_client import OpenAILLMClient

# Initialize
llm_client = OpenAILLMClient(api_key="sk-...")

agent = ReActAgent(
    name="ReasoningAgent",
    llm_client=llm_client,
    tools=function_calling_agent,        # From tool system
    vector_memory=vector_memory,         # From memory system
    skill_library=skill_library,         # From skill system
    max_iterations=10
)

# Process with full reasoning
response, loop = await agent.process_with_reasoning(
    user_input="Complex multi-step task"
)

# View reasoning process
print(loop.get_reasoning_trace())
print(loop.get_summary())

# Export trace for analysis
loop.export_trace("reasoning_trace.json")
```

### Reasoning Trace Example

```
ReAct Reasoning Trace:

Step 1:
Thought: The user wants to analyze stock data. I need to search for current prices.
Action: tool_use - {"tool": "web_search", "input": {"query": "AAPL stock price today"}}
Observation: Apple stock is trading at $182.45

Step 2:
Thought: Now I have the current price. Let me calculate potential gains.
Action: tool_use - {"tool": "calculator", "input": {"expression": "182.45 * 1.1"}}
Observation: Result: 200.695

Step 3:
Thought: I have all information needed. Let me provide the final analysis.
Action: response
```

### Customizing the Loop

```python
from src.agents.react_agent import ReActLoop

loop = ReActLoop(
    max_iterations=10,              # Stop after 10 steps
    max_tokens_per_step=1000,       # Token budget per step
    enable_reflection=True          # Enable learning
)

# Add reasoning steps manually
step = loop.add_step(
    thought="I should search for information",
    action_type=ActionType.TOOL_USE,
    action_details={"tool": "web_search", "query": "..."}
)

# Set observation
loop.set_observation(loop_step_index, "Search returned...")
```

---

## 4. Vector Memory & Long-term Memory

### Overview

The vector memory system provides:
- **Semantic search** - Find similar information by meaning
- **Long-term persistence** - Memories survive sessions
- **Importance tracking** - Remember what matters
- **Access patterns** - Learn which memories are useful

### Architecture

```
Memory Item
├─ Content (the actual memory)
├─ Embedding (semantic representation)
├─ Type (conversation, fact, learning, feedback)
├─ Metadata (tags, importance)
├─ Timestamp
├─ Access count
└─ Importance score
    ↓
Vector Store (Persistent)
    ├─ memories.json (all memories)
    └─ Indexes (fast lookup)
    ↓
Semantic Search
├─ Convert query to embedding
├─ Find similar memories by similarity score
└─ Return ranked results
```

### Usage

```python
from src.utils.vector_memory import VectorMemory, SentenceTransformerEmbedding

# Initialize with embeddings
embedding_model = SentenceTransformerEmbedding(model_name="all-MiniLM-L6-v2")
memory = VectorMemory(
    embedding_model=embedding_model,
    storage_path="./long_term_memory",
    similarity_threshold=0.5
)

# Add memories of different types
await memory.add_memory(
    "User prefers Python over JavaScript",
    memory_type="fact",
    metadata={"importance": 0.9, "domain": "preferences"}
)

await memory.add_memory(
    "We discussed machine learning algorithms",
    memory_type="conversation",
    metadata={"date": "2024-01-15"}
)

# Semantic search
results = await memory.search(
    query="What programming languages does user like?",
    limit=3
)

for memory_item, similarity_score in results:
    print(f"{memory_item.content} (match: {similarity_score:.2f})")

# Get context for LLM
context = await memory.get_context(
    query="programming",
    max_results=5,
    memory_type="fact"
)

# Use in system prompt
system_prompt = f"""You are helpful assistant.

{context}

Provide responses based on learned preferences."""

# Statistics
stats = memory.get_stats()
print(f"Total memories: {stats['total_memories']}")
print(f"Types: {stats['type_distribution']}")
```

### Memory Types

| Type | Purpose | Example |
|------|---------|---------|
| `conversation` | Chat history | "User asked about Python" |
| `fact` | Learned facts | "User is in finance" |
| `learning` | Learned patterns | "User prefers detailed answers" |
| `feedback` | Improvement hints | "User said response was too short" |

### Configuration

```python
# Fine-tune similarity
memory = VectorMemory(
    embedding_model=embedding_model,
    similarity_threshold=0.6          # Higher = stricter matching
)

# Disable embeddings (fallback to text search)
memory_no_embed = VectorMemory(
    embedding_model=None,            # Use text search only
    storage_path="./memory"
)

# Export/Import memories
memory.export_memories("backup.json", format="json")
memory.export_memories("backup.csv", format="csv")
```

---

## 5. Skill System

### Overview

Skills are reusable capabilities that agents can learn and apply:
- **Built-in skills** - Pre-configured (reasoning, web search, etc.)
- **Custom skills** - Define your own
- **Dynamic loading** - Load skills at runtime
- **Usage tracking** - Monitor which skills work best
- **Skill learning** - Success rates improve system prompts

### Built-in Skills

```python
from src.agents.skill_system import DEFAULT_SKILLS

for skill in DEFAULT_SKILLS:
    print(f"{skill.name}: {skill.description}")
```

Available: `reasoning`, `web_search`, `code_generation`, `summarization`, `creative_writing`

### Creating Skills

```python
from src.agents.skill_system import Skill, SkillLibrary

# Define skill
data_analysis_skill = Skill(
    name="data_analysis",
    description="Analyze datasets and generate insights",
    instructions="""
    1. Load the dataset
    2. Perform exploratory analysis
    3. Identify patterns and anomalies
    4. Generate insights and recommendations
    """,
    examples=[
        "Analyze sales trends",
        "Detect customer churn patterns"
    ],
    tags=["analysis", "data", "automation"],
    metadata={
        "complexity": "high",
        "tools_required": ["pandas", "matplotlib"]
    }
)

# Save to library
library = SkillLibrary(storage_path="./skills")
library.add_skill(data_analysis_skill)
```

### Using Skills

```python
# Find relevant skills for a task
query = "I need to analyze customer data"
relevant_skills = library.get_relevant_skills(query, max_skills=3)

# Enhance system prompt with skills
system_prompt = library.get_system_prompt_with_skills(
    base_prompt="You are a helpful assistant.",
    skills=relevant_skills
)

# Record skill usage for learning
library.record_skill_usage(
    skill_name="data_analysis",
    success=True  # Update success rate
)

# Check skill statistics
for skill in library.list_skills():
    print(f"{skill.name}: used {skill.usage_count} times, " +
          f"success rate: {skill.success_rate:.2%}")
```

### Skill File Format

Skills are stored as JSON:

```json
{
  "name": "data_analysis",
  "description": "Analyze datasets and generate insights",
  "instructions": "1. Load dataset\n2. Analyze...",
  "examples": ["Analyze sales trends", "Detect patterns"],
  "prerequisites": ["data_loading", "statistical_analysis"],
  "tags": ["analysis", "data"],
  "metadata": {"complexity": "high"},
  "created_at": "2024-01-15T10:30:00",
  "usage_count": 5,
  "success_rate": 0.95
}
```

---

## Integration Guide

### Complete Setup Example

```python
import asyncio
import os
from src.tools.function_calling import FunctionCallingAgent
from src.tools.enhanced_builtin import (
    CalculatorTool, WebSearchTool, GetTimeTool
)
from src.llm.local_providers import LocalLLMFactory
from src.agents.react_agent import ReActAgent
from src.agents.skill_system import SkillLibrary, DEFAULT_SKILLS
from src.utils.vector_memory import VectorMemory, SentenceTransformerEmbedding
from src.llm.openai_client import OpenAILLMClient


async def setup_complete_agent():
    """Setup a complete agent with all features."""
    
    # 1. Tools with function calling
    tools_agent = FunctionCallingAgent("ToolAgent")
    tools_agent.register_tools([
        CalculatorTool(),
        WebSearchTool(),
        GetTimeTool()
    ])
    
    # 2. Vector memory
    embedding_model = SentenceTransformerEmbedding()
    memory = VectorMemory(embedding_model=embedding_model)
    
    # 3. Skill library
    skills = SkillLibrary()
    for skill in DEFAULT_SKILLS:
        skills.add_skill(skill)
    
    # 4. LLM (choose one)
    # Option A: OpenAI
    if os.getenv("OPENAI_API_KEY"):
        llm = OpenAILLMClient(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Option B: Local LLM
    else:
        llm = await LocalLLMFactory.create(
            "ollama",
            "http://localhost:11434",
            "mistral"
        )
        if not llm:
            raise RuntimeError("No LLM available")
    
    # 5. ReAct agent
    agent = ReActAgent(
        name="IntelligentAgent",
        llm_client=llm,
        tools=tools_agent,
        vector_memory=memory,
        skill_library=skills,
        max_iterations=10
    )
    
    return agent


async def main():
    # Setup
    agent = await setup_complete_agent()
    
    # Use
    response, loop = await agent.process_with_reasoning(
        "Calculate the factorial of 5 and search for interesting facts about it"
    )
    
    print(f"Response: {response}")
    print(f"\nReasoning trace:\n{loop.get_reasoning_trace()}")


asyncio.run(main())
```

---

## Configuration (.env)

```env
# OpenAI API (optional)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Local LLM
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=mistral

# Agent Settings
MAX_ITERATIONS=10
TEMPERATURE=0.7

# Memory
MEMORY_PATH=./long_term_memory
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Skills
SKILLS_PATH=./skills
```

---

## Performance Tips

### For CPU-only systems
```bash
# Use smaller models
ollama run neural-chat       # 7B, optimized for CPU
ollama run orca-mini        # 3B, very fast
```

### For GPU systems
```bash
# Use vLLM for best performance
pip install vllm
# Run smaller models but faster
# Quantize models for GPU memory efficiency
```

### Memory optimization
```python
# Batch embeddings for faster processing
embeddings = await embedding_model.embed_batch(texts)

# Limit memory search results
results = await memory.search(query, limit=3)

# Archive old memories
# Implement archival to keep memory fast
```

---

## Troubleshooting

### "sentence-transformers not installed"
```bash
pip install sentence-transformers
```

### "Ollama not responding"
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Test model
ollama run mistral
```

### "Too many tokens"
```python
# Reduce iteration limit
agent = ReActAgent(..., max_iterations=5)

# Use smaller models
# Implement token counting and limits
```

### Memory growing too large
```python
# Implement archival
# Export old memories
memory.export_memories("archive.json")

# Implement cleanup
memory.clear()
```

---

## Next Steps

1. **Run examples:** `python examples_new_features.py`
2. **Setup local LLM:** Start Ollama or vLLM
3. **Configure .env** with your API keys or local URLs
4. **Test each component** independently first
5. **Integrate into OpenAIAgent:** Update agent to use new features
6. **Monitor performance:** Use reasoning traces and memory stats

---

## Resources

- [Ollama Documentation](https://ollama.ai)
- [vLLM GitHub](https://github.com/lm-sys/vllm)
- [sentence-transformers](https://www.sbert.net/)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [Function Calling - OpenAI](https://platform.openai.com/docs/guides/function-calling)


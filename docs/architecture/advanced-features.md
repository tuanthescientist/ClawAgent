# 🚀 ClawAgent Advanced - Features Guide

ClawAgent v2 with **Autonomous Agent**, **Tool Calling**, and **Multi-LLM Support**.

## 🎯 New Features

### 1. 🤖 Autonomous Agent with Tool Calling

The agent can now **independently use tools** to accomplish tasks:

```python
# Agent can use tools autonomously
"I need to calculate 2^10 and check current time"
# Agent uses: calculator_tool, get_time_tool
```

**How it works:**
- Agent analyzes the task
- Decides which tools are needed
- Executes tools and uses results
- Provides final answer

### 2. 🛠️ Built-in Tools

| Tool | Purpose |
|------|---------|
| `web_search` | Search information |
| `calculator` | Math calculations |
| `get_time` | Current time/date |
| `json_parser` | JSON validation |

**Example:**
```json
POST /api/v1/chat/advanced
{
  "message": "What's 2^10 + factorial(5)?",
  "use_tools": true
}
```

Response:
```json
{
  "response": "2^10 = 1024, 5! = 120, so sum = 1144",
  "tools_used": true
}
```

### 3. 📡 Multi-LLM Support

Use different LLM providers:

| Provider | Type | Cost |
|----------|------|------|
| **OpenAI GPT-4** | API (Paid) | $0.03/1K tokens |
| **ChatGPT Subscription** | Browser/Unofficial | Subscription |
| **Local LLM** (Ollama) | Self-hosted (Free) | Free |

**Configuration:**
```env
# Primary: OpenAI
OPENAI_API_KEY=sk-...

# Alternative: ChatGPT subscription
CHATGPT_ACCESS_TOKEN=eyJh...

# Or: Local LLM
USE_LOCAL_LLM=true
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=mistral
```

### 4. 🔗 Dual API Support

- **OpenAI API** - Official, powerful, paid
- **ChatGPT Subscription** - Web version, fallback option
- **Local LLM** - Free, privacy-first

Choose based on your needs:
```python
# Cost-effective: Use ChatGPT subscription
# Powerful: Use OpenAI GPT-4
# Private: Use Local LLM
```

### 5. 🎭 Multi-Agent System

```python
agents = {
    "analyzer": AnalyticsAgent(...),
    "executor": TaskExecutorAgent(...),
    "reporter": ReportingAgent(...)
}

orchestrator = MultiAgentOrchestrator(agents)
await orchestrator.delegate_task("analyze data", "analyzer")
```

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env

# Edit .env:
OPENAI_API_KEY=sk-...
# OR
CHATGPT_ACCESS_TOKEN=eyJh...
# OR
USE_LOCAL_LLM=true
```

### 3. Run Advanced Version
```bash
# Advanced version with autonomous agent + tools
python -m src.main_advanced

# Standard version (simple chatbot)
python -m src.main
```

### 4. Test The API

#### Get Available Tools
```bash
curl http://localhost:8000/api/v1/tools
```

Response:
```json
{
  "status": "success",
  "tools": [
    {"name": "web_search", "description": "Search the web"},
    {"name": "calculator", "description": "Math calculations"},
    {"name": "get_time", "description": "Get current time"}
  ],
  "total": 4
}
```

#### Use Autonomous Agent with Tools
```bash
curl -X POST http://localhost:8000/api/v1/chat/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the current time and calculate 2^8?",
    "use_tools": true,
    "max_iterations": 5
  }'
```

Response:
```json
{
  "status": "success",
  "response": "The current time is 2024-03-28 14:30:45. 2^8 = 256.",
  "tools_used": true
}
```

## 💡 Use Cases

### 1. Task Automation
```
"Create a report: search recent AI news, calculate average, format as JSON"
Agent automatically:
- Uses web_search for news
- Uses calculator for stats
- Uses json_parser for formatting
```

### 2. Data Analysis
```
"Analyze: [JSON data], calculate mean, search for context"
```

### 3. Autonomous Problem Solving
```
"Given these constraints, find the solution"
Agent:
- Breaks down problem
- Uses tools to gather information
- Applies logic to solve
```

## 🔧 Advanced Configuration

### Maximum Agent Iterations
```python
# Prevent infinite loops
await agent.process(message, max_iterations=10)
```

### Custom Tools
```python
class MyCustomTool(Tool):
    async def execute(self, **kwargs) -> str:
        # Your implementation
        pass
    
    def get_schema(self):
        # OpenAI schema
        pass

registry.register(MyCustomTool())
```

### Tool Validation
```python
# Tools are validated before execution
# Type checking
# Parameter validation
# Error handling
```

## 📊 API Endpoints

### `GET /health`
Health check

### `POST /api/v1/chat/advanced`
Autonomous agent chat with tool calling

**Body:**
```json
{
  "message": "Your task",
  "chat_id": "optional_id",
  "use_tools": true,
  "max_iterations": 5
}
```

### `GET /api/v1/tools`
List available tools

### `GET /api/v1/tools/schemas`
Get OpenAI-compatible tool schemas (for GPT function calling)

### `POST /api/v1/whatsapp/webhook`
WhatsApp integration with tool calling

## 🔐 Security

- ✅ Webhook signature verification
- ✅ Tool execution sandboxing
- ✅ Input validation and sanitization
- ✅ Rate limiting (TODO)
- ✅ API key management

## 📈 Performance

- Concurrent tool execution
- Tool caching (planned)
- Async/await throughout
- Memory management

## 🆘 Troubleshooting

### Agent doesn't use tools
```
Check:
1. use_tools=true in request
2. Tools are registered
3. Agent can parse tool calls
```

### ChatGPT token invalid
```
Get new token:
fetch('https://chat.openai.com/api/auth/session')
  .then(r => r.json())
  .then(d => console.log(d.accessToken))
```

### Local LLM not responding
```
Ensure Ollama is running:
ollama serve

Then set:
USE_LOCAL_LLM=true
```

## 🎓 Examples

### Example 1: Math Assistant
```bash
curl -X POST http://localhost:8000/api/v1/chat/advanced \
  -d '{
    "message": "Calculate: sqrt(100) + 2^3 - log(1)",
    "use_tools": true
  }'
```

### Example 2: Research Assistant
```bash
curl -X POST http://localhost:8000/api/v1/chat/advanced \
  -d '{
    "message": "Search for latest AI breakthroughs and summarize",
    "use_tools": true,
    "max_iterations": 10
  }'
```

### Example 3: Task Automation
```bash
curl -X POST http://localhost:8000/api/v1/chat/advanced \
  -d '{
    "message": "Check current time, calculate 365*24*60 minutes in a year, and provide a JSON summary",
    "use_tools": true
  }'
```

## 📚 Comparison

### Basic vs Advanced

| Feature | Basic | Advanced |
|---------|-------|----------|
| Chat | ✅ | ✅ |
| Tool Calling | ❌ | ✅ |
| Autonomous | ❌ | ✅ |
| Dual API | ❌ | ✅ |
| Multi-Agent | ❌ | ✅ |
| WhatsApp | ✅ | ✅ |

## 🚀 Next Steps

1. **Implement Missing Tools:** Add more specialized tools (database, file system, API calls)
2. **Multi-Platform Support:** Add Telegram, Slack, Discord
3. **Persistent Memory:** Long-term context and conversation history
4. **Advanced Scheduling:** Task scheduling and automation
5. **Analytics Dashboard:** Monitor agent performance

## 📖 Related Files

- [Advanced Main Application](../../src/main_advanced.py)
- [Autonomous Agent](../../src/agents/autonomous.py)
- [Tool System](../../src/tools/)
- [Multi-LLM Support](../../src/llm/)

---

**Happy Autonomous Agenting!** 🤖

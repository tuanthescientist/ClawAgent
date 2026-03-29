# 🦅 ClawAgent v3.0

**Production-ready AI Agent Platform v3.0** with Multi-Provider LLM (OpenAI, Ollama, Groq), Hybrid Fallback, Local AI Support, WhatsApp Integration, and Advanced ReAct Framework.

> **NEW in v3.0**: 🎉 Local LLM Support • 🔄 Hybrid Fallback with Circuit Breaker • 🚀 Multi-Provider Architecture • ⚡ Fallback Chain • 📊 Performance Monitoring

## ✨ Features

### Core LLM v3.0
- **🌐 Multi-Provider LLM**: OpenAI, Ollama (local), Groq (fast API), vLLM support
- **🔄 Hybrid Fallback**: Automatic fallback chain with circuit breaker pattern
- **💻 Local LLM**: Run Ollama locally (Qwen, Llama 2, Mistral)
- **⚡ Groq Integration**: Lightning-fast API (175+ tokens/s)
- **📊 Performance Stats**: Track latency, cost, success rates per provider
- **🛡️ Circuit Breaker**: Prevents cascading failures with smart state management
- **🔁 Intelligent Retry**: Configurable retry strategy with exponential backoff

### Agent & Tools
- **🤖 Autonomous Agent**: Advanced ReAct framework with tool orchestration
- **🔧 Tool Calling**: Extensible tool system with 8+ built-in tools
- **🧠 Memory**: Conversation context & vector memory (RAG-ready)
- **⚙️ Multi-Agent Orchestration**: Coordinate multiple agents

### Integration & Deployment
- **💬 WhatsApp Integration**: Direct messaging via Twilio
- **🚀 FastAPI**: High-performance async framework
- **🐳 Docker Ready**: Includes Dockerfile and docker-compose
- **📝 Comprehensive Logging**: Rotation, levels, structured logs
- **🛡️ Production Security**: HMAC verification, environment secrets
- **⚡ Scalable**: Async/await throughout, connection pooling

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API Key
- Twilio Account (for WhatsApp)
- pip or conda

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tuanthescientist/ClawAgent.git
   cd ClawAgent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   OPENAI_API_KEY=sk-...
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155552671
   WHATSAPP_WEBHOOK_TOKEN=your_secret_token
   ```

5. **Run the application**
   ```bash
   python -m src.main
   ```

   The API will be available at `http://localhost:8000`

## 🚀 What's New in v3.0?

### Multi-Provider LLM with Hybrid Fallback

**1. Local LLM Support with Ollama**
```bash
# Install Ollama from https://ollama.ai
ollama pull qwen2.5:14b
ollama serve  # Runs on http://localhost:11434

# ClawAgent automatically detects and uses it!
```

**2. Enable Hybrid Mode**
```env
# .env
LLM_BACKEND=hybrid
OPENAI_API_KEY=sk-...  # Primary fallback
OLLAMA_HOST=http://localhost:11434
GROQ_API_KEY=gsk-...   # (Optional) Ultra-fast fallback
```

**3. Automatic Provider Fallback**
- Primary: Local Ollama (free, private)
- Secondary: Groq (fast API)
- Tertiary: OpenAI (reliable, expensive)
- Built-in **Circuit Breaker** prevents cascading failures

### Code Example: Using v3.0 Hybrid LLM
```python
from src.core.config import AppConfig, LLMBackendType
from src.core.hybrid_controller import HybridLLMController
from src.llm.openai_provider import OpenAIProvider
from src.llm.ollama_provider import OllamaProvider

# Initialize providers
providers = {
    "ollama": OllamaProvider({"host": "http://localhost:11434"}),
    "openai": OpenAIProvider({"api_key": "sk-..."}),
}

# Create hybrid controller with fallback
controller = HybridLLMController(
    providers=providers,
    fallback_chain=["ollama", "openai"],
    circuit_breaker_enabled=True,
)

# Use it like a single provider
response = await controller.generate("Tell me a joke")
print(response.content)
```

**See also**: [UPGRADE_V3_IMPLEMENTATION_GUIDE.md](UPGRADE_V3_IMPLEMENTATION_GUIDE.md)

## 🔧 Advanced Features (v2.0+)

ClawAgent includes **Advanced ReAct Framework** with powerful tools and semantic memory!

### What's New
- 🧠 **Advanced ReAct** - Multi-step reasoning with planning & adaptation
- 🛠️ **Powerful Tools** - Web search, file system, data analysis, API calls, code execution
- 💾 **Vector Memory** - Semantic search with embeddings for context retrieval
- 🎓 **Skill System** - Domain-specific expertise injection
- 📊 **Reasoning Traces** - Export complete reasoning paths for analysis

### Quick Advanced Start

```python
from src.agents.advanced_claw_agent import AdvancedClawAgent
import asyncio

async def main():
    agent = AdvancedClawAgent(
        name="MasterAgent",
        api_key="sk-...",
        enable_advanced_react=True,
        enable_powerful_tools=True,
        enable_memory=True
    )
    
    response = await agent.process(
        "Design a complete data pipeline for analyzing customer behavior"
    )
    
    print(response)
    print(agent.get_statistics())

asyncio.run(main())
```

### Advanced Features Documentation

- **Complete Guide**: [ADVANCED_REACT_INTEGRATION.md](ADVANCED_REACT_INTEGRATION.md)
- **Examples**: [examples_advanced_react_tools.py](examples_advanced_react_tools.py)
- **Status**: [ADVANCED_STATUS.md](ADVANCED_STATUS.md)

### Installation for Advanced Features

```bash
pip install -r requirements-advanced.txt
```

### Key Capabilities

| Feature | Status | Use Case |
|---------|--------|----------|
| Advanced ReAct | ✅ | Complex multi-step reasoning |
| Web Search | ✅ | Research & information gathering |
| Data Analysis | ✅ | Statistical analysis & visualization |
| Code Execution | ⚠️ | Python code (disabled by default) |
| File Operations | ✅ | Safe, sandboxed file access |
| API Integration | ✅ | External service calls |
| Vector Memory | ✅ | Context-aware responses |
| Skill System | ✅ | Domain expertise |

## �📚 API Documentation

### Interactive Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

#### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "ClawAgent API",
  "version": "1.0.0"
}
```

#### Chat
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "message": "Hello, how can you help me?",
  "chat_id": "optional_identifier"
}
```

Response:
```json
{
  "status": "success",
  "response": "I'm ClawAgent, an AI assistant. I can help you with...",
  "chat_id": "optional_identifier"
}
```

#### WhatsApp Webhook
```bash
POST /api/v1/whatsapp/webhook
```

This endpoint receives incoming WhatsApp messages from Twilio and automatically responds through the agent.

## 🔧 Configuration

All settings are managed through environment variables in `.env`:

```env
# Environment
ENV=development
DEBUG=True
LOG_LEVEL=INFO

# OpenAI
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
WHATSAPP_WEBHOOK_TOKEN=your_secret

# Server
HOST=0.0.0.0
PORT=8000
API_PREFIX=/api/v1

# Features
MAX_MESSAGE_LENGTH=4000
ENABLE_PERSISTENCE=True
```

## 🏗️ Project Structure

```
ClawAgent/
├── src/
│   ├── agents/           # AI agent implementations
│   │   ├── base.py      # Base agent class
│   │   └── openai_agent.py  # OpenAI implementation
│   ├── integrations/    # Third-party integrations
│   │   └── whatsapp.py  # Twilio WhatsApp integration
│   ├── utils/           # Utility modules
│   │   └── logger.py    # Logging setup
│   └── main.py          # FastAPI application
├── config/
│   └── settings.py      # Configuration management
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest tests/
pytest --cov=src tests/  # With coverage
```

## 📦 Deployment

### Local Development
```bash
python -m src.main
```

### Production with Uvicorn
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```bash
# Build image
docker build -t clawagent .

# Run container
docker run -p 8000:8000 --env-file .env clawagent
```

## 🔐 Security Notes

1. **Never commit `.env`** - Always use `.env.example` as template
2. **Verify webhook signatures** - All WhatsApp webhooks are verified
3. **Use HTTPS in production** - Especially for webhook endpoints
4. **Rotate API keys regularly** - Update OpenAI and Twilio credentials
5. **Rate limiting** - Consider adding rate limiting in production

## 📝 Logging

Logs are written to:
- **Console**: Real-time output during development
- **File**: `logs/clawagent.log` with automatic rotation (10MB max)

Configure log level in `.env`:
```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
```

## 🐛 Troubleshooting

### WhatsApp messages not received
- Verify Twilio webhook URL is correct
- Check signature verification isn't rejecting requests
- Ensure webhook token matches in settings

### OpenAI rate limiting
- Add delays between requests
- Monitor API usage in OpenAI dashboard
- Consider using GPT-3.5-turbo for lower costs

### Memory issues with long conversations
- Clear conversation history periodically
- Implement message pruning
- Use conversation summarization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Tuan Tran**
- GitHub: [@tuanthescientist](https://github.com/tuanthescientist)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [OpenAI](https://openai.com/) - API and models
- [Twilio](https://www.twilio.com/) - WhatsApp integration
- [Pydantic](https://docs.pydantic.dev/) - Data validation

## 📧 Support

For issues and questions:
- GitHub Issues: [Issues](https://github.com/tuanthescientist/ClawAgent/issues)
- Email: your-email@example.com

---

**Built with ❤️ by the ClawAgent team**

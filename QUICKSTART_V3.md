# ClawAgent v3.0 - Quick Start Guide

Welcome to ClawAgent v3.0! This guide gets you up and running in 5 minutes.

## 🚀 What's New in v3.0

✨ **Core Features**:
- **Multi-Provider LLM Support** - Use OpenAI, Ollama, vLLM, Groq, or LM Studio
- **Hybrid Fallback** - Automatic failover between providers
- **Circuit Breaker** - Intelligent reliability and error recovery  
- **Vector Memory** - Persistent memory with ChromaDB
- **Rate Limiting** - Built-in throttling and quotas
- **Production Ready** - Security, logging, monitoring

## 📦 Installation

### Minimal Setup (OpenAI only)

```bash
# Clone repo
git clone https://github.com/tuanthescientist/ClawAgent.git
cd ClawAgent

# Install core only
pip install -r requirements-core.txt

# Set environment
export OPENAI_API_KEY=sk-...
```

### Full Setup (Local LLM + All Features)

```bash
# Install everything
pip install -r requirements-advanced.txt

# Setup Ollama (macOS/Linux/Windows)
# Visit: https://ollama.ai

# Pull a model
ollama pull qwen2.5:14b

# Verify installation
python -c "from src.core import config; print(config.LLM_BACKEND)"
```

## 🎯 5-Minute Example

### 1. Configure Your LLM

Choose one option:

**Option A: Cloud LLM (OpenAI)**
```bash
export OPENAI_API_KEY=sk-...
export LLM_BACKEND=openai
export LLM_MODEL=gpt-4-turbo
```

**Option B: Local LLM (Ollama)**
```bash
# Make sure Ollama is running: ollama serve
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:14b
export LLM_BACKEND=ollama
```

**Option C: Hybrid (Automatic Fallback)**
```bash
export LLM_BACKEND=hybrid
export FALLBACK_CHAIN=openai,groq,ollama
```

### 2. Use in Your Code

```python
import asyncio
from src.core.config import AppConfig
from src.core.llm_provider import Message
from src.llm.openai_provider import OpenAIProvider

async def main():
    # Initialize provider
    config = AppConfig()
    provider = OpenAIProvider({
        "api_key": config.OPENAI_API_KEY,
        "model": config.LLM_MODEL,
    })
    
    # Create messages
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Explain quantum computing in 1 sentence.")
    ]
    
    # Get response
    response = await provider.complete(messages)
    print(response.content)

asyncio.run(main())
```

### 3. Run Examples

```bash
# Hybrid LLM example (fallback demo)
python examples/hybrid_llm_example.py

# See more examples
ls examples/
```

## 🔧 Configuration Reference

### Core Settings

```python
from src.core.config import AppConfig, LLMBackendType

config = AppConfig(
    LLM_BACKEND=LLMBackendType.HYBRID,      # openai, ollama, vllm, groq, hybrid
    LLM_MODEL="gpt-4-turbo",
    LLM_TEMPERATURE=0.7,
    LLM_MAX_TOKENS=2000,
)
```

### Local LLM Settings

```python
config = AppConfig(
    LLM_BACKEND=LLMBackendType.OLLAMA,
    OLLAMA_HOST="http://localhost:11434",
    OLLAMA_MODEL="qwen2.5:14b",             # qwen2.5, deepseek-r1, llama3.3, etc.
)
```

### Hybrid Fallback Settings

```python
config = AppConfig(
    LLM_BACKEND=LLMBackendType.HYBRID,
    FALLBACK_CHAIN=[
        LLMBackendType.OPENAI,              # Try first (fast but paid)
        LLMBackendType.GROQ,                # Try second (fast and cheap)
        LLMBackendType.OLLAMA,              # Try last (local, free)
    ],
    FALLBACK_RETRY_COUNT=3,                 # Retry each provider 3x
    FALLBACK_TIMEOUT_SECONDS=30,            # Timeout after 30s
    CIRCUIT_BREAKER_ENABLED=True,           # Auto-disable failing providers
)
```

### Vector Memory Settings

```python
config = AppConfig(
    MEMORY_BACKEND=MemoryBackendType.CHROMADB,  # in_memory, chromadb, qdrant
    CHROMADB_PATH="./data/chromadb",
    EMBEDDING_MODEL="text-embedding-3-small",
    EMBEDDING_DIM=1536,
)
```

### Rate Limiting

```python
config = AppConfig(
    RATE_LIMIT_ENABLED=True,
    RATE_LIMIT_REQUESTS_PER_MINUTE=60,      # Max requests/minute
    RATE_LIMIT_TOKENS_PER_MINUTE=90000,     # Max tokens/minute
    RATE_LIMIT_PER_USER=True,               # Per-user limiting
)
```

## 🎮 Using Hybrid Controller

```python
from src.core.hybrid_controller import HybridLLMController
from src.llm.openai_provider import OpenAIProvider
from src.llm.ollama_provider import OllamaProvider

# Setup providers
providers = {
    "openai": OpenAIProvider({
        "api_key": "sk-...",
        "model": "gpt-4-turbo",
    }),
    "ollama": OllamaProvider({
        "host": "http://localhost:11434",
        "model": "qwen2.5:14b",
    })
}

# Create controller
controller = HybridLLMController(
    providers=providers,
    fallback_chain=["openai", "ollama"],
    retry_count=3,
    circuit_breaker_enabled=True,
)

# Use controller
response = await controller.complete(messages)

# Check statistics
stats = controller.get_stats()
print(stats)

# Check health
health = await controller.health_check()
print(health)
```

## 📊 Monitoring

### Statistics

```python
stats = controller.get_stats()

# Output:
# {
#   "providers": {
#     "openai": {
#       "requests": 10,
#       "successes": 9,
#       "failures": 1,
#       "success_rate": "90.0%",
#       "avg_latency_ms": "2500",
#       "total_tokens": 5420,
#       "circuit_breaker": {
#         "state": "closed",
#         "failure_count": 0
#       }
#     }
#   }
# }
```

### Health Check

```python
health = await controller.health_check()

# Output:
# {
#   "overall_healthy": true,
#   "providers": {
#     "openai": {
#       "healthy": true,
#       "latency_ms": 2500,
#       "model": "gpt-4-turbo"
#     },
#     "ollama": {
#       "healthy": false,
#       "error": "Connection refused"
#     }
#   }
# }
```

## 🐳 Docker Setup

### Setup Ollama in Docker

```bash
# Start Ollama container
docker run -d \
  --name ollama \
  -p 11434:11434 \
  ollama/ollama

# Pull model
docker exec ollama ollama pull qwen2.5:14b

# Test
curl http://localhost:11434/api/tags
```

### GPU Support (NVIDIA)

```bash
# With GPU support
docker run -d \
  --name ollama \
  --gpus all \
  -p 11434:11434 \
  ollama/ollama
```

## 🔗 Environment Variables

Create `.env` file:

```env
# LLM
LLM_BACKEND=hybrid
LLM_MODEL=gpt-4-turbo
OPENAI_API_KEY=sk-...

# Local LLM
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen2.5:14b

# Fallback
FALLBACK_CHAIN=openai,groq,ollama
CIRCUIT_BREAKER_ENABLED=true

# Memory
MEMORY_BACKEND=chromadb
CHROMADB_PATH=./data/chromadb

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

Then load in code:

```python
from src.core.config import config

# Config loads from .env automatically
print(config.LLM_BACKEND)      # "hybrid"
print(config.OLLAMA_MODEL)     # "qwen2.5:14b"
```

## 📚 Next Steps

1. **Try Examples**: `python examples/hybrid_llm_example.py`
2. **Read Docs**: 
   - [LOCAL_LLM_GUIDE.md](LOCAL_LLM_GUIDE.md) - Setup local LLMs
   - [TOOLS_LIST.md](TOOLS_LIST.md) - Available tools
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. **Integrate**: Add to your application
4. **Deploy**: Docker + CI/CD

## 🆘 Troubleshooting

### Ollama Connection Failed

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Or use Docker
docker run -p 11434:11434 ollama/ollama
```

### OpenAI API Errors

```bash
# Verify API key
echo $OPENAI_API_KEY

# Check format (should start with sk-)
# If empty, set it:
export OPENAI_API_KEY=sk-...
```

### Provider Timeout

```python
# Increase timeout
config.FALLBACK_TIMEOUT_SECONDS = 60

# Or per provider
provider = OllamaProvider({
    "timeout": 60,  # seconds
})
```

### Circuit Breaker Open

Check health:
```python
health = await controller.health_check()
print(health)  # See which provider is failing
```

After 60 seconds (configurable), circuit breaker will try again.

## 💡 Tips & Best Practices

1. **Start with OpenAI**: Reliable, battle-tested
2. **Add Local LLM**: Setup Ollama for fallback
3. **Use Hybrid**: Best of both worlds
4. **Monitor Metrics**: Check stats regularly
5. **Set Timeouts**: Prevent hanging
6. **Rate Limit**: Protect your quota
7. **Use Circuit Breaker**: Faster failure detection
8. **Log Everything**: Debug issues easily

## 🚀 Production Checklist

- [ ] Setup `.env` with all credentials
- [ ] Run tests: `pytest -v`
- [ ] Check health: `await controller.health_check()`
- [ ] Monitor stats: `controller.get_stats()`
- [ ] Setup logging: Use structured logging
- [ ] Enable rate limiting: `RATE_LIMIT_ENABLED=true`
- [ ] Enable security: `SECURITY_ENABLE_INPUT_SANITIZATION=true`
- [ ] Docker: Test containerized setup
- [ ] CI/CD: Setup GitHub Actions

## 📖 Full Documentation

- [UPGRADE_V3_IMPLEMENTATION_GUIDE.md](UPGRADE_V3_IMPLEMENTATION_GUIDE.md) - Complete implementation
- [Contributing](CONTRIBUTING.md) - How to contribute
- [License](LICENSE) - MIT License

## 🤝 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Docs**: [Documentation](https://docs.clawagent.dev)

---

**Happy coding! 🦞**


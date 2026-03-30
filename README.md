# ClawAgent v3.0

AI agent platform with FastAPI backend, tool orchestration, WhatsApp integration, and hybrid LLM support (OpenAI / local models via Ollama, Groq).

## Highlights

- **FastAPI** - Production-grade async framework
- **Tool-calling agent** - Autonomous task execution with 8+ built-in tools
- **Hybrid LLM** - Fallback between OpenAI, Ollama (local), and Groq
- **WhatsApp integration** - Direct messaging via Twilio
- **Docker-ready** - Single-command deployment
- **Tests & CI** - Pytest suite with GitHub Actions

## Quick Start

```bash
# Clone
git clone https://github.com/tuanthescientist/ClawAgent.git
cd ClawAgent

# Setup
cp .env.example .env
pip install -r requirements.txt

# Run
uvicorn src.main:app --reload
```

Visit `http://localhost:8000/health` to verify.

## Environment Variables

| Variable | Required | Default | Description |
|---|:---:|---|---|
| `OPENAI_API_KEY` | No | - | OpenAI API key (e.g., `sk-...`) |
| `OPENAI_MODEL` | No | `gpt-4` | OpenAI model name |
| `LLM_BACKEND` | No | `hybrid` | LLM mode: `openai`, `ollama`, `groq`, or `hybrid` |
| `OLLAMA_HOST` | No | `http://localhost:11434` | Local Ollama endpoint |
| `GROQ_API_KEY` | No | - | Groq API key (fast inference) |
| `TWILIO_ACCOUNT_SID` | No | - | Twilio account ID (WhatsApp) |
| `TWILIO_AUTH_TOKEN` | No | - | Twilio auth token (WhatsApp) |
| `TWILIO_WHATSAPP_NUMBER` | No | - | WhatsApp sender number |
| `ENV` | No | `development` | App environment |
| `DEBUG` | No | `True` | Debug mode |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Run Modes

### Cloud-only
Uses OpenAI exclusively:
```bash
export LLM_BACKEND=openai
export OPENAI_API_KEY=sk-...
uvicorn src.main:app --reload
```

### Local-only
Uses Ollama (private, free):
```bash
# Start Ollama first
ollama pull qwen2.5:14b
ollama serve

# Then run ClawAgent
export LLM_BACKEND=ollama
uvicorn src.main:app --reload
```

### Hybrid fallback (recommended)
Falls back: OpenAI → Groq → Ollama:
```bash
export LLM_BACKEND=hybrid
export OPENAI_API_KEY=sk-...
export GROQ_API_KEY=gsk-...
export OLLAMA_HOST=http://localhost:11434
uvicorn src.main:app --reload
```

## API Examples

### Health Check
```bash
curl http://localhost:8000/health
```
Response:
```json
{
  "status": "healthy",
  "service": "ClawAgent API v3.0",
  "version": "3.0.0"
}
```

### Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?"}'
```

## Docker

```bash
# Build
docker build -t clawagent:latest .

# Run
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -e LLM_BACKEND=hybrid \
  clawagent:latest
```

Or use docker-compose:
```bash
docker-compose up
```

## Documentation

- **[Quick Start Guide](docs/getting-started/quickstart.md)** - Setup & configuration
- **[Upgrade Guide](docs/getting-started/upgrade-guide.md)** - v2 → v3 migration
- **[Architecture](docs/architecture/)** - Tools system, advanced features
- **[Roadmap](docs/planning/roadmap.md)** - Planned features
- **[Contributing](CONTRIBUTING.md)** - Development guidelines

## Support

- **Issues**: [GitHub Issues](https://github.com/tuanthescientist/ClawAgent/issues)
- **Releases**: [GitHub Releases](https://github.com/tuanthescientist/ClawAgent/releases)
- **License**: [MIT](LICENSE)

---

**Latest**: v3.0.0 | Hybrid LLM | Local + Cloud | Tool Orchestration

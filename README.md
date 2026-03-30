# ClawAgent v3.0

ClawAgent is an AI agent platform built with FastAPI, tool orchestration, optional local LLM support, and WhatsApp integration.

ClawAgent supports OpenAI and optional local LLM execution via Ollama-compatible endpoint.

## Features

- FastAPI backend
- Tool-based agent architecture
- Optional local LLM support
- Docker-ready
- Test suite included

## Quick Start

```bash
git clone https://github.com/tuanthescientist/ClawAgent.git
cd ClawAgent
cp .env.example .env
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Environment Variables

| Variable | Example | Description |
|---|---|---|
| OPENAI_API_KEY | `your_key` | OpenAI API key |
| USE_LOCAL_LLM | `False` | Enable optional local LLM usage |
| LOCAL_LLM_URL | `http://localhost:11434` | Ollama-compatible endpoint |
| LOCAL_LLM_MODEL | `mistral` | Local model name |
| TWILIO_ACCOUNT_SID | `your_sid` | Twilio account SID |
| TWILIO_AUTH_TOKEN | `your_token` | Twilio auth token |
| TWILIO_WHATSAPP_NUMBER | `whatsapp:+1234567890` | WhatsApp sender number |
| WHATSAPP_WEBHOOK_TOKEN | `your_secret` | Webhook verification secret |

## API

### `GET /health`

```json
{
  "status": "healthy",
  "service": "ClawAgent API v3.0",
  "version": "3.0.0"
}
```

- `POST /api/v1/chat`
- `POST /api/v1/whatsapp/webhook`

## Documentation

- [Getting Started](docs/getting-started/quickstart-v3.md)
- [Architecture](docs/architecture/tools-system-architecture.md)
- [Status](docs/status/)
- [Roadmap](docs/planning/roadmap.md)

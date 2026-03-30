"""Main FastAPI application for ClawAgent v3.0.

Features:
- Multi-provider LLM support (OpenAI, Ollama, Groq, vLLM)
- Hybrid fallback with circuit breaker
- WhatsApp integration
- Advanced ReAct framework
- Production-grade reliability
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.utils.logger import setup_logging
from src.core.config import AppConfig, LLMBackendType
from src.core.hybrid_controller import HybridLLMController
from src.llm.openai_provider import OpenAIProvider
from src.llm.ollama_provider import OllamaProvider
from src.llm.groq_provider import GroqProvider
from src.agents.autonomous import AutonomousAgent
from src.integrations.whatsapp import WhatsAppManager


def _resolve_backend(name: str) -> LLMBackendType:
    """Resolve backend name to enum with a safe fallback."""
    try:
        return LLMBackendType(name.lower())
    except ValueError:
        logger.warning("Unknown LLM backend '%s', falling back to OPENAI", name)
        return LLMBackendType.OPENAI

# Setup logging
setup_logging(log_level=settings.LOG_LEVEL, log_file="clawagent.log")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ClawAgent API v3.0",
    description="Professional AI Agent with Hybrid LLM, WhatsApp Integration & Advanced ReAct",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize v3.0 services
try:
    # Load v3.0 configuration
    config = AppConfig(
        LLM_BACKEND=_resolve_backend(settings.LLM_BACKEND),
        LLM_MODEL=settings.OPENAI_MODEL,
        OPENAI_API_KEY=settings.OPENAI_API_KEY or "",
        OLLAMA_HOST=settings.OLLAMA_HOST,
        GROQ_API_KEY=settings.GROQ_API_KEY or "",
    )
    
    # Initialize available LLM providers
    providers = {}
    
    # OpenAI Provider (always available)
    if settings.OPENAI_API_KEY:
        providers["openai"] = OpenAIProvider({
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.OPENAI_MODEL,
            "temperature": 0.7,
            "max_tokens": 2000,
        })
        logger.info("✓ OpenAI provider initialized")
    
    # Ollama Provider (local)
    try:
        providers["ollama"] = OllamaProvider({
            "host": config.OLLAMA_HOST,
            "model": "qwen2.5:14b",  # Default model
            "temperature": 0.7,
        })
        logger.info("✓ Ollama provider initialized (local LLM)")
    except Exception as e:
        logger.debug(f"Ollama provider not available: {e}")
    
    # Groq Provider (fast API)
    try:
        if settings.get("GROQ_API_KEY"):
            providers["groq"] = GroqProvider({
                "api_key": settings.GROQ_API_KEY,
                "model": settings.GROQ_MODEL,
            })
            logger.info("✓ Groq provider initialized (fast API)")
    except Exception as e:
        logger.debug(f"Groq provider not available: {e}")
    
    # Create Hybrid Controller if multiple providers
    if len(providers) > 1:
        llm_provider = HybridLLMController(
            providers=providers,
            fallback_chain=list(providers.keys()),
            retry_count=3,
            circuit_breaker_enabled=True,
        )
        logger.info(f"✓ Hybrid LLM Controller initialized with {len(providers)} providers")
    else:
        llm_provider = next(iter(providers.values()), None)
        logger.info("✓ Single provider mode")

    if not llm_provider:
        raise ValueError("No LLM provider available. Configure OPENAI_API_KEY or a local provider.")
    
    # Initialize Autonomous Agent with new provider
    agent = AutonomousAgent(
        name="ClawAgent v3.0",
        llm_provider=llm_provider,
    )
    
    whatsapp_manager = None
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        whatsapp_manager = WhatsAppManager(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            whatsapp_number=settings.TWILIO_WHATSAPP_NUMBER or "",
            webhook_token=settings.WHATSAPP_WEBHOOK_TOKEN or "",
        )
    
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise


@app.on_event("startup")
async def startup_event():
    """Handle startup event."""
    logger.info("ClawAgent v3.0 API starting...")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"LLM Backend: {config.LLM_BACKEND.value}")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle shutdown event."""
    logger.info("ClawAgent v3.0 API shutting down...")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ClawAgent API v3.0",
        "version": "3.0.0"
    }


# Chat endpoint
@app.post(f"{settings.API_PREFIX}/chat")
async def chat(request: Request):
    """Process chat message.
    
    Request body:
    {
        "message": "Your message here",
        "chat_id": "optional_chat_identifier"
    }
    """
    try:
        data = await request.json()
        user_message = data.get("message", "").strip()
        chat_id = data.get("chat_id")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(user_message) > settings.MAX_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Message exceeds maximum length of {settings.MAX_MESSAGE_LENGTH}"
            )
        
        # Process message with agent
        response = await agent.process(user_message)
        
        logger.info(f"Chat processed - Chat ID: {chat_id}, User: {user_message[:50]}")
        
        return {
            "status": "success",
            "response": response,
            "chat_id": chat_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )


# WhatsApp webhook endpoint
@app.post(f"{settings.API_PREFIX}/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from Twilio."""
    try:
        if not whatsapp_manager:
            raise HTTPException(status_code=503, detail="WhatsApp integration not configured")

        # Get form data
        form_data = await request.form()
        
        # Verify webhook signature
        signature = request.headers.get("X-Twilio-Signature", "")
        body = await request.body()
        
        if not whatsapp_manager.verify_webhook(signature, body.decode()):
            logger.warning("Invalid webhook signature received")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse incoming message
        sender, message_text = whatsapp_manager.parse_incoming_message(dict(form_data))
        
        if not sender or not message_text:
            logger.warning("Failed to parse incoming WhatsApp message")
            raise HTTPException(status_code=400, detail="Invalid message format")
        
        # Process message with agent
        response = await agent.process(message_text)
        
        # Send response back via WhatsApp
        whatsapp_manager.send_message(sender, response)
        
        logger.info(f"WhatsApp message processed - From: {sender}, Message: {message_text[:50]}")
        
        # Return Twilio response
        twiml = whatsapp_manager.create_reply(response)
        return twiml
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"WhatsApp webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ClawAgent API v3.0",
        "version": "3.0.0",
        "endpoints": {
            "health": "/health",
            "chat": f"{settings.API_PREFIX}/chat",
            "whatsapp_webhook": f"{settings.API_PREFIX}/whatsapp/webhook"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

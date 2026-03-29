"""Advanced FastAPI application with Autonomous Agent, Hybrid LLM, Tool Calling, and Multi-Provider Support - v3.0."""

import logging
from fastapi import FastAPI, Request, HTTPException, Form
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
from src.agents.autonomous import AutonomousAgent, MultiAgentOrchestrator
from src.tools.base import ToolRegistry
from src.tools.builtin import get_default_tools
from src.integrations.whatsapp import WhatsAppManager

# Setup logging
setup_logging(log_level=settings.LOG_LEVEL, log_file="clawagent_advanced.log")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ClawAgent Advanced API v3.0",
    description="Professional AI Agent with Hybrid LLM, Tool Calling, Multi-Provider Support & WhatsApp Integration",
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

# Initialize services
try:
    # Load v3.0 configuration
    config = AppConfig(
        LLM_BACKEND=LLMBackendType.HYBRID if settings.LLM_BACKEND.lower() == "hybrid" else LLMBackendType.OPENAI,
        LLM_MODEL=settings.OPENAI_MODEL,
        OPENAI_API_KEY=settings.OPENAI_API_KEY,
        OLLAMA_HOST=settings.get("OLLAMA_HOST", "http://localhost:11434"),
    )
    
    # Initialize available LLM providers
    providers = {}
    
    # OpenAI Provider (primary)
    if settings.OPENAI_API_KEY:
        providers["openai"] = OpenAIProvider({
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.OPENAI_MODEL,
            "temperature": 0.7,
            "max_tokens": 2000,
        })
        logger.info("✓ OpenAI provider initialized")
    
    # Ollama Provider (local LLM)
    try:
        providers["ollama"] = OllamaProvider({
            "host": config.OLLAMA_HOST,
            "model": "qwen2.5:14b",
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
                "model": "mixtral-8x7b-32768",
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
        llm_provider = providers.get("openai")
        logger.info("✓ Single provider mode (OpenAI)")
    
    # Setup tool registry with default tools
    tool_registry = ToolRegistry()
    for tool in get_default_tools():
        tool_registry.register(tool)
    
    # Initialize autonomous agent with v3.0 LLM provider
    if not llm_provider:
        raise ValueError("No LLM provider available")
    
    agent = AutonomousAgent(
        name="ClawAgent Advanced v3.0",
        llm_provider=llm_provider,
        tool_registry=tool_registry
    )
    
    # Initialize WhatsApp manager if configured
    whatsapp_manager = None
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        whatsapp_manager = WhatsAppManager(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            whatsapp_number=settings.TWILIO_WHATSAPP_NUMBER,
            webhook_token=settings.WHATSAPP_WEBHOOK_TOKEN
        )
    
    logger.info("✓ All services initialized successfully (v3.0)")
    logger.info(f"✓ Available tools: {', '.join([t.name for t in tool_registry.list_tools()])}")
    logger.info(f"✓ LLM Backend: {config.LLM_BACKEND.value}")
    
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise


@app.on_event("startup")
async def startup_event():
    """Handle startup event."""
    logger.info("ClawAgent Advanced API v3.0 starting...")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"LLM Backend: {config.LLM_BACKEND.value}")
    logger.info(f"Tools available: {len(tool_registry.list_tools())}")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle shutdown event."""
    logger.info("ClawAgent Advanced API v3.0 shutting down...")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ClawAgent Advanced API v3.0",
        "version": "3.0.0",
        "features": ["autonomous_agent", "tool_calling", "hybrid_llm", "local_llm", "groq", "whatsapp"]
    }


# Advanced chat with autonomous agent and tool calling
@app.post(f"{settings.API_PREFIX}/chat/advanced")
async def advanced_chat(request: Request):
    """Process chat with autonomous agent and tool calling.
    
    Request body:
    {
        "message": "Your message here",
        "chat_id": "optional_chat_identifier",
        "use_tools": true,
        "max_iterations": 5
    }
    """
    try:
        data = await request.json()
        user_message = data.get("message", "").strip()
        chat_id = data.get("chat_id")
        use_tools = data.get("use_tools", True)
        max_iterations = data.get("max_iterations", 10)
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(user_message) > settings.MAX_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Message exceeds maximum length of {settings.MAX_MESSAGE_LENGTH}"
            )
        
        # Process message with autonomous agent
        agent.autonomous_mode = use_tools
        response = await agent.process(user_message, max_iterations=max_iterations)
        
        logger.info(f"Advanced chat processed - Chat ID: {chat_id}")
        
        return {
            "status": "success",
            "response": response,
            "chat_id": chat_id,
            "tools_used": agent.autonomous_mode
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Advanced chat error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(e)}
        )


# Get available tools
@app.get(f"{settings.API_PREFIX}/tools")
async def get_available_tools():
    """Get list of available tools."""
    tools = [
        {
            "name": tool.name,
            "description": tool.description
        }
        for tool in tool_registry.list_tools()
    ]
    
    return {
        "status": "success",
        "tools": tools,
        "total": len(tools)
    }


# Get tool schemas for OpenAI
@app.get(f"{settings.API_PREFIX}/tools/schemas")
async def get_tool_schemas():
    """Get OpenAI-compatible tool schemas."""
    return {
        "status": "success",
        "schemas": tool_registry.get_schemas()
    }


# WhatsApp webhook endpoint (with tool calling)
@app.post(f"{settings.API_PREFIX}/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages with tool calling."""
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
        
        # Process message with autonomous agent
        response = await agent.process(
            message_text,
            max_iterations=5  # Limit for WhatsApp
        )
        
        # Send response back via WhatsApp
        whatsapp_manager.send_message(sender, response)
        
        logger.info(f"WhatsApp message processed with tools - From: {sender}")
        
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
        "name": "ClawAgent Advanced API",
        "version": "2.0.0",
        "features": {
            "autonomous_agent": "AI agent that can autonomously call tools",
            "tool_calling": f"{len(tool_registry.list_tools())} built-in tools available",
            "multi_llm": "Support for OpenAI + ChatGPT Browser + Local LLM",
            "whatsapp": "WhatsApp integration via Twilio"
        },
        "endpoints": {
            "health": "/health",
            "chat_advanced": f"{settings.API_PREFIX}/chat/advanced",
            "tools": f"{settings.API_PREFIX}/tools",
            "tool_schemas": f"{settings.API_PREFIX}/tools/schemas",
            "whatsapp_webhook": f"{settings.API_PREFIX}/whatsapp/webhook"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_advanced:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

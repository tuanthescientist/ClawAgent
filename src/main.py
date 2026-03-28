"""Main FastAPI application for ClawAgent."""

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
from src.agents.openai_agent import OpenAIAgent
from src.integrations.whatsapp import WhatsAppManager

# Setup logging
setup_logging(log_level=settings.LOG_LEVEL, log_file="clawagent.log")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ClawAgent API",
    description="Professional AI Agent with WhatsApp Integration",
    version="1.0.0"
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
    agent = OpenAIAgent(
        name="ClawAgent",
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_MODEL
    )
    
    whatsapp_manager = WhatsAppManager(
        account_sid=settings.TWILIO_ACCOUNT_SID,
        auth_token=settings.TWILIO_AUTH_TOKEN,
        whatsapp_number=settings.TWILIO_WHATSAPP_NUMBER,
        webhook_token=settings.WHATSAPP_WEBHOOK_TOKEN
    )
    
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise


@app.on_event("startup")
async def startup_event():
    """Handle startup event."""
    logger.info("ClawAgent API starting...")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle shutdown event."""
    logger.info("ClawAgent API shutting down...")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ClawAgent API",
        "version": "1.0.0"
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
        "name": "ClawAgent API",
        "version": "1.0.0",
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

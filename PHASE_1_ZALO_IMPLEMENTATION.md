# Phase 1: Zalo OA Integration - Implementation Guide

**Status**: Ready to implement  
**Priority**: CRITICAL  
**Timeline**: 1-2 weeks  
**Owner**: TBD  

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Implementation Steps](#implementation-steps)
4. [File Structure](#file-structure)
5. [Code Templates](#code-templates)
6. [Testing Strategy](#testing-strategy)
7. [Deployment](#deployment)

---

## 🎯 Overview

### Goal
Create a complete Zalo OA integration for ClawAgent that:
- ✅ Receives messages from Zalo users
- ✅ Routes to ReAct agent
- ✅ Sends responses back through Zalo
- ✅ Handles rich messages (buttons, images, carousel)
- ✅ Secures webhook with signature verification

### Success Criteria
- User sends message in Zalo OA → Agent responds
- All message types supported (text, image, button, carousel)
- Webhook signature verified (no replay attacks)
- 100% test coverage for critical paths
- Documentation complete & clear

### Scope
- **Zalo API Version**: v3.0 (Official Account API)
- **Message Types Supported**: Text, Image, Button, Carousel, Template
- **Event Types**: user_send_text, user_send_image, send_item, etc.
- **Integration Point**: FastAPI webhook endpoint
- **Agent Interface**: Platform-agnostic (reuse WhatsApp flow)

---

## 🏗️ Architecture

### High-Level Flow

```
Zalo User                    ClawAgent Server                    LLM
    │                              │                               │
    ├─ sends message────────→(1)webhook receiver─────────────────→(2)parse
    │                              │
    │                              ├─→(3)signature verify
    │                              │
    │                              ├─→(4)extract text/data
    │                              │
    │                              ├─→(5)route to agent
    │                              │
    │◄─ receive response◄────(6)format response◄───(7)get response
    │
```

### Component Architecture

```
src/integrations/
├── zalo.py                  # Main ZaloOAIntegration class
├── zalo_events.py           # Event type definitions
├── zalo_messages.py         # Message format definitions
└── zalo_api.py              # Zalo API client

src/
├── main.py                  # Add /api/v1/zalo/webhook route
└── agents/
    └── enhanced_openai_agent.py  # Existing agent (no change)

config/
└── settings.py              # Add ZALO_* config variables
```

### Key Classes

```python
# Event handling
class ZaloEvent:
    event_id: str
    timestamp: int
    user_id: str
    data: Dict

class ZaloMessage:
    message_id: str
    user_id: str
    text: str
    attachment: Optional[Dict]

# API integration
class ZaloAPIClient:
    async def send_text(user_id: str, text: str) -> bool
    async def send_template(user_id: str, template: Dict) -> bool
    async def get_user_info(user_id: str) -> Dict

# Webhook handler
class ZaloOAIntegration:
    async def receive_webhook(request: FastAPI.Request) -> Dict
    def verify_signature(signature: str, body: bytes) -> bool
    async def handle_message(event: ZaloEvent) -> None
```

---

## 📝 Implementation Steps

### Step 1: Setup & Configuration (1 day)

#### 1.1 Environment Variables
Add to `.env`:
```env
# Zalo OA Configuration
ZALO_OA_APP_ID=your_app_id
ZALO_OA_SECRET_KEY=your_secret_key
ZALO_OA_ACCESS_TOKEN=your_access_token
ZALO_OA_USER_ID=your_user_id (optional)

# Webhook
ZALO_WEBHOOK_URL=https://your-domain.com/api/v1/zalo/webhook
ZALO_API_VERSION=v3
ZALO_API_BASE_URL=https://openapi.zalo.me

# Optional
ZALO_REQUEST_TIMEOUT=30  # seconds
ZALO_MAX_RETRIES=3
```

#### 1.2 Pydantic Models
Create `src/integrations/zalo_models.py`:

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ZaloWebhookRequest(BaseModel):
    """Zalo webhook signature verification"""
    timestamp: int
    signature: str
    data: str

class ZaloEventData(BaseModel):
    """Generic Zalo event"""
    event_id: str
    timestamp: int
    sender_id: str
    recipient_id: str
    message: Dict

class ZaloTextMessage(BaseModel):
    """Text message from user"""
    text: str

class ZaloImageMessage(BaseModel):
    """Image message from user"""
    image_url: str
    width: Optional[int]
    height: Optional[int]

# Response models
class ZaloSendTextRequest(BaseModel):
    """Send text to Zalo"""
    recipient_id: str
    message_template: Dict = {"text": "..."}

class ZaloButtonTemplate(BaseModel):
    """Button/Quick reply template"""
    title: str
    buttons: List[Dict]

class ZaloCarouselTemplate(BaseModel):
    """Carousel template"""
    elements: List[Dict]
```

#### 1.3 Zalo API Client
Create `src/integrations/zalo_api.py` (150 lines):

```python
import aiohttp
import asyncio
from typing import Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ZaloAPIClient:
    def __init__(self, app_id: str, secret_key: str, access_token: str):
        self.app_id = app_id
        self.secret_key = secret_key
        self.access_token = access_token
        self.base_url = "https://openapi.zalo.me"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def send_text(self, user_id: str, text: str) -> bool:
        """Send text message to user"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "recipient": {"user_id": user_id},
                "message": {"text": text}
            }
            
            async with self.session.post(
                f"{self.base_url}/v3.0/me/message",
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                if response.status == 200:
                    logger.info(f"Message sent to {user_id}")
                    return True
                else:
                    logger.error(f"Failed to send: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    async def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Get user profile info"""
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }
            
            async with self.session.get(
                f"{self.base_url}/v3.0/{user_id}",
                headers=headers,
                timeout=30
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
```

---

### Step 2: Webhook Receiver & Security (2 days)

#### 2.1 Signature Verification
Create `src/integrations/zalo_security.py` (80 lines):

```python
import hmac
import hashlib
from typing import Tuple
import json
import logging

logger = logging.getLogger(__name__)

class ZaloWebhookSecurity:
    """Handle Zalo webhook signature verification"""
    
    @staticmethod
    def verify_signature(signature: str, body: str, secret_key: str) -> bool:
        """
        Verify Zalo webhook signature
        
        Zalo signature format:
        signature = HMAC_SHA256(data, secret_key)
        
        Args:
            signature: X-ZALO-SIGNATURE header value
            body: Raw request body
            secret_key: ZALO_OA_SECRET_KEY
            
        Returns:
            True if signature valid, False otherwise
        """
        try:
            # Compute expected signature
            expected_signature = hmac.new(
                secret_key.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare (constant time to prevent timing attacks)
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if not is_valid:
                logger.warning(f"Invalid signature: {signature[:20]}...")
            
            return is_valid
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False

    @staticmethod
    def extract_data(body: bytes, signature: str, secret_key: str) -> dict:
        """Extract and verify webhook data"""
        try:
            # Verify signature first
            if not ZaloWebhookSecurity.verify_signature(
                signature, 
                body.decode(), 
                secret_key
            ):
                raise ValueError("Signature verification failed")
            
            # Parse JSON
            data = json.loads(body)
            
            # Validate timestamp (prevent replay attacks)
            # Timestamp should be within last 5 minutes
            import time
            timestamp = data.get("timestamp", 0)
            current_time = int(time.time())
            
            if abs(current_time - timestamp) > 300:
                raise ValueError("Timestamp too old (replay attack?)")
            
            return data
        except Exception as e:
            logger.error(f"Failed to extract webhook data: {e}")
            raise
```

#### 2.2 Main Zalo Integration Class
Create `src/integrations/zalo.py` (250 lines):

```python
from fastapi import Request
from typing import Optional, Dict
import logging
from datetime import datetime
import json

from .zalo_api import ZaloAPIClient
from .zalo_security import ZaloWebhookSecurity
from .zalo_models import ZaloEventData

logger = logging.getLogger(__name__)

class ZaloOAIntegration:
    """Zalo Official Account Integration"""
    
    def __init__(
        self,
        app_id: str,
        secret_key: str,
        access_token: str,
        agent=None
    ):
        self.app_id = app_id
        self.secret_key = secret_key
        self.access_token = access_token
        self.agent = agent  # ReAct agent instance
        self.api_client = ZaloAPIClient(
            app_id=app_id,
            secret_key=secret_key,
            access_token=access_token
        )
        self.security = ZaloWebhookSecurity()

    async def handle_webhook(self, request: Request) -> Dict:
        """
        Main webhook handler
        
        Called from FastAPI route:
        @app.post("/api/v1/zalo/webhook")
        async def zalo_webhook(request: Request):
            zalo = ZaloOAIntegration(...)
            return await zalo.handle_webhook(request)
        """
        try:
            # Get signature from header
            signature = request.headers.get("X-ZALO-SIGNATURE", "")
            
            # Read body
            body = await request.body()
            
            # Verify and extract data
            event_data = self.security.extract_data(
                body,
                signature,
                self.secret_key
            )
            
            # Log event
            logger.info(f"Received Zalo event: {event_data.get('event_name')}")
            
            # Route event to handler
            event_name = event_data.get("event_name")
            handler = getattr(self, f"handle_{event_name}", None)
            
            if handler:
                await handler(event_data)
            else:
                logger.warning(f"Unknown event: {event_name}")
            
            # Always return 200 OK to Zalo (async processing)
            return {"status": "ok"}
        
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return {"status": "error", "message": str(e)}

    async def handle_user_send_text(self, event: Dict) -> None:
        """Handle user sending text message"""
        try:
            user_id = event.get("sender", {}).get("id")
            text = event.get("message", {}).get("text")
            
            if not user_id or not text:
                logger.warning("Invalid message data")
                return
            
            logger.info(f"Text from {user_id}: {text}")
            
            # Process with agent
            response = await self._get_agent_response(
                user_id=user_id,
                message_text=text
            )
            
            # Send back to Zalo
            await self.send_text(user_id, response)
        
        except Exception as e:
            logger.error(f"Error handling text message: {e}")

    async def handle_user_send_image(self, event: Dict) -> None:
        """Handle user sending image"""
        try:
            user_id = event.get("sender", {}).get("id")
            image_url = event.get("message", {}).get("image")
            
            logger.info(f"Image from {user_id}: {image_url}")
            
            # Could add image processing here
            # For now, just acknowledge
            await self.send_text(
                user_id,
                "Thanks for the image! I received it but can't process images yet."
            )
        
        except Exception as e:
            logger.error(f"Error handling image: {e}")

    async def _get_agent_response(
        self,
        user_id: str,
        message_text: str
    ) -> str:
        """Get response from ReAct agent"""
        try:
            # Call agent with platform context
            if self.agent:
                response = await self.agent.process(
                    message=message_text,
                    platform="zalo",
                    user_id=user_id
                )
                return response
            else:
                return "Sorry, agent not available."
        
        except Exception as e:
            logger.error(f"Agent error: {e}")
            return f"Error: {str(e)}"

    async def send_text(self, user_id: str, text: str) -> bool:
        """Send text message through Zalo"""
        try:
            async with self.api_client as client:
                return await client.send_text(user_id, text)
        except Exception as e:
            logger.error(f"Failed to send text: {e}")
            return False

    async def send_template(
        self,
        user_id: str,
        template_type: str,
        data: Dict
    ) -> bool:
        """Send template message (buttons, carousel, etc.)"""
        # Implementation for buttons, carousel, etc.
        # TBD based on exact Zalo template format
        pass
```

---

### Step 3: FastAPI Integration (1 day)

#### 3.1 Update `src/main.py`

Add to FastAPI app:

```python
from src.integrations.zalo import ZaloOAIntegration
from config.settings import (
    ZALO_OA_APP_ID,
    ZALO_OA_SECRET_KEY,
    ZALO_OA_ACCESS_TOKEN
)

# Initialize Zalo integration
zalo_integration = ZaloOAIntegration(
    app_id=ZALO_OA_APP_ID,
    secret_key=ZALO_OA_SECRET_KEY,
    access_token=ZALO_OA_ACCESS_TOKEN,
    agent=agent  # Pass ReAct agent instance
)

# Add webhook route
@app.post("/api/v1/zalo/webhook")
async def zalo_webhook(request: Request):
    """
    Zalo OA webhook endpoint
    
    Receives events from Zalo Official Account
    """
    return await zalo_integration.handle_webhook(request)

# Optional: Add Zalo verification endpoint (GET)
@app.get("/api/v1/zalo/webhook")
async def zalo_verify(request: Request):
    """
    Zalo webhook verification
    Zalo may send GET request to verify webhook
    """
    return {"status": "ok"}
```

#### 3.2 Update `config/settings.py`

Add Zalo configuration:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Zalo OA Configuration
    ZALO_OA_APP_ID: str = ""
    ZALO_OA_SECRET_KEY: str = ""
    ZALO_OA_ACCESS_TOKEN: str = ""
    ZALO_API_VERSION: str = "v3"
    ZALO_API_BASE_URL: str = "https://openapi.zalo.me"
    ZALO_REQUEST_TIMEOUT: int = 30
    ZALO_MAX_RETRIES: int = 3
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

### Step 4: Testing (2 days)

#### 4.1 Unit Tests
Create `tests/test_zalo_integration.py`:

```python
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import json
import time
import hmac
import hashlib

from src.integrations.zalo import ZaloOAIntegration
from src.integrations.zalo_security import ZaloWebhookSecurity

class TestZaloWebhookSecurity:
    """Test Zalo webhook signature verification"""
    
    def test_verify_valid_signature(self):
        """Valid signature should return True"""
        secret = "test_secret"
        body = "test_body"
        
        # Compute correct signature
        signature = hmac.new(
            secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        
        security = ZaloWebhookSecurity()
        assert security.verify_signature(signature, body, secret) is True
    
    def test_verify_invalid_signature(self):
        """Invalid signature should return False"""
        security = ZaloWebhookSecurity()
        assert security.verify_signature("wrong", "body", "secret") is False
    
    def test_replay_attack_prevention(self):
        """Old timestamp should be rejected"""
        # TBD: Test replay attack prevention
        pass

class TestZaloOAIntegration:
    """Test Zalo OA Integration"""
    
    @pytest.fixture
    def zalo_integration(self):
        """Create test integration"""
        return ZaloOAIntegration(
            app_id="test_id",
            secret_key="test_secret",
            access_token="test_token",
            agent=AsyncMock()
        )
    
    @pytest.mark.asyncio
    async def test_handle_text_message(self, zalo_integration):
        """Test handling text message"""
        # TBD: Complete test
        pass
    
    @pytest.mark.asyncio
    async def test_send_text(self, zalo_integration):
        """Test sending text message"""
        # TBD: Complete test
        pass

# More tests...
```

#### 4.2 Integration Tests

Test with Zalo API Tester (manual):

```
1. Zalo Developer Portal → Webhook Tester
2. Send test event:
   {
     "event_name": "user_send_text",
     "timestamp": 1234567890,
     "sender": {"id": "123456789"},
     "message": {"text": "Hello"}
   }
3. Verify webhook receives and processes
4. Verify response sent back to test interface
```

---

### Step 5: Documentation (1 day)

Create `ZALO_SETUP.md`:
- Developer account setup
- Creating OA app
- Getting credentials
- Configuring webhook
- Testing

---

## 📁 File Structure

```
src/
├── integrations/
│   ├── __init__.py
│   ├── zalo.py              (250 lines) - Main integration
│   ├── zalo_api.py          (150 lines) - API client
│   ├── zalo_security.py     (80 lines)  - Signature verification
│   ├── zalo_models.py       (100 lines) - Pydantic models
│   ├── zalo_events.py       (50 lines)  - Event definitions
│   └── base.py              (existing)  - Integration base class
├── main.py                  (updated)   - Add Zalo routes
└── ...

config/
└── settings.py              (updated)   - Add ZALO_* vars

tests/
└── test_zalo_integration.py (200+ lines) - Zalo tests

docs/
└── ZALO_SETUP.md            (new)       - Setup guide
```

---

## 📊 Effort Estimate

| Task | Days | Notes |
|------|------|-------|
| Setup & Config | 0.5 | Env vars, models |
| Security & Signature | 1.5 | Verify, timestamp |
| Webhook Receiver | 1 | Event routing |
| API Client | 1 | Send/get methods |
| FastAPI Integration | 0.5 | Route setup |
| Testing | 2 | Unit + integration |
| Documentation | 1 | Guide + examples |
| **TOTAL** | **7-8 days** | 1 dev week |

---

## 🚀 Next Steps

1. **Approval**: Get sign-off on architecture
2. **Setup**: Get Zalo OA credentials
3. **Dev**: Implement in feature branch
4. **Review**: Code review + testing
5. **Deploy**: Merge to main + release v2.1
6. **Monitor**: Track Zalo message volume

---

## 📞 Questions?

Common questions addressed in implementation:
- Q: How to test without real Zalo account?  
  A: Use Zalo API Tester in Dev Portal
  
- Q: How to handle rate limiting?  
  A: Will be added in Phase 5
  
- Q: How to send rich messages?  
  A: Template support in Phase 1B

---

**Let's build this! 🦞**


"""WhatsApp integration using Twilio."""

import logging
from typing import Dict, Optional, Tuple
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import hashlib
import hmac

logger = logging.getLogger(__name__)


class WhatsAppManager:
    """Manages WhatsApp integration with Twilio."""
    
    def __init__(self, account_sid: str, auth_token: str, whatsapp_number: str, webhook_token: str):
        self.client = Client(account_sid, auth_token)
        self.whatsapp_number = whatsapp_number
        self.webhook_token = webhook_token
        self.account_sid = account_sid
        self.auth_token = auth_token
        
    def send_message(self, to_number: str, message: str) -> Optional[Dict]:
        """Send a WhatsApp message.
        
        Args:
            to_number: Recipient's WhatsApp number (format: whatsapp:+1234567890)
            message: Message content
            
        Returns:
            Message SID if successful, None otherwise
        """
        try:
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number.replace('whatsapp:', '')}"
            
            msg = self.client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_number
            )
            
            logger.info(f"WhatsApp message sent to {to_number}: {msg.sid}")
            return {"success": True, "message_id": msg.sid}
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def verify_webhook(self, request_signature: str, request_body: str) -> bool:
        """Verify incoming webhook request is from Twilio.
        
        Args:
            request_signature: X-Twilio-Signature header value
            request_body: Raw request body
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Create the URL with Twilio's auth token
            hash_object = hmac.new(
                self.auth_token.encode(),
                msg=request_body.encode(),
                digestmod=hashlib.sha1
            )
            expected_signature = hash_object.digest()
            expected_signature_b64 = __import__('base64').b64encode(expected_signature).decode()
            
            return hmac.compare_digest(request_signature, expected_signature_b64)
            
        except Exception as e:
            logger.error(f"Error verifying webhook: {str(e)}")
            return False
    
    def parse_incoming_message(self, data: Dict) -> Tuple[Optional[str], Optional[str]]:
        """Parse incoming WhatsApp message.
        
        Args:
            data: Form data from Twilio webhook
            
        Returns:
            Tuple of (sender_number, message_text) or (None, None) if parsing fails
        """
        try:
            sender = data.get("From")
            message = data.get("Body")
            
            if sender and message:
                logger.debug(f"Parsed message from {sender}: {message[:50]}...")
                return sender, message
                
            logger.warning("Received incomplete message data")
            return None, None
            
        except Exception as e:
            logger.error(f"Error parsing incoming message: {str(e)}")
            return None, None
    
    def create_reply(self, message_body: str) -> str:
        """Create Twilio MessagingResponse for WhatsApp reply.
        
        Args:
            message_body: The reply message content
            
        Returns:
            XML response string
        """
        resp = MessagingResponse()
        resp.message(message_body)
        return str(resp)

"""Tests for WhatsApp integration."""

import pytest
from unittest.mock import Mock, patch
from src.integrations.whatsapp import WhatsAppManager


def test_whatsapp_manager_init(mock_twilio_creds):
    """Test WhatsAppManager initialization."""
    manager = WhatsAppManager(**mock_twilio_creds)
    
    assert manager.whatsapp_number == "whatsapp:+15551234567"
    assert manager.webhook_token == "test-webhook-token"


def test_parse_incoming_message(mock_twilio_creds):
    """Test parsing incoming WhatsApp message."""
    manager = WhatsAppManager(**mock_twilio_creds)
    
    data = {
        "From": "whatsapp:+15559876543",
        "Body": "Hello, ClawAgent!"
    }
    
    sender, message = manager.parse_incoming_message(data)
    
    assert sender == "whatsapp:+15559876543"
    assert message == "Hello, ClawAgent!"


def test_parse_incoming_message_missing_body(mock_twilio_creds):
    """Test parsing with missing message body."""
    manager = WhatsAppManager(**mock_twilio_creds)
    
    data = {"From": "whatsapp:+15559876543"}
    sender, message = manager.parse_incoming_message(data)
    
    assert sender is None
    assert message is None


def test_create_reply(mock_twilio_creds):
    """Test creating WhatsApp reply."""
    manager = WhatsAppManager(**mock_twilio_creds)
    
    reply = manager.create_reply("Test response")
    
    assert isinstance(reply, str)
    assert "Test response" in reply

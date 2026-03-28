"""Configuration settings for ClawAgent."""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000

    # WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str
    WHATSAPP_WEBHOOK_TOKEN: str

    # Database
    DATABASE_URL: str = "sqlite:///./clawagent.db"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Features
    ENABLE_PERSISTENCE: bool = True
    ENABLE_LOGGING: bool = True
    MAX_MESSAGE_LENGTH: int = 4000

    class Config:
        env_file = ".env"
        case_sensitive = True


# Load settings
settings = Settings()  # type: ignore

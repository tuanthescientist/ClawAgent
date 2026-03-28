"""Configuration settings for ClawAgent."""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000

    # ChatGPT via Browser (Optional)
    CHATGPT_ACCESS_TOKEN: Optional[str] = None
    
    # Local LLM (Ollama)
    USE_LOCAL_LLM: bool = False
    LOCAL_LLM_URL: str = "http://localhost:11434"
    LOCAL_LLM_MODEL: str = "mistral"

    # WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    WHATSAPP_WEBHOOK_TOKEN: Optional[str] = None

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

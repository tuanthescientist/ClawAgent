"""Configuration settings for ClawAgent."""

from typing import Any, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Application
    APP_NAME: str = "ClawAgent"
    APP_VERSION: str = "3.0.0"

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000

    # Hybrid / provider routing
    LLM_BACKEND: str = "openai"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "mixtral-8x7b-32768"

    # ChatGPT via Browser (Optional)
    CHATGPT_ACCESS_TOKEN: Optional[str] = None
    
    # Local LLM (Ollama)
    USE_LOCAL_LLM: bool = False
    LOCAL_LLM_URL: str = "http://localhost:11434"
    OLLAMA_HOST: str = "http://localhost:11434"
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
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )
    
    # Features
    ENABLE_PERSISTENCE: bool = True
    ENABLE_LOGGING: bool = True
    MAX_MESSAGE_LENGTH: int = 4000

    @field_validator("DEBUG", mode="before")
    @classmethod
    def normalize_debug(cls, value: Any) -> Any:
        """Accept common environment-style truthy/falsy strings for DEBUG."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-style compatibility helper for older code paths."""
        return getattr(self, key, default)


# Load settings
settings = Settings()  # type: ignore

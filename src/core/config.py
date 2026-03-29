"""
Configuration management for ClawAgent v3.0

Supports:
- Multiple LLM backends (OpenAI, Ollama, vLLM, Groq, LM Studio)
- Hybrid fallback configuration
- Vector memory backends (ChromaDB, Qdrant)
- Rate limiting and reliability settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from enum import Enum
import logging


class LLMBackendType(str, Enum):
    """Supported LLM backends"""
    OPENAI = "openai"
    OLLAMA = "ollama"
    VLLM = "vllm"
    GROQ = "groq"
    LM_STUDIO = "lm_studio"
    HYBRID = "hybrid"


class MemoryBackendType(str, Enum):
    """Supported memory backends"""
    IN_MEMORY = "in_memory"
    CHROMADB = "chromadb"
    QDRANT = "qdrant"


class CodeExecutionSandboxType(str, Enum):
    """Code execution sandbox types"""
    DOCKER = "docker"
    RESTRICTED = "restricted"
    DISABLED = "disabled"


class AppConfig(BaseSettings):
    """
    Application configuration with environment variable support.
    
    Example:
        config = AppConfig()
        config.LLM_BACKEND  # "hybrid"
        config.OLLAMA_MODEL  # "qwen2.5:14b"
    """

    # ==================== Core Settings ====================
    APP_NAME: str = "ClawAgent"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"  # development, staging, production

    # ==================== LLM Settings ====================
    LLM_BACKEND: LLMBackendType = LLMBackendType.OPENAI
    LLM_MODEL: str = "gpt-4-turbo"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    LLM_TOP_P: float = 1.0
    LLM_TIMEOUT_SECONDS: int = 30

    # ==================== OpenAI Settings ====================
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_ORG_ID: Optional[str] = None

    # ==================== Local LLM Settings ====================
    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:14b"
    OLLAMA_TIMEOUT: int = 60

    # vLLM
    VLLM_HOST: str = "http://localhost:8000"
    VLLM_MODEL: str = "meta-llama/Llama-2-13b-hf"
    VLLM_API_KEY: Optional[str] = None

    # LM Studio
    LM_STUDIO_HOST: str = "http://localhost:1234/v1"
    LM_STUDIO_MODEL: str = "gpt-4-turbo"

    # Groq (OpenAI compatible)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "mixtral-8x7b-32768"

    # ==================== Hybrid Backend Settings ====================
    FALLBACK_CHAIN: List[LLMBackendType] = [
        LLMBackendType.OPENAI,
        LLMBackendType.GROQ,
        LLMBackendType.OLLAMA,
    ]
    FALLBACK_RETRY_COUNT: int = 3
    FALLBACK_TIMEOUT_SECONDS: int = 30

    # ==================== Embedding Settings ====================
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536
    EMBEDDING_API_KEY: Optional[str] = None

    # ==================== Memory Settings ====================
    MEMORY_BACKEND: MemoryBackendType = MemoryBackendType.CHROMADB
    
    # ChromaDB
    CHROMADB_PATH: str = "./data/chromadb"
    CHROMADB_RESET_ON_START: bool = False
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None

    # ==================== Rate Limiting ====================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_TOKENS_PER_MINUTE: int = 90000
    RATE_LIMIT_PER_USER: bool = True

    # ==================== Circuit Breaker ====================
    CIRCUIT_BREAKER_ENABLED: bool = True
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT_SECONDS: int = 60

    # ==================== Tool Execution ====================
    TOOLS_TIMEOUT_SECONDS: int = 30
    TOOLS_MAX_RETRIES: int = 2
    
    # Code Execution
    CODE_EXECUTION_ENABLED: bool = False
    CODE_EXECUTION_SANDBOX: CodeExecutionSandboxType = CodeExecutionSandboxType.DISABLED
    CODE_EXECUTION_MAX_TIME: int = 10
    
    # File System
    FILESYSTEM_ROOT: str = "./workspace"
    FILESYSTEM_RESTRICTED: bool = True
    FILESYSTEM_MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Web Browser
    BROWSER_HEADLESS: bool = True
    BROWSER_TIMEOUT_SECONDS: int = 30
    BROWSER_MAX_TABS: int = 5

    # ==================== Security ====================
    SECURITY_ENABLE_INPUT_SANITIZATION: bool = True
    SECURITY_ENABLE_PROMPT_INJECTION_DETECTION: bool = True
    SECURITY_ENABLE_RATE_LIMITING: bool = True
    SECURITY_MAX_INPUT_LENGTH: int = 10000
    SECURITY_ENABLE_ENCRYPTION: bool = False

    # ==================== Logging ====================
    LOGGING_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOGGING_FILE: Optional[str] = None
    LOGGING_STRUCTURED: bool = True

    # ==================== API Settings ====================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    API_TIMEOUT: int = 60

    # ==================== Webhook Settings ====================
    WEBHOOK_TIMEOUT: int = 30
    WEBHOOK_RETRY_COUNT: int = 3

    # ==================== Database ====================
    DATABASE_URL: Optional[str] = None
    DATABASE_ECHO: bool = False

    # ==================== Monitoring ====================
    MONITORING_ENABLED: bool = True
    MONITORING_PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global config instance
try:
    config = AppConfig()
    logging.info(
        f"Config loaded: LLM_BACKEND={config.LLM_BACKEND}, "
        f"MEMORY_BACKEND={config.MEMORY_BACKEND}"
    )
except Exception as e:
    logging.error(f"Failed to load config: {e}")
    raise


def get_config() -> AppConfig:
    """Get global config instance"""
    return config

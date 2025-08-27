from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Conversational RAG Service"
    
    # Vector Database (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "documents"
    
    # Chat Memory (Redis)
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CHAT_PREFIX: str = "chat:"
    REDIS_SESSION_TTL: int = 3600  # 1 hour
    
    # LLM Configuration
    LLM_PROVIDER: str = "openai"  # openai, anthropic, huggingface
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    
    # LLM Model Settings
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    HUGGINGFACE_MODEL: str = "microsoft/DialoGPT-medium"
    
    # RAG Settings
    MAX_CONTEXT_LENGTH: int = 4000
    SIMILARITY_THRESHOLD: float = 0.7
    MAX_RETRIEVED_CHUNKS: int = 5
    
    # Email Service (Gmail SMTP)
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: Optional[str] = None
    
    # Interview Settings
    DEFAULT_INTERVIEW_DURATION: int = 60  # minutes
    INTERVIEW_REMINDER_HOURS: int = 24
    
    class Config:
        env_file = ".env"

settings = Settings()
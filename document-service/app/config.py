from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Document Service"
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "document_db"
    
    # Vector Database
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    
    # File Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Hugging-face API
    USE_HUGGINGFACE_API: bool = True
    HUGGINGFACE_API_KEY: Optional[str] = None
    API_EMBEDDING_MODEL_URL: str = "https://router.huggingface.co/hf-inference/models/{model}/pipeline/feature-extraction"
    
    class Config:
        env_file = ".env"

settings = Settings()
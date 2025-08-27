from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import connect_to_redis, close_redis_connection, connect_to_qdrant
from app.api.routes.chat_routes import router as chat_router
from app.api.routes.interview_routes import router as interview_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Conversational RAG Service...")
    
    try:
        await connect_to_redis()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Redis: {e}")
        raise
    
    try:
        connect_to_qdrant()
        logger.info("✅ Qdrant connected")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant: {e}")
        raise
    
    logger.info("🎉 All services started successfully")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Conversational RAG Service...")
    await close_redis_connection()
    logger.info("👋 Goodbye!")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    description="Advanced conversational AI with RAG capabilities and interview booking",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(
    chat_router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["chat"]
)

app.include_router(
    interview_router,
    prefix=f"{settings.API_V1_STR}/interviews",
    tags=["interviews"]
)

@app.get("/")
async def root():
    return {
        "message": "Conversational RAG API",
        "version": "1.0.0",
        "status": "running",
        "docs": f"{settings.API_V1_STR}/docs",
        "features": [
            "Multi-turn conversations",
            "RAG with vector search",
            "Interview booking",
            "Email notifications",
            "Multiple LLM providers"
        ]
    }

@app.get("/health")
async def health_check():
    from app.database import db
    
    redis_status = "connected" if db.redis_client else "disconnected"
    qdrant_status = "connected" if db.qdrant_client else "disconnected"
    
    return {
        "status": "healthy",
        "service": "conversational-rag-service",
        "components": {
            "redis": redis_status,
            "qdrant": qdrant_status,
            "llm_provider": settings.LLM_PROVIDER
        },
        "timestamp": "2024-01-01T00:00:00Z"  # Will be current time in real implementation
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
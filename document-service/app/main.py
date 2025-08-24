from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, connect_to_qdrant
from app.api.routes.document_routes import router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Document Service...")
    try:
        await connect_to_mongo()
        logger.info("✅ MongoDB connected")
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
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
    logger.info("🛑 Shutting down Document Service...")
    await close_mongo_connection()
    logger.info("👋 Goodbye!")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes with proper prefix
app.include_router(
    router,
    prefix=f"{settings.API_V1_STR}/documents",
    tags=["documents"]
)

@app.get("/")
async def root():
    return {
        "message": "Document Service API", 
        "version": "1.0.0",
        "status": "running",
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    from app.database import db
    
    mongo_status = "connected" if db.client else "disconnected"
    qdrant_status = "connected" if db.qdrant_client else "disconnected"
    
    return {
        "status": "healthy", 
        "service": "document-service",
        "mongodb": mongo_status,
        "qdrant": qdrant_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
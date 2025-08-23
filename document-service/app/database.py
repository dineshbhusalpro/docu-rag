from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    qdrant_client: QdrantClient = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)

async def close_mongo_connection():
    """Close database connection"""
    db.client.close()

def connect_to_qdrant():
    """Create Qdrant connection"""
    db.qdrant_client = QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY
    )
    
    # Create collection if it doesn't exist
    try:
        collections = db.qdrant_client.get_collections()
        if "documents" not in [col.name for col in collections.collections]:
            db.qdrant_client.create_collection(
                collection_name="documents",
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
    except Exception as e:
        print(f"Error setting up Qdrant: {e}")

def get_database():
    return db.client[settings.DATABASE_NAME]
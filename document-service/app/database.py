from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    qdrant_client: QdrantClient = None

db = Database()

async def connect_to_mongo():
    """Create async database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        # Test connection
        await db.client.admin.command('ping')
        print("✅ Connected to MongoDB (async)")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("🔌 Closed MongoDB connection")

def connect_to_qdrant():
    """Create Qdrant connection"""
    try:
        db.qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY,
            timeout=30
        )
        
        # Test connection and create collection if needed
        collections = db.qdrant_client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        if "documents" not in collection_names:
            db.qdrant_client.create_collection(
                collection_name="documents",
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
            print("✅ Created Qdrant collection: documents")
        
        print("✅ Connected to Qdrant")
    except Exception as e:
        print(f"❌ Error setting up Qdrant: {e}")
        raise

def get_database():
    """Get async database instance"""
    if not db.client:
        raise Exception("Database not connected. Call connect_to_mongo() first.")
    return db.client[settings.DATABASE_NAME]

def get_qdrant():
    """Get Qdrant client instance"""
    if not db.qdrant_client:
        raise Exception("Qdrant not connected. Call connect_to_qdrant() first.")
    return db.qdrant_client
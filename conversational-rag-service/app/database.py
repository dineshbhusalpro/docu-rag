import redis.asyncio as redis
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from app.config import settings

class Database:
    redis_client: redis.Redis = None
    qdrant_client: QdrantClient = None

db = Database()

async def connect_to_redis():
    """Create Redis connection for chat memory"""
    try:
        db.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            retry_on_timeout=True,
            socket_connect_timeout=5
        )
        await db.redis_client.ping()
        print("✅ Connected to Redis")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        raise

async def close_redis_connection():
    """Close Redis connection"""
    if db.redis_client:
        await db.redis_client.close()
        print("🔌 Closed Redis connection")

def connect_to_qdrant():
    """Create Qdrant connection for vector search"""
    try:
        db.qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            api_key=settings.QDRANT_API_KEY,
            timeout=30
        )
        
        # Test connection
        collections = db.qdrant_client.get_collections()
        print(f"✅ Connected to Qdrant ({len(collections.collections)} collections)")
    except Exception as e:
        print(f"❌ Error connecting to Qdrant: {e}")
        raise

def get_redis():
    """Get Redis client instance"""
    if not db.redis_client:
        raise Exception("Redis not connected. Call connect_to_redis() first.")
    return db.redis_client

def get_qdrant():
    """Get Qdrant client instance"""
    if not db.qdrant_client:
        raise Exception("Qdrant not connected. Call connect_to_qdrant() first.")
    return db.qdrant_client
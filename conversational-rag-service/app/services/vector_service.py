from typing import List, Dict, Any, Optional
from qdrant_client.models import Filter, FieldCondition, Range, MatchValue
from app.database import get_qdrant
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.collection_name = settings.QDRANT_COLLECTION_NAME

    def search_similar_chunks(
        self,
        query_embedding: List[float],
        document_ids: Optional[List[str]] = None,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks in the vector database"""
        try:
            qdrant_client = get_qdrant()
            
            # Build filter if document_ids specified
            query_filter = None
            if document_ids:
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(any=document_ids)
                        )
                    ]
                )
            
            # Search for similar vectors
            results = qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "content": result.payload.get("content", ""),
                    "document_id": result.payload.get("document_id", ""),
                    "chunk_index": result.payload.get("chunk_index", 0),
                    "score": result.score,
                    "start_char": result.payload.get("start_char", 0),
                    "end_char": result.payload.get("end_char", 0),
                    "metadata": result.payload.get("metadata", {})
                })
            
            logger.info(f"Found {len(formatted_results)} similar chunks")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the vector collection"""
        try:
            qdrant_client = get_qdrant()
            collection_info = qdrant_client.get_collection(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}
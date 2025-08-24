from typing import List, Dict, Any
from qdrant_client.models import PointStruct
from app.database import get_qdrant
import uuid

class VectorService:
    def store_document(self, document_id: str, chunks: List[Dict], embeddings: List[List[float]]):
        """Store document chunks in vector database"""
        try:
            qdrant_client = get_qdrant()
            points = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "document_id": document_id,
                        "chunk_index": i,
                        "content": chunk['content'],
                        "start_char": chunk['start_char'],
                        "end_char": chunk['end_char'],
                        "strategy": chunk.get('strategy', 'unknown'),
                        "metadata": chunk.get('metadata', {})
                    }
                )
                points.append(point)
            
            qdrant_client.upsert(
                collection_name="documents",
                points=points
            )
            print(f"✅ Stored {len(points)} chunks for document {document_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error storing chunks for document {document_id}: {e}")
            return False

    def search_similar(self, query_embedding: List[float], limit: int = 5):
        """Search for similar chunks"""
        try:
            qdrant_client = get_qdrant()
            results = qdrant_client.search(
                collection_name="documents",
                query_vector=query_embedding,
                limit=limit
            )
            
            return [
                {
                    "content": result.payload["content"],
                    "document_id": result.payload["document_id"],
                    "score": result.score,
                    "chunk_index": result.payload.get("chunk_index", 0),
                    "strategy": result.payload.get("strategy", "unknown")
                }
                for result in results
            ]
            
        except Exception as e:
            print(f"❌ Error searching chunks: {e}")
            return []

    def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        try:
            qdrant_client = get_qdrant()
            # Delete points with matching document_id
            qdrant_client.delete(
                collection_name="documents",
                points_selector={
                    "filter": {
                        "must": [
                            {
                                "key": "document_id",
                                "match": {
                                    "value": document_id
                                }
                            }
                        ]
                    }
                }
            )
            print(f"✅ Deleted chunks for document {document_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting chunks for document {document_id}: {e}")
            return False
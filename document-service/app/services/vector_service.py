from typing import List, Dict, Any
from qdrant_client.models import PointStruct
from app.database import db
import uuid

class VectorService:
    async def store_document(self, document_id: str, chunks: List[Dict], embeddings: List[List[float]]):
        """Store document chunks in vector database"""
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
                    "end_char": chunk['end_char']
                }
            )
            points.append(point)
        
        db.qdrant_client.upsert(
            collection_name="documents",
            points=points
        )

    async def search_similar(self, query_embedding: List[float], limit: int = 5):
        """Search for similar chunks"""
        results = db.qdrant_client.search(
            collection_name="documents",
            query_vector=query_embedding,
            limit=limit
        )
        
        return [
            {
                "content": result.payload["content"],
                "document_id": result.payload["document_id"],
                "score": result.score
            }
            for result in results
        ]

    async def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        db.qdrant_client.delete(
            collection_name="documents",
            points_selector={"filter": {"document_id": document_id}}
        )
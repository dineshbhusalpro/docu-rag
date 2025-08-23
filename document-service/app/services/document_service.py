from typing import List, Optional
from fastapi import UploadFile, HTTPException
from bson import ObjectId
from app.database import get_database
from app.models.document_model import DocumentModel
from app.services.embedding_service import EmbeddingService
from app.services.vector_service import VectorService
from app.utils.file_utils import FileUtils
from app.utils.text_processing import TextProcessor
import os

class DocumentService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
        self.file_utils = FileUtils()
        self.text_processor = TextProcessor()

    async def upload_document(
        self, 
        file: UploadFile, 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200,
        chunking_strategy: str = "fixed"
    ):
        """Upload and process document with specified chunking strategy"""
        # Validate file
        self.file_utils.validate_file(file)
        
        # Validate chunking strategy
        valid_strategies = ["fixed", "sentence", "semantic", "paragraph", "hybrid"]
        if chunking_strategy not in valid_strategies:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid chunking strategy. Must be one of: {valid_strategies}"
            )
        
        # Save file
        file_path = await self.file_utils.save_file(file)
        
        try:
            # Extract text
            content = await self.text_processor.extract_text(file_path)
            
            # Create document record
            document = DocumentModel(
                filename=file.filename,
                file_path=file_path,
                file_size=file.size,
                content=content,
                status="processing"
            )
            
            # Save to database
            db = get_database()
            result = await db.documents.insert_one(document.model_dump(by_alias=True))
            document_id = str(result.inserted_id)
            
            # Process in background (simplified - in production use Celery)
            await self._process_document(document_id, content, chunk_size, chunk_overlap, chunking_strategy)
            
            return {
                "document_id": document_id, 
                "status": "uploaded", 
                "message": f"Document processing started with {chunking_strategy} chunking strategy"
            }
            
        except Exception as e:
            # Clean up file on error
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

    async def _process_document(
        self, 
        document_id: str, 
        content: str, 
        chunk_size: int, 
        chunk_overlap: int, 
        chunking_strategy: str
    ):
        """Process document into chunks and embeddings"""
        try:
            # Create chunks using specified strategy
            chunks = self.text_processor.create_chunks(
                text=content, 
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap,
                strategy=chunking_strategy
            )
            
            # Generate embeddings
            embeddings = []
            for chunk in chunks:
                embedding = await self.embedding_service.get_embedding(chunk['content'])
                embeddings.append(embedding)
            
            # Store in vector database
            await self.vector_service.store_document(document_id, chunks, embeddings)
            
            # Update document status with chunking metadata
            db = get_database()
            await db.documents.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {
                    "status": "completed", 
                    "chunks": chunks,
                    "chunking_metadata": {
                        "strategy": chunking_strategy,
                        "total_chunks": len(chunks),
                        "avg_chunk_size": sum(len(c['content']) for c in chunks) / len(chunks) if chunks else 0,
                        "chunk_size_target": chunk_size,
                        "chunk_overlap": chunk_overlap
                    }
                }}
            )
            
        except Exception as e:
            # Update status to failed
            db = get_database()
            await db.documents.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {"status": "failed", "error": str(e)}}
            )
            raise

    async def get_document(self, document_id: str) -> Optional[DocumentModel]:
        """Get document by ID"""
        db = get_database()
        doc = await db.documents.find_one({"_id": ObjectId(document_id)})
        return DocumentModel(**doc) if doc else None

    async def list_documents(self, skip: int = 0, limit: int = 20) -> List[DocumentModel]:
        """List documents with pagination"""
        db = get_database()
        cursor = db.documents.find().skip(skip).limit(limit).sort("created_at", -1)
        documents = await cursor.to_list(length=limit)
        return [DocumentModel(**doc) for doc in documents]

    async def delete_document(self, document_id: str) -> bool:
        """Delete document and associated data"""
        try:
            # Get document first
            document = await self.get_document(document_id)
            if not document:
                return False
            
            # Delete from vector database
            await self.vector_service.delete_document(document_id)
            
            # Delete file
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            # Delete from database
            db = get_database()
            result = await db.documents.delete_one({"_id": ObjectId(document_id)})
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

    async def get_chunking_stats(self, document_id: str) -> dict:
        """Get detailed chunking statistics for a document"""
        document = await self.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not document.chunks:
            return {"message": "Document not yet processed"}
        
        chunks = document.chunks
        
        # Calculate statistics
        chunk_sizes = [len(chunk['content']) for chunk in chunks]
        strategy_counts = {}
        
        for chunk in chunks:
            strategy = chunk.get('strategy', 'unknown')
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        
        return {
            "document_id": document_id,
            "total_chunks": len(chunks),
            "chunking_strategies_used": strategy_counts,
            "chunk_size_stats": {
                "min": min(chunk_sizes) if chunk_sizes else 0,
                "max": max(chunk_sizes) if chunk_sizes else 0,
                "avg": sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
                "median": sorted(chunk_sizes)[len(chunk_sizes)//2] if chunk_sizes else 0
            },
            "content_coverage": {
                "total_characters": len(document.content),
                "chunked_characters": sum(chunk_sizes),
                "coverage_percentage": (sum(chunk_sizes) / len(document.content)) * 100 if document.content else 0
            }
        }
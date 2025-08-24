from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from app.schemas.document_schema import DocumentResponse, DocumentDetail, DocumentList, DocumentUpload
from app.services.document_service import DocumentService
from app.api.deps import get_document_service

router = APIRouter()

@router.get("/debug/system-info")
async def get_system_info():
    """Debug endpoint to check system capabilities"""
    import sys
    import os
    
    info = {
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "upload_directory_exists": os.path.exists("uploads"),
        "environment_variables": {
            "MONGODB_URL": os.getenv("MONGODB_URL", "not set"),
            "QDRANT_HOST": os.getenv("QDRANT_HOST", "not set")
        }
    }
    
    # Check library availability
    libraries = {}
    try:
        import nltk
        libraries["nltk"] = "available"
        try:
            nltk.data.find('tokenizers/punkt')
            libraries["nltk_punkt"] = "available"
        except:
            libraries["nltk_punkt"] = "missing"
    except ImportError:
        libraries["nltk"] = "missing"
    
    try:
        from sentence_transformers import SentenceTransformer
        libraries["sentence_transformers"] = "available"
    except ImportError:
        libraries["sentence_transformers"] = "missing"
    
    try:
        from sklearn.cluster import KMeans
        libraries["sklearn"] = "available"
    except ImportError:
        libraries["sklearn"] = "missing"
    
    info["libraries"] = libraries
    return info

@router.post("/debug/simple-upload", response_model=dict)
async def simple_upload_test(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service)
):
    """Simple upload test with minimal processing"""
    try:
        # Basic file validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file size
        if file.size and file.size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=413, detail="File too large")
        
        # Try to read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        return {
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type,
            "first_100_chars": content[:100].decode('utf-8', errors='ignore') if content else "",
            "status": "basic_upload_test_successful"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "status": "upload_test_failed"
        }

@router.post("/upload", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int = Query(1000, ge=100, le=4000, description="Target size for each chunk"),
    chunk_overlap: int = Query(200, ge=0, le=1000, description="Overlap between chunks"),
    chunking_strategy: str = Query("fixed", description="Chunking strategy: fixed, sentence, semantic, paragraph, hybrid"),
    embedding_provider: str = Query("huggingface_api", description="Embedding Provider: huggingface_api, local_model"),
    service: DocumentService = Depends(get_document_service)
):
    """Upload a document with specified chunking strategy"""
    try:
        return await service.upload_document(file, chunk_size, chunk_overlap, chunking_strategy, embedding_provider)
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_details = {
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "file_info": {
                "filename": getattr(file, 'filename', 'unknown'),
                "content_type": getattr(file, 'content_type', 'unknown'),
                "size": getattr(file, 'size', 'unknown')
            }
        }
        print(f"Upload error: {error_details}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/", response_model=DocumentList)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    query: str = Query(None, description="Search query for filename or content"),
    status: str = Query(None, description="Filter by document status"),
    service: DocumentService = Depends(get_document_service)
):
    """List documents with optional search and filtering"""
    try:
        if query or status:
            documents, total = await service.search_documents(query, status, skip, limit)
        else:
            documents = await service.list_documents(skip, limit)
            total = await service.count_documents()
        
        document_responses = [
            DocumentResponse(
                id=str(doc.id),
                filename=doc.filename,
                file_size=doc.file_size,
                status=doc.status,
                created_at=doc.created_at,
                total_chunks=len(doc.chunks)
            )
            for doc in documents
        ]
        
        return DocumentList(
            documents=document_responses, 
            total=total
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get document details"""
    document = await service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentDetail(
        id=str(document.id),
        filename=document.filename,
        file_size=document.file_size,
        status=document.status,
        created_at=document.created_at,
        total_chunks=len(document.chunks),
        content_preview=document.content[:500] + "..." if len(document.content) > 500 else document.content,
        chunks=document.chunks
    )

@router.get("/{document_id}/stats")
async def get_chunking_stats(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get detailed chunking statistics for a document"""
    return await service.get_chunking_stats(document_id)

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Delete a document"""
    success = await service.delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}

@router.get("/{document_id}/status")
async def get_document_status(
    document_id: str,
    service: DocumentService = Depends(get_document_service)
):
    """Get document processing status"""
    document = await service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "document_id": document_id,
        "status": document.status,
        "total_chunks": len(document.chunks)
    }

@router.get("/strategies/available")
async def get_available_chunking_strategies():
    """Get list of available chunking strategies with descriptions"""
    return {
        "strategies": {
            "fixed": {
                "name": "Fixed Size",
                "description": "Split text into fixed-size chunks with configurable overlap",
                "best_for": "General purpose, consistent chunk sizes",
                "parameters": ["chunk_size", "chunk_overlap"]
            },
            "sentence": {
                "name": "Sentence-Based",
                "description": "Respect sentence boundaries while maintaining target chunk size",
                "best_for": "Maintaining sentence integrity, better readability",
                "parameters": ["target_size", "overlap"]
            },
            "semantic": {
                "name": "Semantic Clustering",
                "description": "Group sentences by semantic similarity using embeddings",
                "best_for": "Maintaining topical coherence, better for Q&A",
                "parameters": ["max_chunks"]
            },
            "paragraph": {
                "name": "Paragraph-Based",
                "description": "Split by paragraphs while respecting size limits",
                "best_for": "Maintaining document structure, formal documents",
                "parameters": ["target_size", "overlap"]
            },
            "hybrid": {
                "name": "Hybrid Approach",
                "description": "Combines semantic clustering with size-based splitting",
                "best_for": "Best of both worlds - coherence and size control",
                "parameters": ["chunk_size", "chunk_overlap"]
            }
        }
    }

@router.get("/{document_id}/chunks/{chunk_index}")
async def get_chunk_detail(
    document_id: str,
    chunk_index: int,
    service: DocumentService = Depends(get_document_service)
):
    """Get detailed information about a specific chunk"""
    document = await service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if chunk_index >= len(document.chunks) or chunk_index < 0:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    chunk = document.chunks[chunk_index]
    
    # Add additional chunk analysis
    chunk_analysis = {
        "chunk_index": chunk_index,
        "content": chunk["content"],
        "start_char": chunk["start_char"],
        "end_char": chunk["end_char"],
        "strategy": chunk.get("strategy", "unknown"),
        "metadata": chunk.get("metadata", {}),
        "analysis": {
            "character_count": len(chunk["content"]),
            "word_count": len(chunk["content"].split()),
            "sentence_count": len([s for s in chunk["content"].split('.') if s.strip()]),
            "paragraph_count": len([p for p in chunk["content"].split('\n\n') if p.strip()])
        }
    }
    
    return chunk_analysis

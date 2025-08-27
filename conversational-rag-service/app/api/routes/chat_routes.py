from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas.chat_schema import (
    ChatRequest, 
    ChatResponse, 
    ConversationListResponse,
    ConversationHistoryResponse
)
from app.services.rag_service import RAGService
from app.services.memory_service import MemoryService
from app.services.vector_service import VectorService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest):
    """Send a message and get AI response with RAG capabilities"""
    try:
        rag_service = RAGService()
        
        result = await rag_service.process_chat_message(
            user_message=request.message,
            conversation_id=request.conversation_id,
            document_ids=request.document_ids,
            use_rag=request.use_rag,
            max_context_chunks=request.max_context_chunks
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List active conversations"""
    try:
        memory_service = MemoryService()
        conversation_ids = await memory_service.get_active_conversations(limit + offset)
        
        # Apply pagination
        paginated_ids = conversation_ids[offset:offset + limit]
        
        conversations = []
        for conv_id in paginated_ids:
            # Get basic info for each conversation
            messages = await memory_service.get_conversation_history(conv_id, limit=1)
            if messages:
                conversations.append({
                    "conversation_id": conv_id,
                    "last_message": messages[-1],
                    "last_activity": messages[-1]["timestamp"]
                })
        
        # Count active conversations
        active_count = len(conversation_ids)
        
        return ConversationListResponse(
            conversations=conversations,
            total=len(conversations),
            active_conversations=active_count
        )
        
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """Get conversation history"""
    try:
        memory_service = MemoryService()
        messages = await memory_service.get_conversation_history(conversation_id, limit, offset)
        
        if not messages:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return ConversationHistoryResponse(
            conversation_id=conversation_id,
            messages=messages,
            total_messages=len(messages),
            created_at=messages[0]["timestamp"] if messages else None,
            last_activity=messages[-1]["timestamp"] if messages else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    try:
        memory_service = MemoryService()
        success = await memory_service.clear_conversation(conversation_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Conversation cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(conversation_id: str):
    """Get conversation summary"""
    try:
        rag_service = RAGService()
        summary = await rag_service.get_conversation_summary(conversation_id)
        
        if "error" in summary:
            raise HTTPException(status_code=404, detail=summary["error"])
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/vector-info")
async def get_vector_database_info():
    """Get vector database information for debugging"""
    try:
        vector_service = VectorService()
        info = vector_service.get_collection_info()
        return info
        
    except Exception as e:
        logger.error(f"Error getting vector info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    session_id: Optional[str] = Field(None, description="Session ID for memory")
    use_rag: bool = Field(default=True, description="Whether to use RAG for context")
    document_ids: Optional[List[str]] = Field(None, description="Specific document IDs to search")
    max_context_chunks: int = Field(default=5, ge=1, le=10, description="Maximum context chunks to retrieve")

class ChatResponse(BaseModel):
    message_id: str
    conversation_id: str
    response: str
    retrieved_chunks: Optional[List[Dict[str, Any]]] = None
    total_chunks_found: int = 0
    processing_time_ms: int
    timestamp: datetime

class ConversationListResponse(BaseModel):
    conversations: List[Dict[str, Any]]
    total: int
    active_conversations: int

class ConversationHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]
    total_messages: int
    created_at: datetime
    last_activity: datetime
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ConversationCreateRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Custom session ID")
    user_id: Optional[str] = Field(None, description="User identifier")
    rag_enabled: bool = Field(default=True, description="Enable RAG for this conversation")
    document_filter: Optional[List[str]] = Field(None, description="Specific documents to search")
    max_context_chunks: int = Field(default=5, ge=1, le=10)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ConversationResponse(BaseModel):
    conversation_id: str
    session_id: str
    status: str
    message: str
    created_at: datetime
    settings: Dict[str, Any]

class ConversationUpdateRequest(BaseModel):
    rag_enabled: Optional[bool] = None
    document_filter: Optional[List[str]] = None
    max_context_chunks: Optional[int] = Field(None, ge=1, le=10)
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

class ConversationSettingsResponse(BaseModel):
    conversation_id: str
    rag_enabled: bool
    max_context_chunks: int
    similarity_threshold: float
    document_filter: Optional[List[str]]
    metadata: Dict[str, Any]

class ConversationAnalyticsResponse(BaseModel):
    conversation_id: str
    analytics: Dict[str, Any]
    generated_at: datetime

class MessageFeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = Field(None, max_length=1000)
    feedback_type: Optional[str] = None

class ConversationExportRequest(BaseModel):
    format: str = Field(default="json", description="Export format: json, csv, txt")
    include_metadata: bool = Field(default=True)
    include_chunks: bool = Field(default=False, description="Include retrieved chunks in export")

class ConversationSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Search query")
    user_id: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[str] = None
    has_activity_since: Optional[datetime] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
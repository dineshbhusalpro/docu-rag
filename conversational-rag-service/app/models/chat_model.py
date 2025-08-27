from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessageModel(BaseModel):
    message_id: str = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="Associated conversation ID")
    session_id: Optional[str] = Field(None, description="Session identifier")
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # RAG specific fields
    query_embedding: Optional[List[float]] = Field(None, description="Query embedding vector")
    retrieved_chunks: Optional[List[Dict[str, Any]]] = Field(None, description="RAG retrieved chunks")
    similarity_scores: Optional[List[float]] = Field(None, description="Similarity scores for retrieved chunks")
    
    # Processing metadata
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    llm_provider: Optional[str] = Field(None, description="LLM provider used")
    model_used: Optional[str] = Field(None, description="Specific model used")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    
    # Context information
    context_length: Optional[int] = Field(None, description="Context length used")
    conversation_turn: Optional[int] = Field(None, description="Turn number in conversation")
    
    # Additional metadata
    user_id: Optional[str] = Field(None, description="User identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ChatSessionModel(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    conversation_id: str = Field(..., description="Associated conversation ID")
    user_id: Optional[str] = Field(None, description="User identifier")
    
    # Session settings
    rag_enabled: bool = Field(default=True, description="Whether RAG is enabled for this session")
    max_context_chunks: int = Field(default=5, ge=1, le=10, description="Maximum chunks to retrieve")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold")
    document_filter: Optional[List[str]] = Field(None, description="Document IDs to filter")
    
    # Session statistics
    message_count: int = Field(default=0, ge=0)
    total_tokens_used: int = Field(default=0, ge=0)
    total_processing_time_ms: int = Field(default=0, ge=0)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Session expiration time")
    
    # Session metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatFeedback(BaseModel):
    message_id: str = Field(..., description="Message being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")
    feedback_type: Optional[str] = Field(None, description="Type of feedback: helpful, accurate, relevant, etc.")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = Field(None)

class ChatAnalytics(BaseModel):
    conversation_id: str
    total_messages: int
    user_messages: int
    assistant_messages: int
    avg_response_time_ms: float
    total_tokens_used: int
    avg_similarity_score: Optional[float]
    unique_documents_referenced: int
    session_duration_minutes: float
    user_satisfaction_score: Optional[float]
    
    # Topic analysis
    main_topics: List[str] = Field(default_factory=list)
    intent_categories: List[str] = Field(default_factory=list)
    
    # Usage patterns
    peak_activity_hour: Optional[int] = None
    avg_messages_per_session: float = 0.0
    bounce_rate: float = 0.0  # Sessions with only one message
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ConversationModel(BaseModel):
    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = Field(default=0)
    context_documents: List[str] = Field(default_factory=list, description="Document IDs used in conversation")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatMessage(BaseModel):
    message_id: str = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="Associated conversation ID")
    role: str = Field(..., description="Message role: user, assistant, system")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retrieved_chunks: Optional[List[Dict[str, Any]]] = Field(None, description="RAG retrieved chunks")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ConversationSummary(BaseModel):
    conversation_id: str
    total_messages: int
    duration_minutes: float
    topics_discussed: List[str]
    documents_referenced: List[str]
    key_insights: List[str]
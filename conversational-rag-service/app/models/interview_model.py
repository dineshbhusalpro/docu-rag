from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from enum import Enum

class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class InterviewType(str, Enum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    GENERAL = "general"

class InterviewModel(BaseModel):
    interview_id: str = Field(..., description="Unique interview identifier")
    conversation_id: str = Field(..., description="Associated conversation ID")
    candidate_email: EmailStr = Field(..., description="Candidate email address")
    candidate_name: str = Field(..., description="Candidate name")
    interviewer_email: Optional[EmailStr] = Field(None, description="Interviewer email")
    interviewer_name: Optional[str] = Field(None, description="Interviewer name")
    
    # Schedule Details
    scheduled_date: datetime = Field(..., description="Interview date and time")
    duration_minutes: int = Field(default=60, description="Interview duration")
    timezone: str = Field(default="UTC", description="Timezone for interview")
    
    # Interview Details
    interview_type: InterviewType = Field(default=InterviewType.GENERAL)
    status: InterviewStatus = Field(default=InterviewStatus.SCHEDULED)
    position: Optional[str] = Field(None, description="Job position")
    requirements: List[str] = Field(default_factory=list, description="Interview requirements")
    
    # Meeting Details
    meeting_link: Optional[str] = Field(None, description="Video call link")
    meeting_room: Optional[str] = Field(None, description="Physical meeting room")
    
    # Notifications
    reminder_sent: bool = Field(default=False)
    confirmation_sent: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Info
    notes: Optional[str] = Field(None, description="Additional notes")
    feedback: Optional[str] = Field(None, description="Interview feedback")
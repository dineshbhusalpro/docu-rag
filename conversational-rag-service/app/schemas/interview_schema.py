from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class InterviewBookingRequest(BaseModel):
    candidate_email: EmailStr = Field(..., description="Candidate email")
    candidate_name: str = Field(..., min_length=1, max_length=100)
    preferred_date: datetime = Field(..., description="Preferred interview date/time")
    interview_type: str = Field(default="general", description="Type of interview")
    position: Optional[str] = Field(None, description="Job position")
    duration_minutes: int = Field(default=60, ge=15, le=180)
    timezone: str = Field(default="UTC")
    message: Optional[str] = Field(None, description="Additional message from candidate")

class InterviewResponse(BaseModel):
    interview_id: str
    status: str
    scheduled_date: datetime
    confirmation_sent: bool
    message: str

class InterviewUpdateRequest(BaseModel):
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    interviewer_email: Optional[EmailStr] = None
    interviewer_name: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None

class InterviewListResponse(BaseModel):
    interviews: List[Dict[str, Any]]
    total: int
    upcoming: int
    completed: int
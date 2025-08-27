from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from app.schemas.interview_schema import (
    InterviewBookingRequest,
    InterviewResponse,
    InterviewUpdateRequest,
    InterviewListResponse
)
from app.services.interview_service import InterviewService
from app.models.interview_model import InterviewStatus
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/book", response_model=InterviewResponse)
async def book_interview(request: InterviewBookingRequest):
    """Book a new interview"""
    try:
        interview_service = InterviewService()
        
        # Generate conversation_id (in real implementation, this might come from the chat)
        conversation_id = f"interview_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        interview = await interview_service.schedule_interview(
            conversation_id=conversation_id,
            candidate_email=request.candidate_email,
            candidate_name=request.candidate_name,
            preferred_date=request.preferred_date,
            interview_type=request.interview_type,
            position=request.position,
            duration_minutes=request.duration_minutes,
            timezone=request.timezone,
            message=request.message
        )
        
        return InterviewResponse(
            interview_id=interview.interview_id,
            status=interview.status.value,
            scheduled_date=interview.scheduled_date,
            confirmation_sent=interview.confirmation_sent,
            message="Interview scheduled successfully. Confirmation email sent."
        )
        
    except Exception as e:
        logger.error(f"Error booking interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=InterviewListResponse)
async def list_interviews(
    status: Optional[str] = Query(None, description="Filter by interview status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List interviews with optional status filter"""
    try:
        interview_service = InterviewService()
        interviews = await interview_service.list_interviews(status, limit, offset)
        
        # Convert to dict format for response
        interview_dicts = []
        for interview in interviews:
            interview_dicts.append({
                "interview_id": interview.interview_id,
                "candidate_name": interview.candidate_name,
                "candidate_email": interview.candidate_email,
                "scheduled_date": interview.scheduled_date,
                "status": interview.status.value,
                "interview_type": interview.interview_type.value,
                "position": interview.position,
                "duration_minutes": interview.duration_minutes,
                "confirmation_sent": interview.confirmation_sent,
                "reminder_sent": interview.reminder_sent
            })
        
        # Get counts by status
        all_interviews = await interview_service.list_interviews(None, 1000, 0)
        upcoming = len([i for i in all_interviews if i.status in [InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED]])
        completed = len([i for i in all_interviews if i.status == InterviewStatus.COMPLETED])
        
        return InterviewListResponse(
            interviews=interview_dicts,
            total=len(interview_dicts),
            upcoming=upcoming,
            completed=completed
        )
        
    except Exception as e:
        logger.error(f"Error listing interviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{interview_id}")
async def get_interview(interview_id: str):
    """Get interview details"""
    try:
        interview_service = InterviewService()
        interview = await interview_service.get_interview(interview_id)
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        return {
            "interview_id": interview.interview_id,
            "conversation_id": interview.conversation_id,
            "candidate_name": interview.candidate_name,
            "candidate_email": interview.candidate_email,
            "scheduled_date": interview.scheduled_date,
            "status": interview.status.value,
            "interview_type": interview.interview_type.value,
            "position": interview.position,
            "duration_minutes": interview.duration_minutes,
            "timezone": interview.timezone,
            "meeting_link": interview.meeting_link,
            "meeting_room": interview.meeting_room,
            "notes": interview.notes,
            "confirmation_sent": interview.confirmation_sent,
            "reminder_sent": interview.reminder_sent,
            "created_at": interview.created_at,
            "updated_at": interview.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{interview_id}")
async def update_interview(interview_id: str, request: InterviewUpdateRequest):
    """Update interview details"""
    try:
        interview_service = InterviewService()
        
        # Convert request to dict, excluding None values
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        updated_interview = await interview_service.update_interview(interview_id, updates)
        
        if not updated_interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        return {
            "message": "Interview updated successfully",
            "interview_id": interview_id,
            "updates": updates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{interview_id}")
async def cancel_interview(
    interview_id: str,
    reason: Optional[str] = Query(None, description="Cancellation reason")
):
    """Cancel an interview"""
    try:
        interview_service = InterviewService()
        success = await interview_service.cancel_interview(interview_id, reason)
        
        if not success:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        return {
            "message": "Interview cancelled successfully",
            "interview_id": interview_id,
            "reason": reason
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming/list")
async def get_upcoming_interviews(
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours ahead to look for interviews")
):
    """Get upcoming interviews"""
    try:
        interview_service = InterviewService()
        interviews = await interview_service.get_upcoming_interviews(hours_ahead)
        
        upcoming_list = []
        for interview in interviews:
            upcoming_list.append({
                "interview_id": interview.interview_id,
                "candidate_name": interview.candidate_name,
                "scheduled_date": interview.scheduled_date,
                "status": interview.status.value,
                "interview_type": interview.interview_type.value,
                "position": interview.position,
                "hours_until": (interview.scheduled_date - datetime.utcnow()).total_seconds() / 3600
            })
        
        return {
            "upcoming_interviews": upcoming_list,
            "count": len(upcoming_list),
            "hours_ahead": hours_ahead
        }
        
    except Exception as e:
        logger.error(f"Error getting upcoming interviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reminders/send")
async def send_interview_reminders():
    """Send reminders for upcoming interviews"""
    try:
        interview_service = InterviewService()
        sent_count = await interview_service.send_interview_reminders()
        
        return {
            "message": f"Sent {sent_count} interview reminders",
            "reminders_sent": sent_count
        }
        
    except Exception as e:
        logger.error(f"Error sending reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))
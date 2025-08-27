from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime, timedelta
from app.models.interview_model import InterviewModel, InterviewStatus
from app.services.email_service import EmailService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class InterviewService:
    def __init__(self):
        self.email_service = EmailService()
        self.interviews_store = {}  # In production, use a proper database

    async def schedule_interview(
        self,
        conversation_id: str,
        candidate_email: str,
        candidate_name: str,
        preferred_date: datetime,
        interview_type: str = "general",
        position: Optional[str] = None,
        duration_minutes: int = 60,
        timezone: str = "UTC",
        message: Optional[str] = None
    ) -> InterviewModel:
        """Schedule a new interview"""
        try:
            # Create interview record
            interview = InterviewModel(
                interview_id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                candidate_email=candidate_email,
                candidate_name=candidate_name,
                scheduled_date=preferred_date,
                interview_type=interview_type,
                position=position,
                duration_minutes=duration_minutes,
                timezone=timezone,
                notes=message
            )
            
            # Store interview (in production, save to database)
            self.interviews_store[interview.interview_id] = interview
            
            # Send confirmation email
            confirmation_sent = await self.email_service.send_interview_confirmation(interview)
            interview.confirmation_sent = confirmation_sent
            
            logger.info(f"Scheduled interview {interview.interview_id} for {candidate_email}")
            return interview
            
        except Exception as e:
            logger.error(f"Error scheduling interview: {e}")
            raise Exception(f"Failed to schedule interview: {str(e)}")

    async def update_interview(
        self,
        interview_id: str,
        updates: Dict[str, Any]
    ) -> Optional[InterviewModel]:
        """Update interview details"""
        try:
            interview = self.interviews_store.get(interview_id)
            if not interview:
                return None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(interview, field):
                    setattr(interview, field, value)
            
            interview.updated_at = datetime.utcnow()
            
            # Send update notification if status changed
            if "status" in updates:
                await self.email_service.send_interview_update(interview, updates)
            
            logger.info(f"Updated interview {interview_id}")
            return interview
            
        except Exception as e:
            logger.error(f"Error updating interview: {e}")
            return None

    async def cancel_interview(
        self,
        interview_id: str,
        reason: Optional[str] = None
    ) -> bool:
        """Cancel an interview"""
        try:
            interview = self.interviews_store.get(interview_id)
            if not interview:
                return False
            
            interview.status = InterviewStatus.CANCELLED
            interview.updated_at = datetime.utcnow()
            if reason:
                interview.notes = f"{interview.notes or ''}\nCancellation reason: {reason}".strip()
            
            # Send cancellation email
            await self.email_service.send_interview_cancellation(interview, reason)
            
            logger.info(f"Cancelled interview {interview_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling interview: {e}")
            return False

    async def get_interview(self, interview_id: str) -> Optional[InterviewModel]:
        """Get interview by ID"""
        return self.interviews_store.get(interview_id)

    async def list_interviews(
        self,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[InterviewModel]:
        """List interviews with optional filtering"""
        try:
            interviews = list(self.interviews_store.values())
            
            # Filter by status if provided
            if status:
                interviews = [i for i in interviews if i.status == status]
            
            # Sort by scheduled date
            interviews.sort(key=lambda x: x.scheduled_date)
            
            # Apply pagination
            return interviews[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error listing interviews: {e}")
            return []

    async def get_upcoming_interviews(self, hours_ahead: int = 24) -> List[InterviewModel]:
        """Get interviews scheduled within the next N hours"""
        try:
            now = datetime.utcnow()
            cutoff_time = now + timedelta(hours=hours_ahead)
            
            upcoming = []
            for interview in self.interviews_store.values():
                if (interview.status in [InterviewStatus.SCHEDULED, InterviewStatus.CONFIRMED] and
                    now <= interview.scheduled_date <= cutoff_time):
                    upcoming.append(interview)
            
            return sorted(upcoming, key=lambda x: x.scheduled_date)
            
        except Exception as e:
            logger.error(f"Error getting upcoming interviews: {e}")
            return []

    async def send_interview_reminders(self) -> int:
        """Send reminders for upcoming interviews"""
        try:
            reminder_hours = settings.INTERVIEW_REMINDER_HOURS
            upcoming = await self.get_upcoming_interviews(reminder_hours)
            
            sent_count = 0
            for interview in upcoming:
                if not interview.reminder_sent:
                    success = await self.email_service.send_interview_reminder(interview)
                    if success:
                        interview.reminder_sent = True
                        sent_count += 1
            
            logger.info(f"Sent {sent_count} interview reminders")
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending reminders: {e}")
            return 0
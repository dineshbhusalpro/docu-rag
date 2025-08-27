import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from app.models.interview_model import InterviewModel
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL or settings.SMTP_USERNAME

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP"""
        try:
            if not all([self.username, self.password, self.from_email]):
                logger.warning("Email service not properly configured")
                return False

            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email

            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def send_interview_confirmation(self, interview: InterviewModel) -> bool:
        """Send interview confirmation email"""
        try:
            subject = f"Interview Scheduled - {interview.position or 'Position'}"
            
            body = f"""Dear {interview.candidate_name},

Thank you for your interest! I'm pleased to confirm that your interview has been scheduled.

Interview Details:
- Date & Time: {interview.scheduled_date.strftime('%Y-%m-%d %H:%M')} ({interview.timezone})
- Duration: {interview.duration_minutes} minutes
- Type: {interview.interview_type.title()}
- Position: {interview.position or 'General Interview'}

{f'Meeting Link: {interview.meeting_link}' if interview.meeting_link else ''}
{f'Meeting Room: {interview.meeting_room}' if interview.meeting_room else ''}

{f'Additional Notes: {interview.notes}' if interview.notes else ''}

Please reply to confirm your attendance. If you need to reschedule, please let us know at least 24 hours in advance.

We look forward to speaking with you!

Best regards,
Interview Team
"""

            html_body = f"""
            <html>
            <body>
                <h2>Interview Confirmation</h2>
                <p>Dear {interview.candidate_name},</p>
                <p>Thank you for your interest! I'm pleased to confirm that your interview has been scheduled.</p>
                
                <h3>Interview Details:</h3>
                <ul>
                    <li><strong>Date & Time:</strong> {interview.scheduled_date.strftime('%Y-%m-%d %H:%M')} ({interview.timezone})</li>
                    <li><strong>Duration:</strong> {interview.duration_minutes} minutes</li>
                    <li><strong>Type:</strong> {interview.interview_type.title()}</li>
                    <li><strong>Position:</strong> {interview.position or 'General Interview'}</li>
                    {f'<li><strong>Meeting Link:</strong> <a href="{interview.meeting_link}">{interview.meeting_link}</a></li>' if interview.meeting_link else ''}
                    {f'<li><strong>Meeting Room:</strong> {interview.meeting_room}</li>' if interview.meeting_room else ''}
                </ul>
                
                {f'<p><strong>Additional Notes:</strong> {interview.notes}</p>' if interview.notes else ''}
                
                <p>Please reply to confirm your attendance. If you need to reschedule, please let us know at least 24 hours in advance.</p>
                
                <p>We look forward to speaking with you!</p>
                
                <p>Best regards,<br>Interview Team</p>
            </body>
            </html>
            """

            return await self._send_email(interview.candidate_email, subject, body, html_body)

        except Exception as e:
            logger.error(f"Error sending interview confirmation: {e}")
            return False

    async def send_interview_reminder(self, interview: InterviewModel) -> bool:
        """Send interview reminder email"""
        try:
            hours_until = (interview.scheduled_date - datetime.utcnow()).total_seconds() / 3600
            time_desc = f"in {int(hours_until)} hours" if hours_until > 1 else "soon"
            
            subject = f"Interview Reminder - Tomorrow at {interview.scheduled_date.strftime('%H:%M')}"
            
            body = f"""Dear {interview.candidate_name},

This is a friendly reminder about your upcoming interview {time_desc}.

Interview Details:
- Date & Time: {interview.scheduled_date.strftime('%Y-%m-%d %H:%M')} ({interview.timezone})
- Duration: {interview.duration_minutes} minutes
- Type: {interview.interview_type.title()}
- Position: {interview.position or 'General Interview'}

{f'Meeting Link: {interview.meeting_link}' if interview.meeting_link else ''}
{f'Meeting Room: {interview.meeting_room}' if interview.meeting_room else ''}

Please ensure you're available at the scheduled time. If you have any last-minute concerns, please contact us immediately.

Best regards,
Interview Team
"""

            return await self._send_email(interview.candidate_email, subject, body)

        except Exception as e:
            logger.error(f"Error sending interview reminder: {e}")
            return False

    async def send_interview_cancellation(self, interview: InterviewModel, reason: Optional[str] = None) -> bool:
        """Send interview cancellation email"""
        try:
            subject = f"Interview Cancelled - {interview.scheduled_date.strftime('%Y-%m-%d %H:%M')}"
            
            body = f"""Dear {interview.candidate_name},

We regret to inform you that your scheduled interview on {interview.scheduled_date.strftime('%Y-%m-%d %H:%M')} has been cancelled.

{f'Reason: {reason}' if reason else ''}

We apologize for any inconvenience this may cause. If you would like to reschedule, please reply to this email and we'll find a new time that works for both parties.

Thank you for your understanding.

Best regards,
Interview Team
"""

            return await self._send_email(interview.candidate_email, subject, body)

        except Exception as e:
            logger.error(f"Error sending interview cancellation: {e}")
            return False

    async def send_interview_update(self, interview: InterviewModel, updates: dict) -> bool:
        """Send interview update notification"""
        try:
            subject = f"Interview Update - {interview.scheduled_date.strftime('%Y-%m-%d %H:%M')}"
            
            update_details = []
            for field, value in updates.items():
                if field == "scheduled_date":
                    update_details.append(f"New Date & Time: {value.strftime('%Y-%m-%d %H:%M')}")
                elif field == "meeting_link":
                    update_details.append(f"Meeting Link: {value}")
                elif field == "meeting_room":
                    update_details.append(f"Meeting Room: {value}")
                elif field == "interviewer_name":
                    update_details.append(f"Interviewer: {value}")
                elif field == "status":
                    update_details.append(f"Status: {value.title()}")
            
            body = f"""Dear {interview.candidate_name},

There has been an update to your scheduled interview:

{chr(10).join(update_details)}

Current Interview Details:
- Date & Time: {interview.scheduled_date.strftime('%Y-%m-%d %H:%M')} ({interview.timezone})
- Duration: {interview.duration_minutes} minutes
- Type: {interview.interview_type.title()}
- Position: {interview.position or 'General Interview'}

{f'Meeting Link: {interview.meeting_link}' if interview.meeting_link else ''}
{f'Meeting Room: {interview.meeting_room}' if interview.meeting_room else ''}

If you have any questions about these changes, please don't hesitate to contact us.

Best regards,
Interview Team
"""

            return await self._send_email(interview.candidate_email, subject, body)

        except Exception as e:
            logger.error(f"Error sending interview update: {e}")
            return False
"""Email service for notifications"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ):
        """
        Send email
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)
        """
        try:
            logger.info(f"Sending email to {len(to_emails)} recipients")
            
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject
            
            # Add plain text part
            msg.attach(MIMEText(body, "plain"))
            
            # Add HTML part if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info("Email sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            raise
    
    async def send_validation_report(self, email: str, report_id: str):
        """Send validation report via email"""
        subject = "Звіт про валідацію етикетки"
        body = f"Ваш звіт про валідацію готовий. ID: {report_id}"
        
        # TODO: Create HTML template
        
        await self.send_email([email], subject, body)


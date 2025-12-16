"""Email sender - handles SMTP sending only."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailSender:
    """Service for sending emails via SMTP."""
    
    def __init__(self, config: dict):
        """
        Initialize email sender.
        
        Args:
            config: Dictionary with smtp_server, smtp_port, sender_email
        """
        self.smtp_server = config['smtp_server']
        self.smtp_port = config['smtp_port']
        self.sender_email = config['sender_email']
    
    def send(
        self,
        recipient: str,
        subject: str,
        html_body: Optional[str] = None,
        plain_body: Optional[str] = None
    ) -> bool:
        """
        Send email with HTML or plain text body.
        
        Args:
            recipient: Recipient email address
            subject: Email subject
            html_body: HTML email body (optional)
            plain_body: Plain text email body (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not html_body and not plain_body:
            print("✗ No email body provided")
            return False
            
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            # Attach body content
            if plain_body:
                msg.attach(MIMEText(plain_body, 'plain'))
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.sendmail(self.sender_email, recipient, msg.as_string())
            
            print(f"✓ Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            return False

"""Email tools."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from tool_registry import ToolRegistry


def send_email(to: str, subject: str, body: str, mock: bool = True) -> dict:
    """Send an email."""
    try:
        if mock:
            # Mock mode for development
            return {
                "success": True,
                "mock": True,
                "message": f"[MOCK] Email sent to {to}",
                "subject": subject,
                "body": body[:200] + "..." if len(body) > 200 else body
            }

        # Real SMTP (requires environment variables)
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        sender_email = os.getenv("EMAIL_ADDRESS")
        sender_password = os.getenv("EMAIL_PASSWORD")

        if not sender_email or not sender_password:
            return {
                "success": False,
                "error": "Email credentials not configured"
            }

        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = to

        # Add body
        part = MIMEText(body, "plain")
        message.attach(part)

        # Send
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to, message.as_string())

        return {
            "success": True,
            "message": f"Email sent to {to}",
            "subject": subject
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# Register tool
ToolRegistry.register(
    "email.send",
    send_email,
    "Send an email",
    {
        "type": "object",
        "properties": {
            "to": {"type": "string", "description": "Recipient email address"},
            "subject": {"type": "string", "description": "Email subject"},
            "body": {"type": "string", "description": "Email body"},
            "mock": {"type": "boolean", "description": "Use mock mode (default: true)"}
        },
        "required": ["to", "subject", "body"]
    }
)

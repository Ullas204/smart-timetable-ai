"""
Email utility for Smart Academic OS.

Sends emails via SMTP (SSL/TLS) with proper error handling,
input validation, and structured logging. Credentials from .env.
"""

import smtplib
import re
import os
import logging
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "0") == "1"

logger = logging.getLogger(__name__)


def _validate_email_format(email: str) -> bool:
    """Validate email format with regex."""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def _sanitize_subject(subject: str) -> str:
    """Sanitize email subject line."""
    subject = str(subject).strip()
    subject = re.sub(r'[\r\n\t]', ' ', subject)
    return subject[:200] if subject else "No Subject"


def send_email(subject: str, message: str, to_email: str):
    """Send an email via SMTP.

    Returns (success: bool, message: str).
    """
    if not EMAIL or not PASSWORD:
        logger.warning("Email not configured: missing EMAIL or EMAIL_PASSWORD")
        return False, "Email not configured — set EMAIL and EMAIL_PASSWORD in .env"

    if not _validate_email_format(to_email):
        logger.warning("Invalid recipient email format: %s", to_email[:30] if to_email else "empty")
        return False, "Invalid recipient email format"

    subject = _sanitize_subject(subject)
    message = str(message)[:10000]  # Cap message length

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        if SMTP_USE_TLS:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
                server.login(EMAIL, PASSWORD)
                server.send_message(msg)
        logger.info("Email sent to %s: %s", to_email, subject)
        return True, "Sent successfully"
    except smtplib.SMTPAuthenticationError:
        logger.error("Email authentication failed — check EMAIL_PASSWORD")
        return False, "Authentication failed — check app password"
    except smtplib.SMTPException as e:
        logger.error("SMTP error: %s", e)
        return False, f"SMTP error: {e}"
    except OSError as e:
        logger.error("Network error sending email: %s", e)
        return False, f"Network error: {e}"
    except Exception as e:
        logger.error("Unexpected email error: %s", e)
        return False, f"Email error: {e}"

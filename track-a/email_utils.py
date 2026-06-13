import smtplib
from email.mime.text import MIMEText
import os
import logging
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "0") == "1"

logger = logging.getLogger(__name__)


def send_email(subject, message, to_email):
    if not EMAIL or not PASSWORD:
        logger.warning("Email not configured: missing EMAIL or EMAIL_PASSWORD")
        return False, "Email not configured"

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email

    try:
        if SMTP_USE_TLS:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL, PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(EMAIL, PASSWORD)
                server.send_message(msg)
        logger.info(f"Email sent to {to_email}: {subject}")
        return True, "Sent successfully"
    except smtplib.SMTPAuthenticationError:
        logger.error("Email authentication failed — check EMAIL_PASSWORD")
        return False, "Authentication failed — check app password"
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False, f"SMTP error: {e}"
    except Exception as e:
        logger.error(f"Email Error: {e}")
        return False, str(e)
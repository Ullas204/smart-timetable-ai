"""
LangChain tools for Email Notifications.

Wraps notification_engine and email_utils into reusable LangChain tools.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def send_email_notification(subject: str, message: str, to_email: str = "") -> str:
    """Send an email notification to the user. Use this when the user wants to email their study plan, send a reminder, or share any information via email.

    Args:
        subject: Email subject line (e.g., "Weekly Study Plan").
        message: Email body content.
        to_email: Recipient email address. Uses the configured email if empty.
    """
    try:
        from email_utils import send_email
        from models import get_profile_value

        if not subject or not message:
            return json.dumps({"success": False, "error": "Subject and message are required."})

        if not to_email:
            to_email = get_profile_value("user_email", "")

        if not to_email:
            return json.dumps({"success": False, "error": "No email configured. Set your email in Settings."})

        success, msg = send_email(subject, message, to_email)
        logger.info("Email to %s: %s", to_email, "sent" if success else "failed")

        return json.dumps({
            "success": success,
            "message": msg,
            "to_email": to_email,
            "subject": subject
        })
    except Exception as e:
        logger.error("send_email_notification failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def send_event_notification(title: str, start: str, end: str) -> str:
    """Send an email notification about a scheduled event. Use this when the user wants to be notified about an upcoming event.

    Args:
        title: Event title.
        start: Event start time (ISO 8601).
        end: Event end time (ISO 8601).
    """
    try:
        from notification_engine import notify_event_creation

        success, msg = notify_event_creation(title, start, end)
        logger.info("Event notification for '%s': %s", title, "sent" if success else "failed")

        return json.dumps({
            "success": success,
            "message": msg,
            "event_title": title
        })
    except Exception as e:
        logger.error("send_event_notification failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


NOTIFICATION_TOOLS = [send_email_notification, send_event_notification]

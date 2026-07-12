"""
Notification engine for Smart Academic OS.

Dispatches email notifications for events and study reminders
with proper validation and logging.
"""

import logging
from email_utils import send_email
from models import get_profile_value

logger = logging.getLogger(__name__)


def send_alert(title: str, message: str):
    """Send an alert to the user's configured email."""
    email = get_profile_value("user_email", "")
    if not email:
        logger.info("No email configured for notifications")
        return False, "No email configured — set your email in Settings"
    success, msg = send_email(title, message, email)
    if not success:
        logger.warning("Notification failed: %s", msg)
    return success, msg


def notify_event_creation(title: str, start: str, end: str):
    """Send notification for new event creation."""
    return send_alert(
        "New Event Scheduled",
        f"Event: {title}\nTime: {start} to {end}"
    )


def notify_study_reminder(subject: str, time: str):
    """Send study session reminder."""
    return send_alert(
        "Study Reminder",
        f"It's time for your {subject} session starting at {time}!"
    )

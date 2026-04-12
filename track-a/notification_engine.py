from email_utils import send_email
from models import get_profile_value

def send_alert(title, message):
    email = get_profile_value("user_email", "ullasnullas204@gmail.com")
    try:
        send_email(title, message, email)
        return True
    except:
        return False

def notify_event_creation(title, start, end):
    return send_alert(
        "📅 New Event Scheduled",
        f"Event: {title}\nTime: {start} to {end}"
    )

def notify_study_reminder(subject, time):
    return send_alert(
        "🚀 Study Reminder",
        f"It's time for your {subject} session starting at {time}!"
    )

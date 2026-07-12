import datetime
import logging
from models import fetch_events, fetch_focus_logs

logger = logging.getLogger(__name__)

try:
    from google_calendar import check_conflict
    _has_google = True
except ImportError:
    _has_google = False
    def check_conflict(start, end):
        return False, None


def detect_missed_sessions():
    events = fetch_events()
    now = datetime.datetime.now()
    focus_logs = fetch_focus_logs()
    focus_dates = set()
    for log in focus_logs:
        try:
            focus_dates.add(log[1][:10] if log[1] else "")
        except (IndexError, TypeError):
            continue

    missed = []
    for event in events:
        try:
            event_time = datetime.datetime.fromisoformat(event[2])
            # Strip timezone info to compare with naive `now`
            if event_time.tzinfo is not None:
                event_time = event_time.replace(tzinfo=None)
            event_date = event_time.strftime("%Y-%m-%d")
            if event_time < now and event_date not in focus_dates:
                missed.append({
                    "id": event[0],
                    "title": event[1],
                    "scheduled_time": event[2],
                })
        except (ValueError, IndexError):
            continue

    return missed[:5]


def find_replacement_slot(duration_hours=1, days_ahead=7):
    now = datetime.datetime.now(datetime.timezone.utc)
    for day_offset in range(1, days_ahead + 1):
        for hour in range(8, 22):
            candidate_start = (now + datetime.timedelta(days=day_offset)).replace(
                hour=hour, minute=0, second=0, microsecond=0
            )
            candidate_end = candidate_start + datetime.timedelta(hours=duration_hours)
            try:
                conflict, _ = check_conflict(
                    candidate_start.isoformat() + "Z",
                    candidate_end.isoformat() + "Z"
                )
                if not conflict:
                    return candidate_start.isoformat(), candidate_end.isoformat()
            except Exception as e:
                logger.debug("Slot conflict check failed: %s", e)
                continue
    return None, None


def auto_reschedule(missed_sessions):
    rescheduled = 0
    for session in missed_sessions:
        new_start, new_end = find_replacement_slot()
        if new_start and new_end:
            from models import insert_event
            insert_event(
                f"Rescheduled: {session['title']}",
                new_start,
                new_end
            )
            rescheduled += 1

    if rescheduled:
        return f"✅ Successfully rescheduled {rescheduled} session(s). Check your calendar!"
    return "⚠️ No available slots found. Try reducing study hours or expanding your availability."

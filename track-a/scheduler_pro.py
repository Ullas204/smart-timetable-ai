"""
Scheduler Pro — advanced scheduling with conflict resolution.
"""
import datetime
import logging

from google_calendar import get_events, check_conflict

logger = logging.getLogger(__name__)


def find_free_slots(duration_hours=1, days_ahead=3):
    try:
        events = get_events()
    except Exception as e:
        logger.warning("Google Calendar access failed: %s", e)
        events = []

    now = datetime.datetime.now(datetime.timezone.utc)
    free_slots = []

    current_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)

    for _ in range(24 * days_ahead):
        start = current_time.isoformat() + "Z"
        end = (current_time + datetime.timedelta(hours=duration_hours)).isoformat() + "Z"

        conflict, _ = check_conflict(start, end)
        if not conflict:
            free_slots.append((start, end))
            if len(free_slots) >= 5:
                break

        current_time += datetime.timedelta(hours=1)

    return free_slots


def suggest_optimal_study_time(subject):
    slots = find_free_slots(duration_hours=2)
    for s, e in slots:
        dt = datetime.datetime.fromisoformat(s.replace("Z", ""))
        if 9 <= dt.hour <= 21:
            return s, e
    return slots[0] if slots else (None, None)


def resolve_conflict_pro(title, start, end):
    conflict, existing = check_conflict(start, end)
    if not conflict:
        return None, None

    alt_start, alt_end = suggest_optimal_study_time(title)
    return existing, (alt_start, alt_end)

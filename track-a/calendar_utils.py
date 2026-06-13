from models import fetch_events
from google_calendar import check_conflict as g_check_conflict
import datetime


def detect_conflict(start, end):
    events = fetch_events()

    for e in events:
        _, title, s, en = e
        if not (end <= s or start >= en):
            return True, title, "local"

    return False, None, None


def detect_all_conflicts(start, end):
    local_conflict, local_title, _ = detect_conflict(start, end)
    if local_conflict:
        return True, local_title, "local"

    try:
        g_conflict, g_title = g_check_conflict(start, end)
        if g_conflict:
            return True, g_title, "google"
    except Exception:
        pass

    return False, None, None
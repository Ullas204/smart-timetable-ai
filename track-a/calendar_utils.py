from models import fetch_events


def detect_conflict(start, end):
    events = fetch_events()

    for e in events:
        _, title, s, en = e

        if not (end <= s or start >= en):
            return True, title

    return False, None
import datetime
from models import fetch_focus_logs, fetch_tasks


def get_readiness_score(subject):
    focus_logs = fetch_focus_logs()
    tasks = fetch_tasks()
    subject_lower = subject.lower()

    total_minutes = 0
    session_count = 0
    for log in focus_logs:
        try:
            if len(log) >= 4 and subject_lower in str(log[3]).lower():
                minutes = int(log[2]) if log[2] else 0
                total_minutes += minutes
                session_count += 1
        except (ValueError, IndexError):
            continue

    completed_tasks = sum(1 for t in tasks
                         if subject_lower in t[1].lower() and t[3] == 'completed')
    pending_tasks = sum(1 for t in tasks
                       if subject_lower in t[1].lower() and t[3] != 'completed')

    score = 0
    score += min(30, total_minutes / 10)
    score += min(25, session_count * 5)
    score += min(30, completed_tasks * 10)
    score -= min(25, pending_tasks * 5)

    return max(0, min(100, score))


def get_readiness_summary():
    from db import get_subject_names
    subjects = get_subject_names() or ["Math", "Physics", "Computer Science", "History"]
    scores = {s: get_readiness_score(s) for s in subjects}
    avg = sum(scores.values()) / len(scores) if scores else 0

    if avg >= 80:
        rec = "You're well-prepared! Focus on revision and practice tests."
    elif avg >= 60:
        rec = "Good progress. Increase study hours for weaker subjects."
    elif avg >= 40:
        rec = "Needs improvement. Create a focused study plan for weak areas."
    else:
        rec = "Critical. Prioritize catching up on missed topics immediately."

    return {
        "scores": scores,
        "avg_score": avg,
        "recommendation": rec
    }

import datetime
from models import fetch_focus_logs, fetch_tasks, fetch_events


def get_completion_rate():
    tasks = fetch_tasks()
    if not tasks:
        return 100.0
    completed = sum(1 for t in tasks if t[3] == 'completed')
    return round((completed / len(tasks)) * 100, 1)


def get_study_streak():
    logs = fetch_focus_logs()
    if not logs:
        return 0

    study_dates = set()
    for log in logs:
        try:
            study_dates.add(log[1][:10] if log[1] else "")
        except (IndexError, TypeError):
            continue

    if not study_dates:
        return 0

    sorted_dates = sorted(study_dates, reverse=True)
    streak = 1
    for i in range(1, len(sorted_dates)):
        curr = datetime.datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d").date()
        prev = datetime.datetime.strptime(sorted_dates[i], "%Y-%m-%d").date()
        if (curr - prev).days == 1:
            streak += 1
        else:
            break
    return streak


def generate_report():
    logs = fetch_focus_logs()
    tasks = fetch_tasks()

    daily_minutes = {}
    for log in logs:
        try:
            log_date = log[1][:10] if log[1] else ""
            duration = int(log[2]) if log[2] else 0
            daily_minutes[log_date] = daily_minutes.get(log_date, 0) + duration
        except (ValueError, IndexError, TypeError):
            continue

    total_days = len(daily_minutes)
    total_minutes = sum(daily_minutes.values())
    avg_daily = total_minutes / max(1, total_days)

    sorted_dates = sorted(daily_minutes.keys())[-14:]
    trends = [{"date": d, "minutes": daily_minutes[d]} for d in sorted_dates]

    missed = 0
    events = fetch_events()
    now = datetime.datetime.now()
    for event in events:
        try:
            event_time = datetime.datetime.fromisoformat(event[2])
            if event_time.tzinfo is not None:
                event_time = event_time.replace(tzinfo=None)
            if event_time < now:
                date_str = event_time.strftime("%Y-%m-%d")
                if date_str not in daily_minutes:
                    missed += 1
        except (ValueError, IndexError):
            continue

    completion = get_completion_rate()
    streak = get_study_streak()

    recommendations = []
    if avg_daily < 60:
        recommendations.append("Aim for at least 1 hour of focused study daily.")
    if completion < 50:
        recommendations.append(f"Task completion is low ({completion}%). Prioritize finishing pending tasks.")
    if missed > 3:
        recommendations.append(f"You've missed {missed} sessions. Consider using the Rescheduler agent.")
    if streak >= 7:
        recommendations.append(f"Amazing {streak}-day streak! Maintain consistency.")
    elif streak >= 3:
        recommendations.append(f"Great {streak}-day streak! Try to extend it.")
    else:
        recommendations.append("Build a daily study habit. Even 30 min counts!")

    return {
        "streak": streak,
        "completion_rate": completion,
        "avg_daily_minutes": round(avg_daily, 1),
        "total_minutes": total_minutes,
        "missed_sessions": missed,
        "trends": trends,
        "recommendations": recommendations
    }

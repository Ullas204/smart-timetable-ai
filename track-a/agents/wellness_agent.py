import datetime
from models import fetch_focus_logs


def get_wellness_status():
    logs = fetch_focus_logs()
    now = datetime.datetime.now()
    today = now.strftime("%Y-%m-%d")
    week_ago = (now - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

    today_minutes = 0
    weekly_minutes = 0
    sessions_today = 0
    longest_streak = 0
    current_streak = 0
    breaks_taken = 0

    for log in logs:
        try:
            log_time = log[1][:10] if log[1] else ""
            duration = int(log[2]) if log[2] else 0

            if log_time == today:
                today_minutes += duration
                sessions_today += 1
            if log_time >= week_ago:
                weekly_minutes += duration
        except (ValueError, IndexError, TypeError):
            continue

    avg_session_len = today_minutes / max(1, sessions_today)
    energy_level = max(0, min(100, 100 - (today_minutes * 0.3)))

    if today_minutes > 0:
        breaks_taken = max(0, sessions_today - 1)

    alerts = []
    if today_minutes > 240:
        alerts.append("You've studied over 4 hours today. Take a longer break!")
    if avg_session_len > 120:
        alerts.append(f"Average session is {avg_session_len:.0f} min — consider Pomodoro technique (25 min).")
    if weekly_minutes > 2000:
        alerts.append("Weekly study load is very high. Ensure you're resting adequately.")

    recommendation = None
    if energy_level < 40:
        recommendation = "Your energy is low. Take a 30-min break, hydrate, and stretch."
    elif today_minutes < 60:
        recommendation = "Good start! Try to study at least 1 hour today for consistency."
    else:
        recommendation = "You're on a good rhythm. Keep it up!"

    return {
        "energy_level": energy_level,
        "today_minutes": today_minutes,
        "weekly_minutes": weekly_minutes,
        "sessions_today": sessions_today,
        "breaks_taken": breaks_taken,
        "avg_session_minutes": avg_session_len,
        "alerts": alerts,
        "recommendation": recommendation
    }


def get_weekly_trend():
    logs = fetch_focus_logs()
    now = datetime.datetime.now()
    daily_data = {}

    for log in logs:
        try:
            log_date = log[1][:10] if log[1] else ""
            duration = int(log[2]) if log[2] else 0
            if log_date:
                daily_data[log_date] = daily_data.get(log_date, 0) + duration
        except (ValueError, IndexError, TypeError):
            continue

    sorted_dates = sorted(daily_data.keys())[-14:]
    return [
        {"date": d, "minutes": daily_data[d]}
        for d in sorted_dates
    ]

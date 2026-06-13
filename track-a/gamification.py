from models import fetch_focus_logs, fetch_achievements
import math

def calculate_xp():
    logs = fetch_focus_logs()
    total_xp = 0
    if not logs:
        return 0
    for log in logs:
        try:
            # Points is column index 3 in focus_logs (id, start_time, duration, points, subject)
            points = int(log[3]) if len(log) > 3 else 0
            total_xp += points
        except (ValueError, TypeError, IndexError):
            continue
    return total_xp

def get_user_level():
    xp = calculate_xp()
    try:
        level = 1 + math.floor(math.sqrt(xp / 10))
    except:
        level = 1
    return level

def get_progress_to_next_level():
    xp = calculate_xp()
    level = get_user_level()
    try:
        current_level_xp = 10 * ((level - 1) ** 2)
        next_level_xp = 10 * (level ** 2)
        if next_level_xp == current_level_xp:
            return 0.0
        progress = (xp - current_level_xp) / (next_level_xp - current_level_xp)
        return min(1.0, max(0.0, progress))
    except:
        return 0.0

def get_achievements():
    try:
        achievements = fetch_achievements()
        return achievements if achievements else []
    except:
        return []

def debug_logs():
    logs = fetch_focus_logs()
    print("DEBUG LOGS:", logs)

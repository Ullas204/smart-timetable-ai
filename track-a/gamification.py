<<<<<<< HEAD
from models import fetch_focus_logs, fetch_achievements

def calculate_xp():
    logs = fetch_focus_logs()
    total_xp = sum(log[4] for log in logs) if logs else 0
    return total_xp

def get_user_level():
    xp = calculate_xp()
    # Level = 1 + floor(sqrt(xp/10))
    import math
    level = 1 + math.floor(math.sqrt(xp / 10))
    return level

def get_progress_to_next_level():
    xp = calculate_xp()
    level = get_user_level()
    current_level_xp = 10 * ((level - 1) ** 2)
    next_level_xp = 10 * (level ** 2)
    
    if next_level_xp == current_level_xp:
        return 0
        
    progress = (xp - current_level_xp) / (next_level_xp - current_level_xp)
    return min(1.0, max(0.0, progress))
=======
# gamification.py

from models import fetch_focus_logs, fetch_achievements
import math


# ---------------- XP CALCULATION ----------------
def calculate_xp():
    logs = fetch_focus_logs()

    total_xp = 0

    if not logs:
        return 0

    for log in logs:
        try:
            # ✅ Always take LAST column (points) safely
            points = int(log[-1])
            total_xp += points
        except (ValueError, TypeError, IndexError):
            # Skip corrupted rows safely
            continue

    return total_xp


# ---------------- LEVEL SYSTEM ----------------
def get_user_level():
    xp = calculate_xp()

    try:
        level = 1 + math.floor(math.sqrt(xp / 10))
    except:
        level = 1  # fallback safe level

    return level


# ---------------- PROGRESS BAR ----------------
def get_progress_to_next_level():
    xp = calculate_xp()
    level = get_user_level()

    try:
        current_level_xp = 10 * ((level - 1) ** 2)
        next_level_xp = 10 * (level ** 2)

        if next_level_xp == current_level_xp:
            return 0.0

        progress = (xp - current_level_xp) / (next_level_xp - current_level_xp)

        # ✅ Clamp value between 0 and 1
        return min(1.0, max(0.0, progress))

    except:
        return 0.0


# ---------------- ACHIEVEMENTS ----------------
def get_achievements():
    try:
        achievements = fetch_achievements()
        return achievements if achievements else []
    except:
        return []


# ---------------- FOCUS SESSION LOGGING ----------------
def log_focus_session(duration):
    """
    Safe logging wrapper (if you want to call from UI)
    """
    try:
        from db import get_conn

        conn = get_conn()
        c = conn.cursor()

        duration = int(duration)
        points = duration * 2

        c.execute("""
            INSERT INTO focus_logs (start_time, duration, points)
            VALUES (datetime('now'), ?, ?)
        """, (duration, points))

        conn.commit()
        conn.close()

        return points

    except Exception as e:
        return 0  # fallback safe


# ---------------- DEBUG (OPTIONAL) ----------------
def debug_logs():
    logs = fetch_focus_logs()
    print("DEBUG LOGS:", logs)
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

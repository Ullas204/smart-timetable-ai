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

"""
Gamification module — XP, levels, and achievements.
"""
import math
import logging

from models import fetch_focus_logs, fetch_achievements

logger = logging.getLogger(__name__)

_xp_cache = None


def calculate_xp():
    global _xp_cache
    if _xp_cache is not None:
        return _xp_cache
    logs = fetch_focus_logs()
    total_xp = 0
    if not logs:
        return 0
    for log in logs:
        try:
            points = int(log[3]) if len(log) > 3 else 0
            total_xp += points
        except (ValueError, TypeError, IndexError):
            continue
    _xp_cache = total_xp
    return total_xp


def invalidate_xp_cache():
    global _xp_cache
    _xp_cache = None


def get_user_level():
    xp = calculate_xp()
    try:
        level = 1 + math.floor(math.sqrt(xp / 10))
    except (ValueError, ZeroDivisionError):
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
    except (ValueError, ZeroDivisionError):
        return 0.0


def get_achievements():
    try:
        achievements = fetch_achievements()
        return achievements if achievements else []
    except Exception as e:
        logger.warning("Failed to fetch achievements: %s", e)
        return []

"""
LangChain tools for Focus / Pomodoro Timer.

Wraps focus logging and gamification into reusable LangChain tools.
"""

import json
import logging
import datetime

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def start_focus_session(subject: str, duration_minutes: int = 25) -> str:
    """Start and log a focus/Pomodoro study session. Use this when the user wants to begin a focus session or start studying for a specific subject.

    Args:
        subject: The subject to study (e.g., "Math", "Physics").
        duration_minutes: Duration of the focus session in minutes (default 25 for Pomodoro).
    """
    try:
        from models import log_focus_session

        if not subject:
            return json.dumps({"success": False, "error": "Subject is required."})

        duration = max(1, min(240, int(duration_minutes)))
        points = duration * 2

        log_focus_session(duration, subject, points)
        logger.info("Focus session started: %s for %d min (%d XP)", subject, duration, points)

        return json.dumps({
            "success": True,
            "message": f"Focus session started for {subject} ({duration} min). You'll earn {points} XP!",
            "subject": subject,
            "duration_minutes": duration,
            "expected_xp": points
        })
    except Exception as e:
        logger.error("start_focus_session failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def log_completed_focus(subject: str, duration_minutes: int, points: int = 0) -> str:
    """Log a completed focus session after the timer ends. Use this to record study time when a Pomodoro or focus session is completed.

    Args:
        subject: The subject studied.
        duration_minutes: Actual duration in minutes.
        points: XP points earned (auto-calculated if 0).
    """
    try:
        from models import log_focus_session

        if not subject:
            return json.dumps({"success": False, "error": "Subject is required."})

        duration = max(1, int(duration_minutes))
        if points <= 0:
            points = duration * 2

        log_focus_session(duration, subject, points)
        logger.info("Focus session logged: %s, %d min, %d XP", subject, duration, points)

        return json.dumps({
            "success": True,
            "message": f"Logged {duration} min of focus on {subject}. +{points} XP!",
            "subject": subject,
            "duration_minutes": duration,
            "xp_earned": points
        })
    except Exception as e:
        logger.error("log_completed_focus failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_gamification_status() -> str:
    """Get the user's gamification status including XP, level, and achievements. Use this when the user asks about their level, XP, or achievements.

    Args: None
    """
    try:
        import gamification
        from db import fetch_achievements

        level = gamification.get_user_level()
        xp = gamification.calculate_xp()
        progress = gamification.get_progress_to_next_level()
        achievements = fetch_achievements()

        achievement_list = []
        for a in achievements:
            achievement_list.append({
                "name": a[1],
                "unlocked": bool(a[2]) if len(a) > 2 else True
            })

        logger.info("Gamification status: level=%d, xp=%d", level, xp)
        return json.dumps({
            "success": True,
            "level": level,
            "xp": xp,
            "progress_to_next_level": round(progress * 100, 1),
            "achievements": achievement_list,
            "total_achievements": len(achievement_list)
        })
    except Exception as e:
        logger.error("get_gamification_status failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


FOCUS_TOOLS = [start_focus_session, log_completed_focus, get_gamification_status]

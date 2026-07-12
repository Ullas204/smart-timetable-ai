"""
LangChain tools for the Analytics Agent.

Wraps analytics_agent and analytics module functions into reusable LangChain tools.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_productivity_analytics() -> str:
    """Get a comprehensive productivity analytics report including study streak, completion rate, trends, and recommendations. Use this when the user wants to see their productivity stats or analytics.

    Args: None
    """
    try:
        from agents.analytics_agent import generate_report

        report = generate_report()
        logger.info("Analytics report generated: streak=%d, completion=%.1f%%",
                     report["streak"], report["completion_rate"])
        return json.dumps({
            "success": True,
            "streak": report["streak"],
            "completion_rate": report["completion_rate"],
            "avg_daily_minutes": report["avg_daily_minutes"],
            "total_minutes": report["total_minutes"],
            "missed_sessions": report["missed_sessions"],
            "trends": report["trends"],
            "recommendations": report["recommendations"]
        })
    except Exception as e:
        logger.error("get_productivity_analytics failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_task_completion_rate() -> str:
    """Get the current task completion rate as a percentage. Use this when the user asks how many tasks they've completed.

    Args: None
    """
    try:
        from agents.analytics_agent import get_completion_rate

        rate = get_completion_rate()
        logger.info("Task completion rate: %.1f%%", rate)
        return json.dumps({
            "success": True,
            "completion_rate": rate,
            "message": f"You've completed {rate:.1f}% of your tasks."
        })
    except Exception as e:
        logger.error("get_task_completion_rate failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_study_streak() -> str:
    """Get the current consecutive study streak in days. Use this when the user asks about their study streak or consistency.

    Args: None
    """
    try:
        from agents.analytics_agent import get_study_streak as _streak

        streak = _streak()
        logger.info("Study streak: %d days", streak)
        return json.dumps({
            "success": True,
            "streak_days": streak,
            "message": f"You're on a {streak}-day study streak!" if streak > 0 else "No active study streak. Start studying today!"
        })
    except Exception as e:
        logger.error("get_study_streak failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_focus_stats() -> str:
    """Get detailed focus session statistics including total time, subject breakdown, and recent sessions. Use this when the user wants to see their focus/study time details.

    Args: None
    """
    try:
        from analytics import get_study_stats

        stats = get_study_stats()
        logger.info("Focus stats: total=%d min", stats["total_focus_time"])
        return json.dumps({
            "success": True,
            "total_focus_time": stats["total_focus_time"],
            "subject_distribution": stats.get("subject_distribution", {}),
            "recent_sessions": stats.get("recent_logs", [])[-5:]
        })
    except Exception as e:
        logger.error("get_focus_stats failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


ANALYTICS_TOOLS = [get_productivity_analytics, get_task_completion_rate, get_study_streak, get_focus_stats]

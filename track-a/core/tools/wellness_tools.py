"""
LangChain tools for the Wellness Agent.

Wraps wellness_agent functions into reusable LangChain tools.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_wellness_status() -> str:
    """Get the user's current wellness status including energy level, study load, and burnout risk. Use this when the user asks about their wellbeing, energy, or burnout risk.

    Args: None
    """
    try:
        from agents.wellness_agent import get_wellness_status as _status

        status = _status()
        logger.info("Wellness check: energy=%.0f%%, today=%d min", status["energy_level"], status["today_minutes"])
        return json.dumps({
            "success": True,
            "energy_level": round(status["energy_level"], 1),
            "today_minutes": status["today_minutes"],
            "weekly_minutes": status["weekly_minutes"],
            "sessions_today": status["sessions_today"],
            "breaks_taken": status["breaks_taken"],
            "avg_session_minutes": round(status["avg_session_minutes"], 1),
            "alerts": status["alerts"],
            "recommendation": status["recommendation"],
            "burnout_risk": "high" if status["energy_level"] < 40 else "low"
        })
    except Exception as e:
        logger.error("get_wellness_status failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_weekly_wellness_trend() -> str:
    """Get the weekly wellness trend showing daily study minutes over time. Use this when the user wants to see their study patterns over the week.

    Args: None
    """
    try:
        from agents.wellness_agent import get_weekly_trend

        trend = get_weekly_trend()
        logger.info("Weekly trend: %d data points.", len(trend))
        return json.dumps({
            "success": True,
            "trend": trend,
            "days_tracked": len(trend)
        })
    except Exception as e:
        logger.error("get_weekly_wellness_trend failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


WELLNESS_TOOLS = [get_wellness_status, get_weekly_wellness_trend]

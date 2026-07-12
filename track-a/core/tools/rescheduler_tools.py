"""
LangChain tools for the Rescheduler Agent.

Wraps rescheduler_agent functions into reusable LangChain tools.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def detect_missed_sessions() -> str:
    """Detect study sessions or events that have been missed (past their scheduled time without a focus log). Use this to check if the user has fallen behind.

    Args: None
    """
    try:
        from agents.rescheduler_agent import detect_missed_sessions as _detect

        missed = _detect()
        logger.info("Detected %d missed sessions.", len(missed))
        return json.dumps({
            "success": True,
            "missed_sessions": missed,
            "count": len(missed),
            "message": f"Found {len(missed)} missed session(s)." if missed else "No missed sessions. You're on track!"
        })
    except Exception as e:
        logger.error("detect_missed_sessions failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def auto_reschedule() -> str:
    """Automatically reschedule all missed sessions to the next available free slots. Use this when the user wants to recover from missed study sessions.

    Args: None
    """
    try:
        from agents.rescheduler_agent import detect_missed_sessions as _detect, auto_reschedule as _reschedule

        missed = _detect()
        if not missed:
            return json.dumps({
                "success": True,
                "message": "No missed sessions to reschedule. You're on track!",
                "rescheduled": 0
            })

        result = _reschedule(missed)
        logger.info("Auto-reschedule result: %s", result)
        return json.dumps({
            "success": True,
            "message": result,
            "rescheduled_count": len(missed)
        })
    except Exception as e:
        logger.error("auto_reschedule failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


RESCHEDULER_TOOLS = [detect_missed_sessions, auto_reschedule]

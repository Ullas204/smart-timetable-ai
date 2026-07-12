"""
LangChain tools for the Readiness Agent.

Wraps readiness_agent functions into reusable LangChain tools.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def check_exam_readiness(subject: str) -> str:
    """Check the user's exam readiness score for a specific subject (0-100%). Use this when the user asks how prepared they are for an exam or how ready they are for a subject.

    Args:
        subject: The subject name (e.g., "Math", "Physics", "Computer Science").
    """
    try:
        from agents.readiness_agent import get_readiness_score

        if not subject:
            return json.dumps({"success": False, "error": "Subject name is required."})

        score = get_readiness_score(subject)

        if score >= 80:
            level = "Well Prepared"
            advice = "Focus on revision and practice tests."
        elif score >= 60:
            level = "Good Progress"
            advice = "Increase study hours for weaker areas."
        elif score >= 40:
            level = "Needs Improvement"
            advice = "Create a focused study plan for weak topics."
        else:
            level = "Critical"
            advice = "Prioritize catching up on missed topics immediately."

        result = {
            "success": True,
            "subject": subject,
            "readiness_score": round(score, 1),
            "level": level,
            "advice": advice
        }

        logger.info("Readiness for %s: %.1f%%", subject, score)
        return json.dumps(result)
    except Exception as e:
        logger.error("check_exam_readiness failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_readiness_overview() -> str:
    """Get a comprehensive readiness overview across all tracked subjects. Use this when the user wants to see their overall academic preparedness.

    Args: None
    """
    try:
        from agents.readiness_agent import get_readiness_summary

        summary = get_readiness_summary()
        logger.info("Readiness overview: avg=%.1f%%", summary["avg_score"])
        return json.dumps({
            "success": True,
            "scores": {k: round(v, 1) for k, v in summary["scores"].items()},
            "average_score": round(summary["avg_score"], 1),
            "recommendation": summary["recommendation"]
        })
    except Exception as e:
        logger.error("get_readiness_overview failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


READINESS_TOOLS = [check_exam_readiness, get_readiness_overview]

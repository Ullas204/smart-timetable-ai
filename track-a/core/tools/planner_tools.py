"""
LangChain tools for the Planner Agent.

Wraps planner_agent.generate_plan into a reusable LangChain tool.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def generate_study_plan(subjects: str, hours_per_day: int = 4, priority_subject: str = "") -> str:
    """Generate an optimized 7-day study plan based on workload distribution and priorities. Use this when the user wants a study schedule, timetable, or weekly plan.

    Args:
        subjects: Comma-separated list of subjects (e.g., "Math, Physics, Computer Science, History").
        hours_per_day: Total study hours per day (1-12). Default is 4.
        priority_subject: The subject to prioritize (optional). Default is none.
    """
    try:
        from agents.planner_agent import generate_plan

        if not subjects:
            return json.dumps({"success": False, "error": "At least one subject is required."})

        subject_list = [s.strip() for s in subjects.split(",") if s.strip()]
        if not subject_list:
            return json.dumps({"success": False, "error": "No valid subjects provided."})

        hours = max(1, min(12, int(hours_per_day)))
        priority = priority_subject.strip() if priority_subject else None

        plan = generate_plan(subjects=subject_list, hours_per_day=hours, priority_subject=priority)

        logger.info("Generated study plan for %d subjects (%dh/day).", len(subject_list), hours)
        return json.dumps({
            "success": True,
            "plan": plan,
            "subjects": subject_list,
            "hours_per_day": hours,
            "priority_subject": priority
        })
    except Exception as e:
        logger.error("generate_study_plan failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_workload(subjects: str) -> str:
    """Get the current workload distribution across subjects. Use this when the user wants to understand their task load per subject.

    Args:
        subjects: Comma-separated list of subjects (e.g., "Math, Physics, CS").
    """
    try:
        from agents.planner_agent import get_workload_distribution

        if not subjects:
            return json.dumps({"success": False, "error": "At least one subject is required."})

        subject_list = [s.strip() for s in subjects.split(",") if s.strip()]
        workload = get_workload_distribution(subject_list, hours_per_day=4)

        logger.info("Retrieved workload for %d subjects.", len(subject_list))
        return json.dumps({"success": True, "workload": workload})
    except Exception as e:
        logger.error("get_workload failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


PLANNER_TOOLS = [generate_study_plan, get_workload]

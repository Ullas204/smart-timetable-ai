"""
LangChain tools for Subject & Exam Management.

Wraps db subject and exam functions into reusable LangChain tools.
"""

import json
import logging
import datetime

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def add_subject(name: str, color: str = "#4285F4", priority: int = 1) -> str:
    """Add a new academic subject to track. Use this when the user wants to add a new subject.

    Args:
        name: Subject name (e.g., "Data Structures").
        color: Hex color code for the subject. Default is blue.
        priority: Priority level 1-5. Default is 1.
    """
    try:
        from db import insert_subject

        if not name:
            return json.dumps({"success": False, "error": "Subject name is required."})

        insert_subject(name, color, int(priority))
        logger.info("Subject added: %s", name)

        return json.dumps({
            "success": True,
            "message": f"Subject '{name}' added successfully.",
            "subject": name
        })
    except Exception as e:
        logger.error("add_subject failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def list_subjects() -> str:
    """List all tracked subjects with their priority and syllabus completion. Use this when the user wants to see their subjects.

    Args: None
    """
    try:
        from db import fetch_subjects

        subjects = fetch_subjects()
        subject_list = []
        for s in subjects:
            subject_list.append({
                "id": s[0],
                "name": s[1],
                "color": s[2],
                "priority": s[3],
                "syllabus_completion": s[4]
            })

        logger.info("Listed %d subjects.", len(subject_list))
        return json.dumps({"success": True, "subjects": subject_list, "count": len(subject_list)})
    except Exception as e:
        logger.error("list_subjects failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def add_exam(subject: str, exam_date: str, weight: float = 1.0) -> str:
    """Add an upcoming exam to track. Use this when the user wants to register an exam.

    Args:
        subject: The subject name.
        exam_date: Exam date in ISO 8601 format (e.g., "2025-08-15").
        weight: Exam weight/importance. Default is 1.0.
    """
    try:
        from db import insert_exam

        if not subject or not exam_date:
            return json.dumps({"success": False, "error": "Subject and exam date are required."})

        insert_exam(subject, exam_date, float(weight))
        logger.info("Exam added: %s on %s", subject, exam_date)

        return json.dumps({
            "success": True,
            "message": f"Exam for '{subject}' scheduled on {exam_date}.",
            "subject": subject,
            "exam_date": exam_date
        })
    except Exception as e:
        logger.error("add_exam failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def list_exams() -> str:
    """List all upcoming exams sorted by date. Use this when the user wants to see their exam schedule.

    Args: None
    """
    try:
        from db import fetch_exams

        exams = fetch_exams()
        exam_list = []
        for e in exams:
            exam_list.append({
                "id": e[0],
                "subject": e[1],
                "exam_date": e[2],
                "weight": e[3],
                "syllabus_covered": e[4],
                "score": e[5]
            })

        logger.info("Listed %d exams.", len(exam_list))
        return json.dumps({"success": True, "exams": exam_list, "count": len(exam_list)})
    except Exception as e:
        logger.error("list_exams failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


SUBJECT_TOOLS = [add_subject, list_subjects, add_exam, list_exams]

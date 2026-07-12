"""
LangChain tools for Attendance Management.

Wraps db attendance functions into reusable LangChain tools.
"""

import json
import logging
import datetime

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def mark_attendance(subject: str, status: str = "present") -> str:
    """Mark attendance for a class/subject. Use this when the user wants to record their attendance.

    Args:
        subject: The subject/class name (e.g., "Math", "Physics").
        status: Attendance status - "present", "absent", or "late". Default is "present".
    """
    try:
        from db import insert_attendance

        if not subject:
            return json.dumps({"success": False, "error": "Subject name is required."})

        if status not in ("present", "absent", "late"):
            status = "present"

        today = datetime.date.today().isoformat()
        insert_attendance(subject, today, status)
        logger.info("Attendance marked: %s = %s on %s", subject, status, today)

        return json.dumps({
            "success": True,
            "message": f"Attendance marked as '{status}' for {subject} on {today}.",
            "subject": subject,
            "status": status,
            "date": today
        })
    except Exception as e:
        logger.error("mark_attendance failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def view_attendance(subject: str = "") -> str:
    """View attendance records, optionally filtered by subject. Use this when the user wants to check their attendance history.

    Args:
        subject: Optional subject filter. Leave empty to see all attendance.
    """
    try:
        from db import fetch_attendance

        records = fetch_attendance(subject if subject else None)
        attendance_list = []
        for r in records:
            attendance_list.append({
                "id": r[0],
                "subject": r[1],
                "date": r[2],
                "status": r[3]
            })

        present = sum(1 for a in attendance_list if a["status"] == "present")
        total = len(attendance_list)
        rate = (present / total * 100) if total > 0 else 0

        logger.info("Attendance viewed: %d records (%.1f%% present)", total, rate)
        return json.dumps({
            "success": True,
            "records": attendance_list,
            "total_records": total,
            "present_count": present,
            "attendance_rate": round(rate, 1)
        })
    except Exception as e:
        logger.error("view_attendance failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


ATTENDANCE_TOOLS = [mark_attendance, view_attendance]

"""
LangChain tools for Event Management.

Wraps the existing db.insert_event, db.fetch_events, and
calendar_utils / scheduler_pro modules into reusable LangChain tools.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def create_event(title: str, start: str, end: str) -> str:
    """Create a new academic event in the calendar. Use this when the user wants to schedule a class, meeting, study session, or any time-blocked activity.

    Args:
        title: The event title/name (e.g., "DBMS Revision", "Physics Lab").
        start: Start time in ISO 8601 format (e.g., "2025-07-12T09:00:00").
        end: End time in ISO 8601 format (e.g., "2025-07-12T11:00:00").
    """
    try:
        from models import insert_event

        if not title:
            return json.dumps({"success": False, "error": "Event title is required."})

        if not start or not end:
            return json.dumps({"success": False, "error": "Start and end times are required."})

        try:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        except ValueError:
            return json.dumps({"success": False, "error": "Invalid datetime format. Use ISO 8601."})

        if end_dt <= start_dt:
            return json.dumps({"success": False, "error": "End time must be after start time."})

        insert_event(title, start, end)
        logger.info("Event created: %s (%s to %s)", title, start, end)

        return json.dumps({
            "success": True,
            "message": f"Event '{title}' scheduled from {start} to {end}.",
            "event": {"title": title, "start": start, "end": end}
        })
    except Exception as e:
        logger.error("create_event failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def list_events() -> str:
    """List all scheduled events from the local calendar. Use this when the user wants to see their upcoming events, schedule, or calendar.

    Args: None
    """
    try:
        from models import fetch_events

        events = fetch_events()
        event_list = []
        for e in events:
            event_list.append({
                "id": e[0],
                "title": e[1],
                "start": e[2],
                "end": e[3]
            })

        logger.info("Listed %d events.", len(event_list))
        return json.dumps({"success": True, "events": event_list, "count": len(event_list)})
    except Exception as e:
        logger.error("list_events failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def find_free_slots(duration_hours: float = 1.0, days_ahead: int = 3) -> str:
    """Find available free time slots in the user's schedule. Use this when the user asks when they are free or when to schedule something.

    Args:
        duration_hours: How many hours the slot should be (default 1.0).
        days_ahead: How many days ahead to search (default 3).
    """
    try:
        from scheduler_pro import find_free_slots as _find_free_slots

        slots = _find_free_slots(duration_hours=int(duration_hours), days_ahead=int(days_ahead))
        slot_list = [{"start": s, "end": e} for s, e in (slots or [])]

        logger.info("Found %d free slots.", len(slot_list))
        return json.dumps({"success": True, "slots": slot_list, "count": len(slot_list)})
    except Exception as e:
        logger.error("find_free_slots failed: %s", e)
        return json.dumps({"success": False, "error": str(e), "slots": []})


@tool
def resolve_event_conflict(title: str, start: str, end: str) -> str:
    """Check for scheduling conflicts and suggest alternatives. Use this when the user wants to schedule an event and needs conflict resolution.

    Args:
        title: The event title.
        start: Start time in ISO 8601 format.
        end: End time in ISO 8601 format.
    """
    try:
        from scheduler_pro import resolve_conflict_pro

        conflict, alt = resolve_conflict_pro(title, start, end)

        if conflict:
            result = {
                "success": True,
                "conflict": True,
                "conflicting_event": conflict,
                "suggestion": {"start": alt[0], "end": alt[1]} if alt and alt[0] else None,
                "message": f"Conflict detected with '{conflict}'."
            }
        else:
            result = {
                "success": True,
                "conflict": False,
                "message": "No conflicts. Slot is available."
            }

        logger.info("Conflict check for '%s': %s", title, "conflict" if conflict else "clear")
        return json.dumps(result)
    except Exception as e:
        logger.error("resolve_event_conflict failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def suggest_study_time(subject: str) -> str:
    """Suggest the optimal study time for a given subject based on the user's schedule and patterns. Use this when the user asks when to study for a specific subject.

    Args:
        subject: The subject name (e.g., "Math", "Physics").
    """
    try:
        from scheduler_pro import suggest_optimal_study_time

        if not subject:
            return json.dumps({"success": False, "error": "Subject name is required."})

        start, end = suggest_optimal_study_time(subject)

        if start:
            result = {
                "success": True,
                "subject": subject,
                "suggested_start": start,
                "suggested_end": end,
                "message": f"Best time for {subject}: {start} to {end}."
            }
        else:
            result = {
                "success": False,
                "subject": subject,
                "message": "No available slots found. Try expanding your availability."
            }

        logger.info("Suggested study time for %s: %s", subject, start)
        return json.dumps(result)
    except Exception as e:
        logger.error("suggest_study_time failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def sync_google_calendar() -> str:
    """Fetch events from Google Calendar and display them. Use this when the user wants to sync or view their Google Calendar events.

    Args: None
    """
    try:
        from google_calendar import get_events as g_get_events

        g_events = g_get_events()
        event_list = []
        for e in g_events:
            event_list.append({
                "title": e.get("summary", "No Title"),
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end": e["end"].get("dateTime", e["end"].get("date")),
            })

        logger.info("Synced %d Google Calendar events.", len(event_list))
        return json.dumps({"success": True, "events": event_list, "count": len(event_list)})
    except Exception as e:
        logger.error("sync_google_calendar failed: %s", e)
        return json.dumps({"success": False, "error": str(e), "message": "Google Calendar unavailable."})


EVENT_TOOLS = [create_event, list_events, find_free_slots, resolve_event_conflict, suggest_study_time, sync_google_calendar]

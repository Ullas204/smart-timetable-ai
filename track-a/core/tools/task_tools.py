"""
LangChain tools for Task Management.

Wraps db.insert_task, db.fetch_tasks, db.update_task_status
into reusable LangChain tools.
"""

import json
import logging
import datetime

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def create_task(title: str, due_date: str, priority: int = 1) -> str:
    """Create a new academic task or assignment. Use this when the user wants to add a to-do item, assignment, homework, or any task with a deadline.

    Args:
        title: Task title/name (e.g., "Complete DBMS Assignment 3").
        due_date: Due date in ISO 8601 date format (e.g., "2025-07-15").
        priority: Priority level 1 (low) to 5 (high). Default is 1.
    """
    try:
        from db import insert_task

        if not title:
            return json.dumps({"success": False, "error": "Task title is required."})

        if not due_date:
            due_date = datetime.date.today().isoformat()

        insert_task(title, due_date, status="pending")
        logger.info("Task created: '%s' (due: %s)", title, due_date)

        return json.dumps({
            "success": True,
            "message": f"Task '{title}' created with due date {due_date}.",
            "task": {"title": title, "due_date": due_date, "priority": priority, "status": "pending"}
        })
    except Exception as e:
        logger.error("create_task failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def list_tasks(status_filter: str = "all") -> str:
    """List all tasks, optionally filtered by status. Use this when the user wants to see their pending tasks, completed tasks, or all tasks.

    Args:
        status_filter: Filter by status - "all", "pending", "in_progress", or "completed". Default is "all".
    """
    try:
        from db import fetch_tasks

        tasks = fetch_tasks()
        task_list = []
        for t in tasks:
            task = {
                "id": t[0],
                "title": t[1],
                "due_date": t[2],
                "priority": t[3] if len(t) > 3 else 1,
                "status": t[4] if len(t) > 4 else "pending"
            }
            if status_filter == "all" or task["status"] == status_filter:
                task_list.append(task)

        logger.info("Listed %d tasks (filter=%s).", len(task_list), status_filter)
        return json.dumps({"success": True, "tasks": task_list, "count": len(task_list)})
    except Exception as e:
        logger.error("list_tasks failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def update_task(task_id: int, new_status: str) -> str:
    """Update the status of an existing task. Use this to move tasks between Kanban columns (pending, in_progress, completed).

    Args:
        task_id: The numeric ID of the task.
        new_status: New status - "pending", "in_progress", or "completed".
    """
    try:
        from db import update_task_status

        if new_status not in ("pending", "in_progress", "completed"):
            return json.dumps({"success": False, "error": "Status must be 'pending', 'in_progress', or 'completed'."})

        update_task_status(int(task_id), new_status)
        logger.info("Task %d updated to status '%s'.", task_id, new_status)

        return json.dumps({
            "success": True,
            "message": f"Task {task_id} status updated to '{new_status}'.",
            "task_id": task_id,
            "new_status": new_status
        })
    except Exception as e:
        logger.error("update_task failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


TASK_TOOLS = [create_task, list_tasks, update_task]

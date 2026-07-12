"""
LangChain Tool Registry for Smart Academic OS (Phase 2 + Phase 3).

Central registry that aggregates all LangChain tools from domain modules
and provides a single entry point for tool binding with the agent executor.

Phase 3 adds Knowledge Base (RAG) tools for document search.

Usage:
    from core.tools import get_all_tools, get_tool_by_name, get_tool_names
"""

import logging
from typing import List, Dict, Optional

from langchain_core.tools import BaseTool

from core.tools.event_tools import EVENT_TOOLS
from core.tools.task_tools import TASK_TOOLS
from core.tools.planner_tools import PLANNER_TOOLS
from core.tools.rescheduler_tools import RESCHEDULER_TOOLS
from core.tools.readiness_tools import READINESS_TOOLS
from core.tools.wellness_tools import WELLNESS_TOOLS
from core.tools.analytics_tools import ANALYTICS_TOOLS
from core.tools.focus_tools import FOCUS_TOOLS
from core.tools.notification_tools import NOTIFICATION_TOOLS
from core.tools.voice_tools import VOICE_TOOLS
from core.tools.attendance_tools import ATTENDANCE_TOOLS
from core.tools.profile_tools import PROFILE_TOOLS
from core.tools.subject_tools import SUBJECT_TOOLS
from core.tools.rag_tools import RAG_TOOLS

logger = logging.getLogger(__name__)

# ── Tool groups for modular registration ──────────────────

TOOL_GROUPS: Dict[str, List[BaseTool]] = {
    "event_management": EVENT_TOOLS,
    "task_management": TASK_TOOLS,
    "planner": PLANNER_TOOLS,
    "rescheduler": RESCHEDULER_TOOLS,
    "readiness": READINESS_TOOLS,
    "wellness": WELLNESS_TOOLS,
    "analytics": ANALYTICS_TOOLS,
    "focus": FOCUS_TOOLS,
    "notifications": NOTIFICATION_TOOLS,
    "voice": VOICE_TOOLS,
    "attendance": ATTENDANCE_TOOLS,
    "profile": PROFILE_TOOLS,
    "subjects": SUBJECT_TOOLS,
    "knowledge_base": RAG_TOOLS,
}

# ── Tool execution log ────────────────────────────────────

_tool_execution_log: List[Dict] = []


def get_all_tools() -> List[BaseTool]:
    """Return a flat list of ALL registered LangChain tools.

    This is the primary method used by the agent executor to bind
    tools to the LLM for function calling.
    """
    all_tools = []
    for group_name, tools in TOOL_GROUPS.items():
        all_tools.extend(tools)
    logger.debug("Returning %d tools from %d groups.", len(all_tools), len(TOOL_GROUPS))
    return all_tools


def get_tools_by_group(group_name: str) -> List[BaseTool]:
    """Return tools from a specific group.

    Args:
        group_name: One of the keys in TOOL_GROUPS (e.g., "event_management").
    """
    return TOOL_GROUPS.get(group_name, [])


def get_tool_names() -> List[str]:
    """Return the names of all registered tools."""
    return [tool.name for tool in get_all_tools()]


def get_tool_by_name(name: str) -> Optional[BaseTool]:
    """Look up a tool by its name.

    Args:
        name: The tool's registered name.
    """
    for tool in get_all_tools():
        if tool.name == name:
            return tool
    return None


def log_tool_execution(tool_name: str, input_data: str, output_data: str, success: bool) -> None:
    """Log a tool execution for debugging and display purposes.

    Args:
        tool_name: Name of the executed tool.
        input_data: The input passed to the tool.
        output_data: The output returned by the tool.
        success: Whether the execution succeeded.
    """
    import datetime
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tool_name": tool_name,
        "input": input_data[:500],
        "output": output_data[:500],
        "success": success,
    }
    _tool_execution_log.append(entry)
    # Keep only last 100 entries
    if len(_tool_execution_log) > 100:
        _tool_execution_log.pop(0)
    logger.info("Tool '%s' executed: success=%s", tool_name, success)


def get_tool_execution_log() -> List[Dict]:
    """Return the full tool execution log."""
    return list(_tool_execution_log)


def clear_tool_execution_log() -> None:
    """Clear the tool execution log."""
    _tool_execution_log.clear()


def get_tool_registry_summary() -> str:
    """Return a human-readable summary of all registered tools."""
    lines = ["=== Smart Academic OS - Tool Registry ===\n"]
    for group_name, tools in TOOL_GROUPS.items():
        lines.append(f"[{group_name}] ({len(tools)} tools)")
        for t in tools:
            lines.append(f"  - {t.name}: {t.description[:80]}...")
        lines.append("")
    lines.append(f"Total: {len(get_all_tools())} tools across {len(TOOL_GROUPS)} groups")
    return "\n".join(lines)


__all__ = [
    "get_all_tools",
    "get_tools_by_group",
    "get_tool_names",
    "get_tool_by_name",
    "log_tool_execution",
    "get_tool_execution_log",
    "clear_tool_execution_log",
    "get_tool_registry_summary",
    "TOOL_GROUPS",
]

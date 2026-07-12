"""
Pydantic schemas for the Agentic AI Core.

Defines the structured types exchanged between the LLM, the agent
executor, and the UI action dispatcher. Phase 2 adds tool execution
tracking fields.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class ActionType(str, Enum):
    """All actions the agent can意图."""

    CREATE = "create"
    FIND = "find"
    TASK = "task"
    STUDY_PLAN = "study_plan"
    FOCUS = "focus"
    STATS = "stats"
    RECOMMEND = "recommend"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"


class ToolExecution(BaseModel):
    """Record of a single tool invocation during agent execution."""

    tool_name: str = Field(description="Name of the tool that was called.")
    input_data: str = Field(default="", description="Input passed to the tool.")
    output_data: str = Field(default="", description="Output returned by the tool.")
    success: bool = Field(default=True, description="Whether the tool executed successfully.")


class AgentResponse(BaseModel):
    """Structured response returned by the AcademicAgent.

    ``raw_action`` preserves the original dict so that the existing
    action dispatcher in app.py works without modification.
    Phase 2 adds ``tools_used`` for tool execution tracking.
    """

    action: ActionType = Field(default=ActionType.CONVERSATION)
    message: str = Field(
        default="",
        description="Natural-language response to display to the user.",
    )
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    due_date: Optional[str] = None
    subjects: Optional[List[str]] = None
    subject: Optional[str] = None
    duration: Optional[int] = None
    raw_action: Optional[dict] = Field(
        default=None,
        description="Backward-compatible action dict for the existing dispatcher.",
    )
    # Phase 2: Tool calling fields
    tools_used: List[ToolExecution] = Field(
        default_factory=list,
        description="List of tools invoked during this agent execution.",
    )
    is_tool_call: bool = Field(
        default=False,
        description="True if the response was produced via tool calling (not pure LLM text).",
    )

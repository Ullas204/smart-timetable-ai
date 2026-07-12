"""
Smart Academic OS - Agentic AI Core (Phase 1-4)

Provides the centralized LangChain agent executor with tool binding,
conversation memory, shared LLM client, configuration, Pydantic schemas,
and the tool registry.

Usage:
    from core.agent_executor import AcademicAgent
    from core.memory import ChatMemory, FallbackMemory
    from core.config import Settings
    from core.tools import get_all_tools, get_tool_registry_summary
"""

from core.agent_executor import AcademicAgent
from core.memory import ChatMemory, FallbackMemory
from core.config import Settings

__all__ = ["AcademicAgent", "ChatMemory", "FallbackMemory", "Settings"]

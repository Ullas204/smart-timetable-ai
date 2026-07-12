"""
Session-scoped conversation memory backed by ``st.session_state``.

Stores LangChain ``HumanMessage`` / ``AIMessage`` objects so they can
be fed directly into the LLM as chat history.  The window is trimmed
to the last *N* exchanges to stay within token limits.

A ``FallbackMemory`` is available for non-Streamlit contexts (CLI, tests).
"""

import logging
from typing import List, Optional

from langchain_core.messages import HumanMessage, AIMessage
from core.config import Settings

logger = logging.getLogger(__name__)

try:
    import streamlit as st

    _HAS_STREAMLIT = True
except ImportError:
    _HAS_STREAMLIT = False


class ChatMemory:
    """Conversation memory that survives Streamlit reruns via session_state."""

    def __init__(
        self,
        session_state_key: str = "chat_history",
        window_size: Optional[int] = None,
    ):
        self.key = session_state_key
        self.window_size = window_size or Settings.MEMORY_WINDOW_SIZE
        if _HAS_STREAMLIT:
            if self.key not in st.session_state:
                st.session_state[self.key] = []
                logger.debug("Initialised empty chat memory (key=%s).", self.key)

    # ── public API ────────────────────────────────────────

    def get_history(self) -> list:
        """Return the full message list (read-only view)."""
        if _HAS_STREAMLIT:
            return st.session_state.get(self.key, [])
        return []

    def add_user_message(self, content: str) -> None:
        """Append a user message and trim if needed."""
        if _HAS_STREAMLIT:
            st.session_state[self.key].append(HumanMessage(content=content))
            self._trim()

    def add_ai_message(self, content: str) -> None:
        """Append an AI message and trim if needed."""
        if _HAS_STREAMLIT:
            st.session_state[self.key].append(AIMessage(content=content))
            self._trim()

    def clear(self) -> None:
        """Reset conversation history."""
        if _HAS_STREAMLIT:
            st.session_state[self.key] = []
        logger.info("Chat memory cleared.")

    def get_messages_for_llm(self) -> list:
        """Return a copy suitable for passing to the LLM."""
        if _HAS_STREAMLIT:
            return list(st.session_state.get(self.key, []))
        return []

    # ── properties ────────────────────────────────────────

    @property
    def message_count(self) -> int:
        if _HAS_STREAMLIT:
            return len(st.session_state.get(self.key, []))
        return 0

    # ── internals ─────────────────────────────────────────

    def _trim(self) -> None:
        """Keep only the last *window_size * 2* messages."""
        if not _HAS_STREAMLIT:
            return
        max_messages = self.window_size * 2
        if len(st.session_state[self.key]) > max_messages:
            st.session_state[self.key] = st.session_state[self.key][-max_messages:]
            logger.debug("Trimmed memory to %d messages.", max_messages)


class FallbackMemory:
    """In-memory conversation history for non-Streamlit contexts (CLI, tests).

    Same API as ``ChatMemory`` but stores messages in a plain list.
    """

    def __init__(self, window_size: Optional[int] = None):
        self.window_size = window_size or Settings.MEMORY_WINDOW_SIZE
        self._messages: List = []
        logger.debug("Initialised FallbackMemory (window=%d).", self.window_size)

    def get_history(self) -> list:
        return list(self._messages)

    def add_user_message(self, content: str) -> None:
        self._messages.append(HumanMessage(content=content))
        self._trim()

    def add_ai_message(self, content: str) -> None:
        self._messages.append(AIMessage(content=content))
        self._trim()

    def clear(self) -> None:
        self._messages.clear()
        logger.info("FallbackMemory cleared.")

    def get_messages_for_llm(self) -> list:
        return list(self._messages)

    @property
    def message_count(self) -> int:
        return len(self._messages)

    def _trim(self) -> None:
        max_messages = self.window_size * 2
        if len(self._messages) > max_messages:
            self._messages = self._messages[-max_messages:]

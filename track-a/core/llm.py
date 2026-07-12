"""
Shared LangChain LLM client.

Exposes a singleton ``get_llm()`` that returns a ``ChatGoogleGenerativeAI``
instance configured from ``Settings``.  All core modules should use this
single client instead of creating their own.
"""

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import Settings

logger = logging.getLogger(__name__)

_llm_instance: ChatGoogleGenerativeAI | None = None


def get_llm() -> ChatGoogleGenerativeAI:
    """Return the shared Gemini LLM instance (lazy-initialised)."""
    global _llm_instance
    if _llm_instance is None:
        if not Settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set.  "
                "Add it to your .env file or environment."
            )
        logger.info(
            "Initialising LangChain LLM: model=%s  temp=%.1f",
            Settings.LLM_MODEL,
            Settings.LLM_TEMPERATURE,
        )
        _llm_instance = ChatGoogleGenerativeAI(
            model=Settings.LLM_MODEL,
            google_api_key=Settings.GEMINI_API_KEY,
            temperature=Settings.LLM_TEMPERATURE,
            max_output_tokens=Settings.LLM_MAX_OUTPUT_TOKENS,
        )
    return _llm_instance


def reset_llm() -> None:
    """Discard the cached LLM instance so the next call re-creates it."""
    global _llm_instance
    _llm_instance = None
    logger.info("LLM instance reset.")

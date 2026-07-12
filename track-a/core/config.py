"""
Centralized configuration for Smart Academic OS.

Reads environment variables from .env (local) or Streamlit secrets (HF Spaces).
"""

import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_BASE_DIR, ".env"))


def _get_secret(key: str, default: str = "") -> str:
    """Get a secret from env vars or Streamlit secrets (HF Spaces)."""
    val = os.getenv(key, "")
    if val:
        return val
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return default


class Settings:
    """Application-wide settings loaded from environment variables."""

    # ── LLM ───────────────────────────────────────────────
    GEMINI_API_KEY: str = _get_secret("GEMINI_API_KEY")
    LLM_MODEL: str = _get_secret("LLM_MODEL", "gemini-2.0-flash")
    LLM_TEMPERATURE: float = float(_get_secret("LLM_TEMPERATURE", "0.3"))
    LLM_MAX_OUTPUT_TOKENS: int = int(_get_secret("LLM_MAX_OUTPUT_TOKENS", "2048"))

    # ── Memory ────────────────────────────────────────────
    MEMORY_WINDOW_SIZE: int = int(_get_secret("MEMORY_WINDOW_SIZE", "20"))

    # ── Database ──────────────────────────────────────────
    DB_PATH: str = _get_secret("DB_PATH", "db.sqlite3")

    # ── Email / SMTP ──────────────────────────────────────
    EMAIL: str = _get_secret("EMAIL")
    EMAIL_PASSWORD: str = _get_secret("EMAIL_PASSWORD")
    SMTP_SERVER: str = _get_secret("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(_get_secret("SMTP_PORT", "465"))

    # ── App ───────────────────────────────────────────────
    TIMEZONE: str = _get_secret("TIMEZONE", "Asia/Kolkata")
    APP_TITLE: str = "Smart Academic OS"

    # ── RAG / Knowledge Base (canonical config is core/rag/config.py) ──
    CHUNK_SIZE: int = int(_get_secret("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(_get_secret("CHUNK_OVERLAP", "200"))
    RETRIEVAL_K: int = int(_get_secret("RETRIEVAL_K", "4"))
    EMBEDDING_MODEL: str = _get_secret("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    MAX_FILE_SIZE_MB: int = int(_get_secret("MAX_FILE_SIZE_MB", "50"))

    # ── Security ──────────────────────────────────────────
    MAX_QUERY_LENGTH: int = int(_get_secret("MAX_QUERY_LENGTH", "5000"))
    MAX_UPLOAD_FILES: int = int(_get_secret("MAX_UPLOAD_FILES", "10"))

    # ── Debug ─────────────────────────────────────────────
    DEBUG: bool = _get_secret("SMART_OS_DEBUG", "0") == "1"

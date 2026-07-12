"""
RAG configuration constants for Smart Academic OS.

Centralizes all RAG-related settings. Values can be overridden
via environment variables in .env.
"""

import os
import logging

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", os.path.join(_BASE_DIR, "knowledge_base"))
FAISS_INDEX_DIR: str = os.getenv("FAISS_INDEX_DIR", os.path.join(_BASE_DIR, "faiss_index"))

# ── Text Splitting ────────────────────────────────────────
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

# ── Retrieval ─────────────────────────────────────────────
RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "4"))

# ── Embeddings ────────────────────────────────────────────
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

# ── File Limits ───────────────────────────────────────────
MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
SUPPORTED_FORMATS = [".pdf", ".txt", ".docx"]

# ── RAG Prompt Template ───────────────────────────────────
RAG_SYSTEM_PREFIX = """\
You are Smart Academic OS with access to the student's uploaded Knowledge Base.

## Knowledge Base Guidelines
- When the user asks about their notes, syllabus, study materials, lecture notes, \
previous question papers, or any uploaded document content, use the \
search_knowledge_base tool to find relevant information.
- Base your answers PRIMARILY on the retrieved context from the Knowledge Base.
- Clearly indicate when your answer comes from uploaded documents.
- Cite the source document name when referencing specific content.
- If the retrieved context does not contain enough information to answer, \
say so honestly: "The uploaded documents don't contain specific information about this topic."
- If the Knowledge Base is empty, tell the user to upload documents first.
- NEVER make up or hallucinate document content that isn't in the retrieved context.
"""

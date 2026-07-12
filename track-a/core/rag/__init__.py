"""
Smart Academic OS - RAG Pipeline (Phase 3).

Provides Retrieval-Augmented Generation capabilities using
FAISS vector store and Google Gemini Embedding 2 Preview.

Usage:
    from core.rag import get_rag_pipeline
    pipeline = get_rag_pipeline()
    result = pipeline.search("Explain Deadlock")
    result = pipeline.answer("Summarize Unit 3 from my DBMS notes")
"""

import logging

logger = logging.getLogger(__name__)

_rag_pipeline = None


def get_rag_pipeline():
    """Return the singleton RAGPipeline instance (lazy-initialized)."""
    global _rag_pipeline
    if _rag_pipeline is None:
        from core.rag.pipeline import RAGPipeline
        _rag_pipeline = RAGPipeline()
        logger.info("RAG pipeline initialized.")
    return _rag_pipeline


def reset_rag_pipeline():
    """Discard the cached RAG pipeline instance."""
    global _rag_pipeline
    _rag_pipeline = None
    logger.info("RAG pipeline reset.")


__all__ = ["get_rag_pipeline", "reset_rag_pipeline"]

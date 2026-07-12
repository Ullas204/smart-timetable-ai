"""
RAG Pipeline for Smart Academic OS.

Combines document retrieval (FAISS) with LLM generation (Gemini)
to answer questions grounded in the student's uploaded documents.
"""

import logging
import re
import time
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage

from core.rag.config import RETRIEVAL_K, RAG_SYSTEM_PREFIX, EMBEDDING_MODEL
from core.rag.vector_store import VectorStoreManager
from core.config import Settings

logger = logging.getLogger(__name__)

# Cache when Gemini API was last known exhausted to skip retries
_api_exhausted_until: float = 0.0
_API_COOLDOWN_SECONDS = 120


# ── Prompt Injection Protection for RAG queries ───────────────

_RAG_INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|prior|above|the\s+retrieved)',
    r'forget\s+(the\s+)?(context|documents?|instructions?)',
    r'you\s+are\s+now\s+',
    r'act\s+as\s+if\s+',
    r'new\s+(system\s+)?prompt\s*:',
    r'disregard\s+',
    r'override\s+',
    r'(DAN|jailbreak|bypass)',
    r'from\s+now\s+on\s+you\s+are',
]
_RAG_INJECTION_RE = re.compile('|'.join(_RAG_INJECTION_PATTERNS), re.IGNORECASE)


def _sanitize_rag_query(query: str) -> str:
    """Sanitize a RAG query to prevent prompt injection."""
    if not query or not isinstance(query, str):
        return ""
    query = query.strip()[:2000]
    if _RAG_INJECTION_RE.search(query):
        logger.warning("Potential prompt injection in RAG query detected")
        return ""
    return query


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline.

    Retrieves relevant document chunks from FAISS and uses Gemini
    to generate grounded answers.
    """

    def __init__(self):
        self._vector_store: Optional[VectorStoreManager] = None
        self._llm = None

    @property
    def vector_store(self) -> VectorStoreManager:
        """Lazy-load the vector store manager."""
        if self._vector_store is None:
            self._vector_store = VectorStoreManager()
        return self._vector_store

    @property
    def llm(self):
        """Lazy-load the shared LLM."""
        if self._llm is None:
            try:
                from core.llm import get_llm
                self._llm = get_llm()
            except Exception as e:
                logger.warning("LLM unavailable for RAG: %s", e)
                self._llm = None
        return self._llm

    def _invoke_llm_with_retry(self, messages, max_retries=2):
        """Invoke LLM with automatic retry on rate-limit (429) errors."""
        global _api_exhausted_until
        if time.time() < _api_exhausted_until:
            raise RuntimeError("Gemini API quota exhausted (cached)")

        last_exc = None
        for attempt in range(max_retries):
            try:
                return self.llm.invoke(messages)
            except Exception as exc:
                last_exc = exc
                exc_str = str(exc)
                if "429" in exc_str or "RESOURCE_EXHAUSTED" in exc_str:
                    _api_exhausted_until = time.time() + _API_COOLDOWN_SECONDS
                    logger.warning("Gemini API quota exhausted. Skipping LLM for %ds.", _API_COOLDOWN_SECONDS)
                    raise
                else:
                    raise
        raise last_exc

    # ── public API ────────────────────────────────────────

    def search(self, query: str, k: int = RETRIEVAL_K) -> dict:
        """Search the knowledge base for relevant document chunks.

        Parameters
        ----------
        query : str
            The user's search query.
        k : int
            Number of top results to return.

        Returns
        -------
        dict
            {"found": bool, "context": str, "sources": list, "chunks": list}
        """
        query = _sanitize_rag_query(query)
        if not query:
            return {
                "found": False,
                "context": "",
                "sources": [],
                "chunks": [],
                "message": "Invalid search query.",
            }

        try:
            chunks = self.vector_store.similarity_search(query, k=k)

            if not chunks:
                return {
                    "found": False,
                    "context": "",
                    "sources": [],
                    "chunks": [],
                    "message": "No relevant documents found in the Knowledge Base.",
                }

            context_parts = []
            sources = []
            seen_sources = set()

            for chunk in chunks:
                text = chunk.page_content.strip()
                if text:
                    context_parts.append(text)

                source = chunk.metadata.get("source", "Unknown")
                doc_id = chunk.metadata.get("doc_id", "")
                page = chunk.metadata.get("page", None)
                chunk_idx = chunk.metadata.get("chunk_index", None)

                source_key = f"{source}:{chunk_idx}"
                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    source_info = {"filename": source, "doc_id": doc_id}
                    if page is not None:
                        source_info["page"] = page + 1
                    sources.append(source_info)

            context = "\n\n---\n\n".join(context_parts)

            logger.info(
                "RAG search: %d chunks found, %d sources.", len(chunks), len(sources)
            )
            return {
                "found": True,
                "context": context,
                "sources": sources,
                "chunks": [{"text": c.page_content[:200], "source": c.metadata.get("source", "")} for c in chunks],
                "message": f"Found {len(chunks)} relevant chunk(s) from {len(sources)} document(s).",
            }

        except Exception as e:
            logger.error("RAG search failed: %s", e)
            return {
                "found": False,
                "context": "",
                "sources": [],
                "chunks": [],
                "message": f"Search failed: {str(e)}",
            }

    def answer(self, query: str, k: int = RETRIEVAL_K) -> dict:
        """Search + generate a grounded answer using the LLM.

        Parameters
        ----------
        query : str
            The user's question.
        k : int
            Number of chunks to retrieve.

        Returns
        -------
        dict
            {"answer": str, "sources": list, "used_rag": bool}
        """
        search_result = self.search(query, k=k)

        if not search_result["found"]:
            return {
                "answer": (
                    "The Knowledge Base is empty or doesn't contain relevant "
                    "information for this query. Please upload study materials "
                    "(PDF, TXT, or DOCX) in the Knowledge Base tab first."
                ),
                "sources": [],
                "used_rag": False,
            }

        if not self.llm:
            return {
                "answer": (
                    f"Based on your uploaded documents:\n\n"
                    f"{search_result['context'][:1000]}"
                ),
                "sources": search_result["sources"],
                "used_rag": True,
            }

        # Build RAG prompt
        rag_prompt = self._build_rag_prompt(query, search_result["context"])

        try:
            messages = [
                SystemMessage(content=RAG_SYSTEM_PREFIX),
                HumanMessage(content=rag_prompt),
            ]
            response = self._invoke_llm_with_retry(messages)
            answer_text = response.content if hasattr(response, "content") else str(response)

            return {
                "answer": answer_text,
                "sources": search_result["sources"],
                "used_rag": True,
            }

        except Exception as e:
            logger.error("RAG LLM invocation failed: %s", e)
            # Return raw context as fallback
            return {
                "answer": (
                    f"Here is the relevant content from your documents "
                    f"(LLM generation failed, showing raw context):\n\n"
                    f"{search_result['context'][:1500]}"
                ),
                "sources": search_result["sources"],
                "used_rag": True,
            }

    def get_status(self) -> dict:
        """Return knowledge base status for display."""
        try:
            from db import fetch_documents
            documents = fetch_documents()

            doc_list = []
            for d in documents:
                doc_list.append({
                    "id": d[0],
                    "filename": d[1],
                    "file_type": d[3],
                    "file_size": d[4],
                    "chunk_count": d[5],
                    "uploaded_at": d[6],
                    "status": d[7],
                })

            vs_stats = self.vector_store.get_index_stats()

            return {
                "success": True,
                "total_documents": len(documents),
                "total_chunks": sum(d.get("chunk_count", 0) for d in doc_list),
                "documents": doc_list,
                "index_stats": vs_stats,
                "embedding_model": EMBEDDING_MODEL,
                "vector_store": "FAISS",
                "index_size_bytes": vs_stats.get("index_size_bytes", 0),
            }
        except Exception as e:
            logger.error("Failed to get KB status: %s", e)
            return {
                "success": False,
                "total_documents": 0,
                "total_chunks": 0,
                "documents": [],
                "error": str(e),
            }

    # ── prompt construction ───────────────────────────────

    def _build_rag_prompt(self, query: str, context: str) -> str:
        """Build a RAG prompt that grounds the LLM in retrieved context."""
        return f"""\
Based on the following excerpts from the student's uploaded academic documents, \
answer the question below. Use ONLY the information provided in the context. \
If the context doesn't contain enough information, say so clearly.

## Retrieved Context from Knowledge Base:
{context}

## Student's Question:
{query}

## Instructions:
- Answer based ONLY on the provided context
- Cite the source document(s) by name when referencing specific content
- If the context is insufficient, state: "The uploaded documents don't contain enough information about this specific topic."
- Be concise, accurate, and helpful for a student
- Format your response clearly with headings or bullet points if appropriate
"""

    # ── source formatting ─────────────────────────────────

    @staticmethod
    def format_sources(sources: list) -> str:
        """Format source documents into a human-readable string."""
        if not sources:
            return ""

        lines = ["**Sources:**"]
        for s in sources:
            page_info = f" (p.{s['page']})" if "page" in s else ""
            lines.append(f"- {s['filename']}{page_info}")

        return "\n".join(lines)

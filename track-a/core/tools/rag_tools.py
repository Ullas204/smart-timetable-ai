"""
LangChain tools for Knowledge Base / RAG search.

Provides tools that allow the LLM to search the student's uploaded
documents (notes, syllabus, question papers, etc.) for relevant context.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_knowledge_base(query: str, k: int = 4) -> str:
    """Search the student's uploaded Knowledge Base for relevant academic content. Use this tool when the user asks about their notes, study materials, syllabus, lecture content, previous question papers, university regulations, or any document they have uploaded. The tool returns the most relevant text chunks and source document names.

    Args:
        query: The search query describing what information to find (e.g., "Explain Deadlock", "Unit 3 DBMS topics", "eligibility criteria").
        k: Number of top relevant chunks to retrieve. Default is 4.
    """
    try:
        from core.rag import get_rag_pipeline

        if not query or not query.strip():
            return json.dumps({"success": False, "error": "Search query is required."})

        pipeline = get_rag_pipeline()
        result = pipeline.search(query.strip(), k=max(1, min(10, int(k))))

        logger.info("KB search: '%.50s...' → found=%s, chunks=%d",
                     query, result["found"], len(result.get("chunks", [])))

        return json.dumps({
            "success": True,
            "found": result["found"],
            "context": result["context"],
            "sources": result["sources"],
            "message": result["message"],
        })
    except Exception as e:
        logger.error("search_knowledge_base failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


@tool
def get_knowledge_base_status() -> str:
    """Check the status of the Knowledge Base. Returns the number of uploaded documents, total indexed chunks, embedding model, and vector store info. Use this when the user wants to know what documents are available or how much content is in the Knowledge Base.

    Args: None
    """
    try:
        from core.rag import get_rag_pipeline

        pipeline = get_rag_pipeline()
        status = pipeline.get_status()

        logger.info("KB status: %d docs, %d chunks",
                     status.get("total_documents", 0),
                     status.get("total_chunks", 0))
        return json.dumps(status)
    except Exception as e:
        logger.error("get_knowledge_base_status failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


RAG_TOOLS = [search_knowledge_base, get_knowledge_base_status]

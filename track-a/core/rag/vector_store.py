"""
FAISS Vector Store manager for the RAG pipeline.

Handles embedding generation via HuggingFace (BAAI/bge-small-en-v1.5),
FAISS index creation, persistence, and similarity search.
"""

import os
import logging
import shutil
from typing import List, Optional

from langchain_core.documents import Document

from core.rag.config import (
    EMBEDDING_MODEL, FAISS_INDEX_DIR, RETRIEVAL_K
)

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages the FAISS vector store with HuggingFace embeddings."""

    def __init__(self):
        self._embeddings = None
        self._faiss = None
        self._doc_store: dict = {}  # doc_id -> metadata for management

    # -- embeddings (lazy) ------------------------------------

    @property
    def embeddings(self):
        """Lazy-load the HuggingFace embedding model.

        The model is downloaded once on first use and cached locally
        by sentence-transformers (~130 MB for bge-small-en-v1.5).
        Subsequent calls reuse the cached instance.
        """
        if self._embeddings is None:
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
            except ImportError:
                raise ImportError(
                    "langchain-huggingface is required for embeddings. "
                    "Install it with: pip install langchain-huggingface sentence-transformers"
                )

            try:
                self._embeddings = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    model_kwargs={"device": "cpu"},
                    encode_kwargs={"normalize_embeddings": True},
                )
                logger.info("Initialized HuggingFace embeddings: %s", EMBEDDING_MODEL)
            except Exception as e:
                logger.error("Failed to load embedding model '%s': %s", EMBEDDING_MODEL, e)
                raise RuntimeError(
                    f"Failed to load embedding model '{EMBEDDING_MODEL}'. "
                    f"Ensure you have internet access for the first download. "
                    f"Error: {e}"
                ) from e

        return self._embeddings

    # -- FAISS index ------------------------------------------

    @property
    def faiss(self):
        """Lazy-load or create the FAISS index."""
        if self._faiss is None:
            self._faiss = self.load_index()
        return self._faiss

    def get_or_create_index(self, documents: Optional[List[Document]] = None):
        """Return existing FAISS index, or create a new one from documents."""
        if self._faiss is not None:
            return self._faiss

        # Try loading from disk first
        loaded = self.load_index()
        if loaded is not None:
            return loaded

        # Create new index from documents
        if documents:
            from langchain_community.vectorstores import FAISS
            self._faiss = FAISS.from_documents(documents, self.embeddings)
            self.save_index()
            logger.info("Created new FAISS index with %d documents.", len(documents))
        else:
            logger.info("No documents to index. FAISS index is empty.")

        return self._faiss

    def add_documents(self, documents: List[Document], doc_id: str) -> int:
        """Add document chunks to the FAISS index.

        Parameters
        ----------
        documents : List[Document]
            Chunked documents with metadata.
        doc_id : str
            Document ID for tracking.

        Returns
        -------
        int
            Number of chunks added.
        """
        if not documents:
            return 0

        try:
            from langchain_community.vectorstores import FAISS

            if self.faiss is None:
                # Create new index
                self._faiss = FAISS.from_documents(documents, self.embeddings)
            else:
                # Add to existing index
                self._faiss.add_documents(documents)

            self._doc_store[doc_id] = {
                "chunk_count": len(documents),
            }

            self.save_index()
            logger.info("Added %d chunks for doc '%s'.", len(documents), doc_id)
            return len(documents)

        except Exception as e:
            logger.error("Failed to add documents to FAISS: %s", e)
            raise

    def similarity_search(self, query: str, k: int = RETRIEVAL_K) -> List[Document]:
        """Find the most relevant document chunks for a query.

        Parameters
        ----------
        query : str
            The search query.
        k : int
            Number of top results to return.
        """
        if self.faiss is None:
            logger.warning("FAISS index is empty. No documents to search.")
            return []

        try:
            results = self.faiss.similarity_search(query, k=k)
            logger.info(
                "Similarity search returned %d results for query: %.50s...",
                len(results), query
            )
            return results
        except Exception as e:
            logger.error("FAISS similarity search failed: %s", e)
            return []

    def save_index(self) -> None:
        """Persist the FAISS index to disk."""
        if self._faiss is None:
            return

        try:
            os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
            self._faiss.save_local(FAISS_INDEX_DIR)
            logger.info("FAISS index saved to %s", FAISS_INDEX_DIR)
        except Exception as e:
            logger.error("Failed to save FAISS index: %s", e)

    def load_index(self):
        """Load the FAISS index from disk.

        Returns the loaded index, or None if not found/corrupted/incompatible.
        If the index was saved with a different embedding model (dimension mismatch),
        it is automatically cleared so a fresh index can be rebuilt on next upload.
        """
        try:
            from langchain_community.vectorstores import FAISS

            index_path = FAISS_INDEX_DIR
            if not os.path.exists(index_path):
                logger.info("No persisted FAISS index found at %s", index_path)
                return None

            self._faiss = FAISS.load_local(
                index_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("Loaded FAISS index from %s", index_path)
            return self._faiss

        except Exception as e:
            # Dimension mismatch or corrupted index -- clear and rebuild later
            logger.warning(
                "Failed to load FAISS index (will recreate on next upload): %s", e
            )
            self._faiss = None
            self._clear_index_directory()
            return None

    def delete_documents_by_id(self, doc_id: str) -> bool:
        """Remove documents with a specific doc_id from the index.

        FAISS doesn't support native delete, so we rebuild the index
        without the target documents.
        """
        if self.faiss is None:
            return False

        try:
            # Get all documents from the index
            all_docs = self.faiss.similarity_search("", k=self.faiss.index.ntotal)

            # Filter out documents matching the doc_id
            remaining = [doc for doc in all_docs if doc.metadata.get("doc_id") != doc_id]

            if len(remaining) == len(all_docs):
                logger.warning("No documents found with doc_id=%s", doc_id)
                return False

            # Rebuild index
            from langchain_community.vectorstores import FAISS
            if remaining:
                self._faiss = FAISS.from_documents(remaining, self.embeddings)
            else:
                self._faiss = None

            self._doc_store.pop(doc_id, None)
            self.save_index()
            logger.info("Deleted doc_id=%s, rebuilt index.", doc_id)
            return True

        except Exception as e:
            logger.error("Failed to delete doc_id=%s: %s", doc_id, e)
            return False

    def clear_index(self) -> None:
        """Wipe the FAISS index completely."""
        self._faiss = None
        self._doc_store.clear()
        self._clear_index_directory()

    def _clear_index_directory(self) -> None:
        """Remove the FAISS index directory from disk."""
        try:
            if os.path.exists(FAISS_INDEX_DIR):
                shutil.rmtree(FAISS_INDEX_DIR)
                logger.info("Cleared FAISS index directory.")
        except Exception as e:
            logger.error("Failed to clear FAISS index: %s", e)

    # -- stats -----------------------------------------------

    def get_index_stats(self) -> dict:
        """Return statistics about the current FAISS index."""
        stats = {
            "has_index": self._faiss is not None,
            "total_vectors": 0,
            "index_size_bytes": 0,
        }

        if self.faiss is not None:
            stats["total_vectors"] = self.faiss.index.ntotal

        if os.path.exists(FAISS_INDEX_DIR):
            total_size = 0
            for f in os.listdir(FAISS_INDEX_DIR):
                fp = os.path.join(FAISS_INDEX_DIR, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
            stats["index_size_bytes"] = total_size

        return stats

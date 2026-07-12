"""
Document ingestion and chunking for the RAG pipeline.

Handles loading PDF, TXT, and DOCX files, splitting them into
optimized chunks with metadata, and deduplication via hashing.
"""

import os
import hashlib
import logging
from typing import List, Optional, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.rag.config import (
    CHUNK_SIZE, CHUNK_OVERLAP, SUPPORTED_FORMATS, MAX_FILE_SIZE_MB, UPLOAD_DIR
)

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Loads, validates, and chunks documents for vector indexing."""

    def __init__(
        self,
        chunk_size: int = CHUNK_SIZE,
        chunk_overlap: int = CHUNK_OVERLAP,
    ):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    # ── public API ────────────────────────────────────────

    def validate_file(self, filename: str, file_size_bytes: int = 0) -> Tuple[bool, str]:
        """Check if a file is supported and within size limits.

        Returns (is_valid, error_message).
        """
        ext = os.path.splitext(filename)[1].lower()

        if ext not in SUPPORTED_FORMATS:
            return False, (
                f"Unsupported format '{ext}'. "
                f"Supported: {', '.join(SUPPORTED_FORMATS)}"
            )

        max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size_bytes > max_bytes:
            return False, (
                f"File too large ({file_size_bytes / 1024 / 1024:.1f}MB). "
                f"Maximum: {MAX_FILE_SIZE_MB}MB"
            )

        return True, ""

    def generate_doc_id(self, filename: str, file_size: int) -> str:
        """Generate a deterministic document ID from filename and size."""
        raw = f"{filename}:{file_size}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def load_document(self, file_path: str) -> List[Document]:
        """Load a document using the appropriate LangChain loader.

        Supports PDF (pypdf), TXT (text), and DOCX (docx2txt).
        """
        ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path)

        try:
            if ext == ".pdf":
                return self._load_pdf(file_path, filename)
            elif ext == ".txt":
                return self._load_text(file_path, filename)
            elif ext == ".docx":
                return self._load_docx(file_path, filename)
            else:
                logger.warning("Unsupported file format: %s", ext)
                return []
        except Exception as e:
            logger.error("Failed to load document '%s': %s", filename, e)
            # Re-raise with context so the UI can display the error
            raise RuntimeError(f"Failed to load '{filename}': {e}") from e

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split loaded documents into optimized chunks."""
        if not documents:
            return []

        chunks = self._splitter.split_documents(documents)
        logger.info(
            "Split %d document(s) into %d chunks.", len(documents), len(chunks)
        )
        return chunks

    def process_file(self, file_path: str, doc_id: str) -> List[Document]:
        """Full pipeline: load → split → add metadata → return chunks.

        Parameters
        ----------
        file_path : str
            Path to the saved file on disk.
        doc_id : str
            The unique document ID for metadata tagging.
        """
        filename = os.path.basename(file_path)

        # Load raw documents
        raw_docs = self.load_document(file_path)
        if not raw_docs:
            logger.warning("No content extracted from '%s'.", filename)
            return []

        # Check if all pages have empty content (scanned/image PDF)
        total_chars = sum(len(doc.page_content.strip()) for doc in raw_docs)
        if total_chars < 10:
            logger.warning(
                "Document '%s' has almost no extractable text (%d chars). "
                "It may be a scanned/image PDF. OCR is not supported.",
                filename, total_chars,
            )
            return []

        # Split into chunks
        chunks = self.split_documents(raw_docs)

        # Enrich metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata["doc_id"] = doc_id
            chunk.metadata["source"] = filename
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(chunks)

        logger.info(
            "Processed '%s': %d chunks created.", filename, len(chunks)
        )
        return chunks

    def _validate_file_content(self, file_content: bytes, filename: str) -> Tuple[bool, str]:
        """Validate file content to detect disguised executables or binary masquerading."""
        if len(file_content) < 4:
            return False, "File is too small or empty"

        # Check for common executable signatures
        exe_signatures = [
            b'MZ',      # PE executable
            b'\x7fELF', # ELF executable
            b'PK',      # Could be ZIP (also DOCX), but check further
            b'%PDF',    # PDF header (valid for PDFs)
        ]
        ext = os.path.splitext(filename)[1].lower()

        # PDFs should start with %PDF
        if ext == '.pdf' and not file_content[:4].startswith(b'%PDF'):
            return False, "Invalid PDF file (missing PDF header)"

        # Reject PE/ELF executables regardless of extension
        if file_content[:2] == b'MZ' and ext != '.pdf':
            return False, "File appears to be an executable"
        if file_content[:4] == b'\x7fELF':
            return False, "File appears to be an executable"

        # For text files, check they're actually text
        if ext == '.txt':
            try:
                file_content[:1024].decode('utf-8')
            except UnicodeDecodeError:
                return False, "Text file contains invalid encoding"

        return True, ""

    def save_uploaded_file(
        self, file_content: bytes, filename: str, doc_id: str
    ) -> Optional[str]:
        """Save an uploaded file to disk after content validation.

        Returns the saved file path, or None on failure.
        """
        is_valid, err = self._validate_file_content(file_content, filename)
        if not is_valid:
            logger.warning("File content validation failed for '%s': %s", filename, err)
            return None

        try:
            doc_dir = os.path.join(UPLOAD_DIR, doc_id)
            os.makedirs(doc_dir, exist_ok=True)

            file_path = os.path.join(doc_dir, filename)
            with open(file_path, "wb") as f:
                f.write(file_content)

            logger.info("Saved uploaded file: %s", file_path)
            return file_path
        except Exception as e:
            logger.error("Failed to save file '%s': %s", filename, e)
            return None

    # ── private loaders ───────────────────────────────────

    def _load_pdf(self, file_path: str, filename: str) -> List[Document]:
        """Load a PDF file using pypdf directly (avoids langchain_community import issues)."""
        import sys
        _vendor = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vendor")
        if os.path.isdir(_vendor) and _vendor not in sys.path:
            sys.path.insert(0, _vendor)
        import pypdf

        reader = pypdf.PdfReader(file_path)
        docs = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                docs.append(Document(
                    page_content=text,
                    metadata={"source": filename, "file_type": "pdf", "page": i + 1},
                ))
        logger.debug("Loaded PDF '%s': %d pages with text.", filename, len(docs))
        return docs

    def _load_text(self, file_path: str, filename: str) -> List[Document]:
        """Load a plain text file."""
        from langchain_community.document_loaders import TextLoader

        loader = TextLoader(file_path, encoding="utf-8")
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = filename
            doc.metadata["file_type"] = "txt"
        logger.debug("Loaded TXT '%s': %d section(s).", filename, len(docs))
        return docs

    def _load_docx(self, file_path: str, filename: str) -> List[Document]:
        """Load a DOCX file using docx2txt."""
        from langchain_community.document_loaders import Docx2txtLoader

        loader = Docx2txtLoader(file_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = filename
            doc.metadata["file_type"] = "docx"
        logger.debug("Loaded DOCX '%s': %d section(s).", filename, len(docs))
        return docs

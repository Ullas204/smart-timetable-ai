# RAG Workflow

## Overview

The RAG (Retrieval-Augmented Generation) pipeline enables the AI assistant to answer questions grounded in uploaded student documents (PDF, TXT, DOCX).

## Pipeline Architecture

```
┌─────────────────────────────────────────────────┐
│              Upload Phase                        │
│                                                  │
│  File Upload → Validate → Load → Chunk → Embed   │
│               (size,     (PyPDF,  (Recursive   │  (Google
│                format)   TextLoader, CharSplit)  │  text-embedding-004)
│                                         │       │
│                                    ┌────┴────┐  │
│                                    │ FAISS   │  │
│                                    │ Index   │  │
│                                    └─────────┘  │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│              Query Phase                         │
│                                                  │
│  User Query → Embed → FAISS Search (top-k=4)     │
│                           │                      │
│                    ┌──────┴──────┐               │
│                    │ Top-K       │               │
│                    │ Chunks +    │               │
│                    │ Source Meta │               │
│                    └──────┬──────┘               │
│                           │                      │
│                    LLM Synthesis                 │
│                    (with source citations)        │
└─────────────────────────────────────────────────┘
```

## Components

### DocumentProcessor
- **validate_file()**: Checks format (PDF/TXT/DOCX) and size (max 50MB)
- **generate_doc_id()**: SHA256 hash of filename+size, truncated to 16 chars (dedup)
- **load_document()**: Routes to PyPDFLoader, TextLoader, or Docx2txtLoader
- **split_documents()**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- **process_file()**: Load → split → add metadata (doc_id, filename)

### VectorStoreManager
- **FAISS index**: Persistent on disk at `faiss_index/`
- **Embeddings**: Google `text-embedding-004` via LangChain
- **add_documents()**: Embed chunks → add to FAISS index → save to disk
- **similarity_search()**: Query embedding → FAISS kNN search → return chunks with metadata
- **delete_documents_by_id()**: Remove vectors by document ID

### RAGPipeline
- **search(query, k=4)**: FAISS search → return formatted results
- **answer(query, k=4)**: Search → build context → LLM synthesis with RAG prompt
- **get_status()**: Document count, chunk count, index size

## Configuration

| Parameter | Value | Source |
|-----------|-------|--------|
| Chunk Size | 1000 chars | `core/rag/config.py` |
| Chunk Overlap | 200 chars | `core/rag/config.py` |
| Retrieval K | 4 | `core/rag/config.py` |
| Embedding Model | text-embedding-004 | `core/rag/config.py` |
| Max File Size | 50 MB | `core/rag/config.py` |
| Supported Formats | PDF, TXT, DOCX | `core/rag/config.py` |

## Database Schema (documents table)

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    filename TEXT,
    file_path TEXT,
    file_type TEXT,
    file_size INTEGER,
    chunk_count INTEGER DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'indexed'
);
```

## Integration with Agent

1. Agent receives user query
2. LLM decides to call `search_knowledge_base(query="...")`
3. Tool invokes `RAGPipeline.search()` → returns chunks + sources
4. LLM receives tool result and synthesizes answer with citations
5. UI displays answer + source documents

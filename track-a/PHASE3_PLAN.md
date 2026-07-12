# Phase 3 – LangChain RAG Integration: Implementation Plan

## Architecture Overview

```
User Query
    │
    ▼
AcademicAgent.execute(query, memory)
    │
    ├── LLM (Gemini 2.0 Flash) + 35 existing tools
    │   └── NEW: + 2 RAG tools (search_knowledge_base, get_knowledge_base_status)
    │
    ├── If query is about documents → LLM calls search_knowledge_base tool
    │       │
    │       ▼
    │   RAGRetriever.search(query)
    │       │
    │       ├── Embed query (Google text-embedding-004)
    │       ├── FAISS similarity search (top-k chunks)
    │       └── Return context chunks + metadata
    │
    └── LLM generates answer grounded in retrieved context
        (with source attribution)
```

## New Files (6 files)

### 1. `core/rag/__init__.py` — RAG Package Init
- Exports: `RAGPipeline`, `get_rag_pipeline`
- Lazy singleton pattern (like `core/llm.py`)

### 2. `core/rag/config.py` — RAG Configuration
- `RAGSettings` class with constants:
  - `CHUNK_SIZE = 1000`
  - `CHUNK_OVERLAP = 200`
  - `RETRIEVAL_K = 4` (top-k chunks)
  - `FAISS_INDEX_DIR = "faiss_index"`
  - `UPLOAD_DIR = "knowledge_base"`
  - `SUPPORTED_FORMATS = [".pdf", ".txt", ".docx"]`
  - `EMBEDDING_MODEL = "models/text-embedding-004"`

### 3. `core/rag/document_processor.py` — Document Ingestion & Chunking
- `DocumentProcessor` class with methods:
  - `load_document(file_path) → List[Document]`
    - Detects format by extension
    - Uses `PyPDFLoader` for .pdf, `TextLoader` for .txt, `Docx2txtLoader` for .docx
  - `split_documents(documents) → List[Document]`
    - Uses `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)`
    - Adds metadata: source filename, page/section number
  - `process_file(file_path, doc_id) → List[Document]`
    - Full pipeline: load → split → add metadata → return chunks
  - `validate_file(filename) → (bool, str)`
    - Checks extension, file size (max 50MB), returns error if invalid
  - `generate_doc_id(filename, file_size) → str`
    - SHA256 hash of filename + size for deduplication

### 4. `core/rag/vector_store.py` — FAISS Vector Store Management
- `VectorStoreManager` class with methods:
  - `__init__()` — initializes embeddings (`GoogleGenerativeAIEmbeddings`) + FAISS index
  - `get_embeddings() → GoogleGenerativeAIEmbeddings`
    - Lazy-loaded, uses same GEMINI_API_KEY from Settings
  - `get_or_create_index(documents) → FAISS`
    - Creates new or loads existing FAISS index from disk
  - `add_documents(documents, doc_id) → int`
    - Chunks → embeddings → add to FAISS, returns chunk count
  - `similarity_search(query, k=4) → List[Document]`
    - Embeds query → FAISS search → return top-k chunks with metadata
  - `save_index() → None`
    - Persists FAISS index to disk (`faiss_index/`)
  - `load_index() → Optional[FAISS]`
    - Loads from disk if exists, returns None otherwise
  - `get_index_stats() → dict`
    - Returns total vectors, index size on disk, last updated
  - `delete_document(doc_id) → bool`
    - Removes vectors by document ID (rebuild index)
  - `clear_index() → None`
    - Wipes FAISS index and persisted files

### 5. `core/rag/pipeline.py` — RAG Pipeline (Retriever + Generation)
- `RAGPipeline` class with methods:
  - `__init__()` — lazy-loads VectorStoreManager + LLM
  - `search(query, k=4) → dict`
    - Calls VectorStoreManager.similarity_search()
    - Returns `{"context": str, "sources": List[dict], "found": bool}`
  - `answer(query, k=4) → dict`
    - search() → build RAG prompt with context → invoke LLM
    - Returns `{"answer": str, "sources": List[dict], "used_rag": bool}`
  - `get_status() → dict`
    - Returns vector store stats, document count, index size
  - `_build_rag_prompt(query, context) → str`
    - Constructs prompt that instructs LLM to answer from context only
    - Includes instruction: "If the context doesn't contain the answer, say so clearly."
  - `_format_sources(documents) → List[dict]`
    - Extracts filename, page number, text preview from each Document

### 6. `core/tools/rag_tools.py` — LangChain RAG Tools
Two `@tool` decorated functions:
  - `search_knowledge_base(query: str, k: int = 4) → str`
    - Description: "Search the knowledge base of uploaded academic documents (notes, syllabus, question papers, regulations). Use this when the user asks questions about their study materials, uploaded notes, or any document content."
    - Calls `RAGPipeline.search(query, k)`
    - Returns JSON with context chunks + sources
  - `get_knowledge_base_status() → str`
    - Description: "Check the status of the knowledge base - how many documents are indexed, total chunks, and storage size."
    - Calls `RAGPipeline.get_status()`
    - Returns JSON with stats

## Modified Files (6 files)

### 7. `core/config.py` — Add RAG Settings
Add to `Settings` class:
```python
# ── RAG / Knowledge Base ──────────────────────────────
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
RETRIEVAL_K: int = int(os.getenv("RETRIEVAL_K", "4"))
FAISS_INDEX_DIR: str = os.getenv("FAISS_INDEX_DIR", "faiss_index")
UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "knowledge_base")
```

### 8. `core/tools/__init__.py` — Register RAG Tools
Add import + group:
```python
from core.tools.rag_tools import RAG_TOOLS
```
Add to TOOL_GROUPS:
```python
"knowledge_base": RAG_TOOLS,
```

### 9. `core/agent_executor.py` — Update System Prompt + RAG Integration
Changes:
a) Update SYSTEM_PROMPT to add:
   - Capability #14: **Knowledge Base (RAG)**: search_knowledge_base, get_knowledge_base_status
   - Tool Calling Rule: When user asks about their notes, syllabus, study materials, uploaded documents → use search_knowledge_base
   - Rule: "If the knowledge base is empty, tell the user to upload documents first"
   - Rule: "Always cite the source document when answering from the knowledge base"

b) Update `_build_system_prompt()` to include a `{rag_status}` placeholder that shows current KB stats so the LLM knows if documents are available.

### 10. `db.py` — Add Documents Table
Add `documents` table to `init_db()`:
```sql
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT,
    file_path TEXT,
    file_type TEXT,
    file_size INTEGER,
    chunk_count INTEGER DEFAULT 0,
    uploaded_at TEXT DEFAULT (datetime('now')),
    status TEXT DEFAULT 'indexed'
)
```
Add CRUD functions:
- `insert_document(doc_id, filename, file_path, file_type, file_size, chunk_count)`
- `fetch_documents() → list`
- `delete_document(doc_id) → bool`
- `get_document(doc_id) → Optional[tuple]`

### 11. `app.py` — Add Knowledge Base Tab + Upload UI
Changes:
a) Add import block:
```python
try:
    from core.rag import get_rag_pipeline
    _has_rag = True
except ImportError:
    _has_rag = False
```

b) Add 9th tab:
```python
tabs = st.tabs([...existing 8..., "\U0001f4da Knowledge Base"])
tab_dash, tab_cal, tab_tasks, tab_stats, tab_agents, tab_voice, tab_ai, tab_settings, tab_kb = tabs
```

c) New `tab_kb` section with:
   - File uploader (PDF, TXT, DOCX)
   - Process button → validates, chunks, embeds, stores in FAISS
   - Document list with delete buttons
   - KB stats (total docs, chunks, index size)
   - Processing progress indicator

d) In AI Assistant tab: Add RAG source display when `is_tool_call=True` and tool is `search_knowledge_base`

### 12. `requirements.txt` — Add Dependencies
```
# Phase 3: RAG Integration
faiss-cpu>=1.7
langchain-text-splitters>=0.3
pypdf>=4.0
docx2txt>=0.8
```

## Document Processing Flow

```
User uploads file in Streamlit
    │
    ├── Validate: extension, size (max 50MB)
    ├── Generate doc_id (SHA256 hash)
    ├── Save to disk: knowledge_base/{doc_id}/{filename}
    │
    ▼
DocumentProcessor.process_file(path, doc_id)
    │
    ├── Load: PyPDFLoader / TextLoader / Docx2txtLoader
    ├── Split: RecursiveCharacterTextSplitter(1000, 200)
    ├── Add metadata: source=filename, doc_id, page/section
    │
    ▼
VectorStoreManager.add_documents(chunks, doc_id)
    │
    ├── Embed: GoogleGenerativeAIEmbeddings (text-embedding-004)
    ├── Store: FAISS.add_documents()
    ├── Save: FAISS index to disk (faiss_index/)
    │
    ▼
db.insert_document(doc_id, filename, path, type, size, chunk_count)
```

## RAG Query Flow

```
User: "Explain Deadlock from my OS notes"
    │
    ▼
AcademicAgent.execute(query)
    │
    ├── LLM sees tool descriptions → decides to call search_knowledge_base
    │
    ▼
search_knowledge_base("Explain Deadlock from my OS notes")
    │
    ├── RAGPipeline.search("Explain Deadlock")
    │   ├── Embed query → FAISS similarity_search(k=4)
    │   └── Return top-4 chunks with metadata
    │
    ├── Returns JSON:
    │   {"found": True, "context": "Deadlock is a condition...", 
    │    "sources": [{"filename": "os_notes.pdf", "preview": "..."}]}
    │
    ▼
LLM generates answer using retrieved context
    │
    ├── Answer grounded in document content
    ├── Sources cited in response
    └── If nothing found: "No relevant information found in the Knowledge Base."
```

## Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| Unsupported file format | UI shows "Unsupported format. Use PDF, TXT, or DOCX." |
| Empty file / 0 pages | UI shows "Document appears empty." |
| Duplicate document (same hash) | UI shows "Document already in Knowledge Base." |
| Embedding API failure | Log error, show "Embedding failed. Check API key." |
| FAISS index corrupted | Auto-rebuild from scratch on next upload |
| KB empty when querying | LLM told to respond "Knowledge Base is empty. Upload documents first." |
| Query finds no relevant chunks | Tool returns `found: false`, LLM says "No relevant information found." |
| Max file size exceeded (50MB) | UI shows "File too large. Maximum 50MB." |

## File Storage Layout

```
track-a/
├── knowledge_base/           # Uploaded documents
│   ├── {doc_id_1}/
│   │   └── os_notes.pdf
│   └── {doc_id_2}/
│       └── dbms_chapter3.txt
├── faiss_index/              # Persisted FAISS index
│   ├── index.faiss
│   └── index.pkl
├── db.sqlite3               # Updated: + documents table
└── ...existing files...
```

## New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `faiss-cpu` | >=1.7 | Vector similarity search |
| `langchain-text-splitters` | >=0.3 | RecursiveCharacterTextSplitter |
| `pypdf` | >=4.0 | PDF document loader |
| `docx2txt` | >=0.8 | DOCX document loader |

## Testing Checklist

After implementation, verify:
1. [ ] Upload a PDF → chunks indexed → search returns relevant content
2. [ ] Upload a TXT → chunks indexed → search works
3. [ ] Upload a DOCX → chunks indexed → search works
4. [ ] Duplicate upload detected and rejected
5. [ ] Unsupported format rejected with error message
6. [ ] "Explain Deadlock from my OS notes" → searches KB → answers from context
7. [ ] "Summarize Unit 3 from DBMS notes" → searches KB → answers
8. [ ] "What are eligibility criteria?" (no relevant docs) → "No relevant information found"
9. [ ] KB status tool returns correct stats
10. [ ] Delete document → removed from FAISS index + disk
11. [ ] All 35 existing tools still work (no regression)
12. [ ] Dashboard, Calendar, Tasks, Analytics tabs unaffected
13. [ ] AI Assistant chat still works for non-RAG queries
14. [ ] Voice commands still work
15. [ ] Email notifications still work

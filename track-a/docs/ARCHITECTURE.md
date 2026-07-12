# System Architecture

## Overview

Smart Academic OS is an **AI-powered academic management platform** built with Streamlit, LangChain, Google Gemini, and FAISS. It uses a **unified agent architecture** where a single LangChain-powered agent handles all user queries through automatic tool calling and RAG retrieval.

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                     │
│  ┌──────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐  │
│  │Dashboard │ │Calendar│ │  Tasks   │ │  AI Assistant │  │
│  │  (9 tabs)│ │  Sync  │ │ (Kanban) │ │   (Chat+RAG)  │  │
│  └────┬─────┘ └───┬────┘ └────┬─────┘ └──────┬───────┘  │
│       │           │           │               │           │
│  ┌────┴───────────┴───────────┴───────────────┴───────┐  │
│  │              Application Layer (app.py)            │  │
│  └───────────────────────┬────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────┐
│              LangChain Agentic AI Core (core/)            │
│  ┌──────────────┐  ┌─────┴─────┐  ┌──────────────────┐  │
│  │AgentExecutor │──│ Tool Bind │──│  RAG Pipeline     │  │
│  │ (37 tools)   │  │ (LangChain│  │  (FAISS + Gemini │  │
│  │              │  │  @tools)  │  │   Embeddings)    │  │
│  └──────┬───────┘  └─────┬─────┘  └────────┬─────────┘  │
│         │                │                  │             │
│  ┌──────┴───────┐  ┌─────┴─────┐  ┌────────┴─────────┐  │
│  │ ChatMemory   │  │  Tool     │  │  VectorStore     │  │
│  │ (session)    │  │  Registry │  │  (FAISS index)   │  │
│  └──────────────┘  └───────────┘  └──────────────────┘  │
│                                                          │
│  ┌──────────────┐  ┌────────────┐  ┌─────────────────┐  │
│  │ LLM Client   │  │  Schemas   │  │   Config        │  │
│  │ (Gemini 2.0) │  │ (Pydantic) │  │   (Settings)    │  │
│  └──────────────┘  └────────────┘  └─────────────────┘  │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────┐
│                    Backend Layer                          │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌──────────┐  │
│  │  db.py   │ │ models.py│ │ agents/    │ │ gamifi-  │  │
│  │ (SQLite) │ │ (CRUD)   │ │ (5 domain  │ │ cation   │  │
│  │          │ │          │ │  agents)   │ │          │  │
│  └──────────┘ └──────────┘ └────────────┘ └──────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌──────────┐  │
│  │ google_  │ │ scheduler│ │ email_     │ │ voice_   │  │
│  │ calendar │ │ _pro.py  │ │ utils.py   │ │ module   │  │
│  └──────────┘ └──────────┘ └────────────┘ └──────────┘  │
└──────────────────────────────────────────────────────────┘
```

## Module Breakdown

### Core Layer (`core/`)
| Module | Purpose | Key Class/Function |
|--------|---------|-------------------|
| `agent_executor.py` | Unified agent with tool binding + RAG | `AcademicAgent.execute()` |
| `llm.py` | Shared Gemini LLM singleton | `get_llm()` |
| `memory.py` | Session-scoped chat history | `ChatMemory`, `FallbackMemory` |
| `schemas.py` | Pydantic models for agent I/O | `AgentResponse`, `ToolExecution` |
| `config.py` | Settings from env vars | `Settings` class |
| `tools/` | 37 LangChain tools (14 groups) | `get_all_tools()` |
| `rag/` | RAG pipeline (FAISS + embeddings) | `RAGPipeline`, `VectorStoreManager` |

### Backend Layer
| Module | Purpose |
|--------|---------|
| `db.py` | SQLite CRUD (10 tables) |
| `models.py` | Thin wrappers over db.py |
| `agents/` | 5 domain agents (planner, rescheduler, readiness, wellness, analytics) |
| `gamification.py` | XP, levels, achievements |
| `google_calendar.py` | Google Calendar API integration |
| `scheduler_pro.py` | Conflict detection + optimal time suggestion |
| `email_utils.py` | SMTP email sending |
| `notification_engine.py` | Notification dispatch |
| `voice_module.py` | Voice command processing |
| `ai_agent.py` | Legacy keyword NLP fallback |

### Frontend Layer
| File | Purpose |
|------|---------|
| `app.py` | Streamlit UI (9 tabs, 1383 lines) |

## Data Flow

```
User Input → Streamlit UI → AcademicAgent.execute()
                              │
                              ├── LLM with tool binding
                              │   ├── Direct answer → UI
                              │   ├── Tool call(s) → Execute → LLM summary → UI
                              │   ├── RAG search → LLM synthesis → UI
                              │   └── Combined tools + RAG → LLM → UI
                              │
                              └── Fallback: ai_agent.process_query() → UI
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit 1.28+ |
| LLM | Google Gemini 2.0 Flash |
| Agent Framework | LangChain + LangChain-Google-Genai |
| Embeddings | Google text-embedding-004 |
| Vector Store | FAISS (CPU) |
| Database | SQLite 3 |
| Document Processing | PyPDF, docx2txt, RecursiveCharacterTextSplitter |
| Calendar | Google Calendar API v3 |
| Email | SMTP (Gmail) |

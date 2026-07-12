# Demo Script & Viva Questions

## Demo Flow (5 minutes)

### 1. Introduction (30s)
"Smart Academic OS is an AI-powered academic management platform using LangChain, Google Gemini, and FAISS for RAG."

### 2. Dashboard Overview (30s)
- Show Dashboard tab with today's events/tasks
- Show gamification widgets (level, XP, streak)

### 3. AI Assistant - Tool Calling (60s)
- Type: "What's on my schedule today?"
- Show tool badges and response
- Type: "Create a task: Write essay due tomorrow, high priority"
- Verify task appears in Tasks tab
- Type: "How productive was I this week?"
- Show analytics tool result

### 4. RAG Demo (60s)
- Go to Knowledge Base tab
- Upload a sample PDF
- Ask in AI Assistant: "Summarize the uploaded document"
- Show RAG indicator and source citations
- Ask: "What are the key concepts in Chapter 2?"
- Show combined tool + RAG query

### 5. Study Planning (30s)
- Show Study Plan tab
- Generate a study plan for upcoming exams
- Show AI's personalized schedule

### 6. Focus Timer & Gamification (30s)
- Start a Pomodoro session
- Show XP earning and level progress
- Show achievements tab

### 7. Deployment (30s)
- Show HF Spaces URL
- Mention mobile accessibility

## Viva Questions & Answers

### Architecture
**Q: What is the overall architecture?**
A: Streamlit frontend → Unified LangChain agent → 37 tools + RAG pipeline → SQLite backend. Single agent handles all queries through automatic tool binding.

**Q: Why LangChain over direct Gemini API?**
A: LangChain provides structured tool calling, automatic prompt management, chat history handling, and extensibility. Direct API would require manual JSON parsing and routing.

**Q: How does the agent decide whether to use tools or RAG?**
A: The system prompt defines a 4-mode decision framework. The LLM analyzes the query, considers available tools, and decides: Direct answer, Tool calling, RAG search, or Combined.

### RAG
**Q: How does RAG work in this system?**
A: Documents are chunked (1000 chars, 200 overlap), embedded via Google text-embedding-004, stored in FAISS. Queries are embedded, kNN search retrieves top-4 chunks, LLM synthesizes answer with citations.

**Q: Why FAISS over Pinecone/Chroma?**
A: FAISS runs locally (no external service), is free, fast for small-medium collections, and works offline. Ideal for student use case with limited documents.

**Q: How do you handle document deduplication?**
A: SHA256 hash of filename+size generates a doc_id. Before re-indexing, existing chunks with same doc_id are deleted.

### Agent
**Q: How many tools does the agent have?**
A: 37 tools across 14 domains: event management, tasks, study planning, rescheduling, exam readiness, wellness, analytics, focus/gamification, notifications, attendance, profile, subjects/exams, voice, and knowledge base.

**Q: What happens if Gemini API is unavailable?**
A: Falls back to ai_agent.py which uses Gemini directly or keyword-based NLP as last resort. Returns same AgentResponse structure for backward compatibility.

### Performance
**Q: How do you optimize for repeated queries?**
A: XP calculation cached per request (gamification triple-call reduced to 1 DB query), Google Calendar service cached, LLM singleton per session, FAISS index persistent on disk.

**Q: How do you handle database concurrency?**
A: SQLite with WAL mode (default on HF Spaces), context manager for connections, transactions for multi-table writes.

### Deployment
**Q: How is this deployed?**
A: Hugging Face Spaces with Streamlit SDK. Secrets managed via HF repository secrets. FAISS index persisted on disk, SQLite file-based.

**Q: What are the limitations?**
A: SQLite concurrent writes limited, FAISS index rebuilds needed on re-upload, no real-time push notifications, Gemini API rate limits.

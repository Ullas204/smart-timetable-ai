# 🎓 Smart Academic OS

An AI-powered academic assistant that unifies scheduling, task management, study planning, and knowledge management into a single intelligent interface using **LangChain**, **Google Gemini**, and **FAISS**.

---

## 🚀 Features

- **RAG-Powered Knowledge Base** — Upload PDFs, TXT, DOCX files and get grounded, source-cited answers using `BAAI/bge-small-en-v1.5` embeddings + FAISS vector search
- **20+ LangChain Tools** — Calendar, tasks, study planning, exam readiness, wellness tracking, analytics, notifications, and more
- **5 Domain AI Agents** — Planner, Rescheduler, Readiness, Wellness, and Analytics agents
- **Zero-shot ReAct Pattern** — Agent autonomously decides which tools to call per query
- **4 Execution Modes** — Direct Answer, Tool Call, RAG Search, Combined
- **Fallback Intelligence** — Knowledge base stays accessible even when LLM is unavailable
- **Conversation Memory** — Session-scoped chat history for context-aware responses
- **Prompt Injection Protection** — Input sanitization and safety guards
- **Gamification** — XP system, levels, and achievements
- **Voice Commands** — Voice-controlled academic assistance
- **Google Calendar Sync** — OAuth2 integration for event synchronization

---

## 🏗️ Architecture

```
UI (Streamlit)
    ↓
AcademicAgent (agent_executor.py)
    ↓
┌────────────┬────────────┬────────────┐
│   Tools    │  RAG Pipeline │  Domain   │
│  (20+)     │  bge-small   │  Agents   │
│            │  → FAISS     │  (5)      │
└────────────┴────────────┴────────────┘
    ↓
SQLite + FAISS + External APIs (Gemini, GCal, SMTP)
```

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Framework | LangChain + Streamlit |
| LLM | Google Gemini 2.0 Flash |
| Embeddings | BAAI/bge-small-en-v1.5 |
| Vector DB | FAISS |
| Database | SQLite3 |
| Hosting | Local / Hugging Face Spaces |

---

## 📁 Project Structure

```
track-a/
├── app.py                  # Streamlit entry point
├── core/
│   ├── agent_executor.py   # AcademicAgent (main LangChain module)
│   ├── config.py           # Centralized settings
│   ├── llm.py              # Shared Gemini LLM singleton
│   ├── memory.py           # Conversation memory
│   ├── schemas.py          # Pydantic schemas
│   ├── rag/                # RAG pipeline
│   │   ├── config.py       # RAG constants
│   │   ├── document_processor.py
│   │   ├── vector_store.py # FAISS + Embeddings
│   │   └── pipeline.py     # Search + Answer
│   └── tools/              # 20+ LangChain tools
├── agents/                 # Domain sub-agents
├── docs/                   # Documentation
├── requirements.txt
└── .env                    # Secrets (not committed)
```

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Ullas204/smart-timetable-ai.git
cd smart-timetable-ai/track-a
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment
Create a `.env` file in `track-a/`:
```
GEMINI_API_KEY=your_google_gemini_api_key
EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 4. Run the app
```bash
streamlit run app.py
```

---

## 🔑 Required Secrets

| Secret | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key ([Get one here](https://ai.google.dev/)) |
| `EMAIL` | Gmail address for notifications |
| `EMAIL_PASSWORD` | Gmail app password |

---

## 📦 Dependencies

- `langchain`, `langchain-core`, `langchain-community`
- `langchain-google-genai`, `langchain-huggingface`
- `sentence-transformers`, `faiss-cpu`
- `streamlit`, `streamlit-calendar`
- `pypdf`, `docx2txt`
- `google-generativeai`, `google-api-python-client`

---

## 🧪 Testing

```bash
pytest tests.py -v
```

43 tests covering database, agents, tools, RAG pipeline, schemas, and configuration.

---

## 📄 License

MIT License

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

**Built with LangChain + Streamlit + Google Gemini + FAISS + HuggingFace**

# Deployment Guide

## Prerequisites

- Python 3.10+
- Google Gemini API key
- (Optional) Google Calendar OAuth2 credentials
- (Optional) Gmail App Password for email notifications

## Local Development

```bash
# 1. Clone and navigate
cd track-a

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .streamlit/secrets.toml
cp .streamlit/secrets_template.toml .streamlit/secrets.toml
# Edit secrets.toml with your API keys

# 5. Run the app
streamlit run app.py --server.port 8501
```

## Hugging Face Spaces Deployment

### Setup

1. Create a new Space at huggingface.co/new
2. Select **Streamlit** as the SDK
3. Set Python version to 3.10+

### Required Files (already prepared)

| File | Purpose |
|------|---------|
| `app.py` | Application entry point |
| `requirements.txt` | Pinned dependencies |
| `README.md` | YAML frontmatter with emoji + SDK config |
| `.streamlit/config.toml` | Theme + server settings |

### Secrets (add in HF Spaces Settings → Repository Secrets)

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Optional secrets:
```
GOOGLE_CALENDAR_CREDENTIALS={"type":"service_account",...}
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### File Structure for HF Spaces

```
track-a/
├── app.py
├── requirements.txt
├── README.md
├── db.py
├── models.py
├── ai_agent.py
├── gamification.py
├── study_planner.py
├── scheduler_pro.py
├── google_calendar.py
├── email_utils.py
├── notification_engine.py
├── analytics.py
├── voice_module.py
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml  (via HF Secrets)
├── core/
│   ├── __init__.py
│   ├── agent_executor.py
│   ├── llm.py
│   ├── memory.py
│   ├── schemas.py
│   ├── config.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── knowledge_tools.py
│   │   ├── voice_tools.py
│   │   └── ... (14 tool modules)
│   └── rag/
│       ├── __init__.py
│       ├── config.py
│       ├── pipeline.py
│       ├── vector_store.py
│       └── document_processor.py
├── agents/
│   ├── __init__.py
│   ├── planner_agent.py
│   ├── rescheduler_agent.py
│   ├── readiness_agent.py
│   ├── wellness_agent.py
│   └── analytics_agent.py
└── tests.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `No API key` | Add GEMINI_API_KEY to HF Secrets or .streamlit/secrets.toml |
| FAISS crash on Windows | Use `faiss-cpu` (already in requirements.txt) |
| Google Calendar 403 | Re-authenticate OAuth2, check scopes |
| Email fails | Verify Gmail App Password (not account password) |

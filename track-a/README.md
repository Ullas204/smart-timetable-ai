---
title: Smart Academic OS
emoji: 🎓
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: "1.28.0"
app_file: app.py
pinned: false
license: mit
---

# Smart Academic OS

AI-powered academic assistant with LangChain RAG + Tool Calling.

## Setup

Set these **Secrets** in your HF Space settings:

```
GEMINI_API_KEY=your_google_gemini_api_key
EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

## Features

- RAG-powered knowledge base search (bge-small-en-v1.5 + FAISS)
- 20+ LangChain tool calls (calendar, tasks, study planning)
- 5 domain AI agents (Planner, Rescheduler, Readiness, Wellness, Analytics)
- Voice commands, analytics dashboard, gamification

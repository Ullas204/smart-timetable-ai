# 🎓 Smart Timetable Assistant AI Agent

An AI-powered academic scheduling system that helps students manage their time efficiently by integrating with Google Calendar, detecting conflicts, and generating smart study plans.

---

## 🚀 Project Overview

Smart Timetable AI Assistant is a productivity tool designed for students to:

- 📅 Schedule academic events
- ⚠️ Detect and avoid time conflicts
- 🤖 Interact using natural language
- 📊 Track productivity
- 🧠 Generate study plans automatically

---

## ✨ Features

### 📅 Calendar Integration
- Google Calendar API (OAuth 2.0)
- Create, fetch, and manage events
- Real-time synchronization

### 🤖 AI Scheduling Agent
- Natural language input
- Example: *"Schedule study at 5 PM"*
- Powered by Gemini API

### ⚠️ Conflict Detection
- Detect overlapping events
- Suggest alternative time slots

### 📚 Academic Management
- Class scheduling
- Assignment tracking
- Study plan generation

### 🔔 Notifications
- Email alerts for scheduled events

### 📊 Dashboard
- Total events tracking
- Study hours analytics

### 📅 Calendar View
- Interactive calendar UI using Streamlit

---

## 🛠️ Tech Stack

| Component | Technology |
|----------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| AI | Google Gemini API |
| Database | SQLite |
| Calendar API | Google Calendar API |
| Notifications | SMTP (Email) |

---

## ⚙️ Setup Instructions

### 🔹 1. Clone Project

```bash
git clone https://github.com/your-username/smart-timetable-ai.git
cd smart-timetable-ai/track-a
# Smart Timetable AI

## Run Track A
cd track-a
pip install -r requirements.txt
streamlit run app.py

## Run Track B Backend
cd track-b/backend
pip install -r requirements.txt
uvicorn main:app --reload

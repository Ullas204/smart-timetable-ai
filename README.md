# 🎓 Smart Academic OS (Next-Gen Smart Timetable AI)

An **AI-powered academic productivity system** that helps students manage schedules, optimize study time, and stay consistent using intelligent automation, analytics, and gamification.

---

## 🚀 Project Overview

**Smart Academic OS** is an upgraded version of the Smart Timetable Assistant.

It combines:

* 📅 Smart Scheduling
* 🤖 AI Assistant
* 📊 Productivity Analytics
* 🎯 Focus Tracking
* 🏆 Gamification

👉 All in one unified system.

---

## ✨ Core Features

### 📅 Smart Calendar System

* Add & view events
* Real-time event tracking
* Conflict-safe scheduling
* SQLite-based persistence

---

### 🤖 AI Scheduling Assistant

* Natural language input
  *Example: “Schedule math at 5 PM”*
* Gemini API integration
* ⚡ Fallback NLP if API fails (NO BREAKAGE)

---

### ⚠️ Conflict Detection

* Detect overlapping events
* Suggest safe time slots

---

### 📚 Task & Assignment Manager

* Add tasks with deadlines
* Update status (Pending / Completed)
* Kanban-style workflow (Streamlit UI)

---

### 🚀 Focus & Pomodoro System

* Start study sessions
* Track duration + subject
* Automatic logging into database

---

### 🏆 Gamification System

* Earn XP for focus sessions
* Level system based on productivity
* Achievement tracking

---

### 📊 Analytics Dashboard

* Total study time
* Subject-wise distribution
* Recent focus sessions
* Real-time updates

---

### 🔔 Notification System

* Email alerts for events
* Safe fallback if SMTP fails

---

### 🎙️ Voice Assistant (Fallback Supported)

* Voice → Text → Action
* Works even if mic fails (manual input fallback)

---

## 🧠 AI Capabilities

* Gemini Pro Integration
* Intent parsing (schedule / query)
* Smart fallback logic (rule-based NLP)
* Context-aware responses

---

## 🏗️ System Architecture

```
Frontend (Streamlit UI)
│
├── Dashboard
├── Calendar View
├── Task Board
├── AI Assistant
├── Voice Interface
│
Backend (Python Modules)
│
├── ai_agent.py
├── scheduler_pro.py
├── analytics.py
├── gamification.py
├── notification_engine.py
├── voice_module.py
│
Database (SQLite)
│
├── events
├── tasks
├── focus_logs
├── user_profile
├── achievements
```

---

## 🗄️ Database Schema

### Events

* id, title, start, end

### Tasks

* id, title, due_date, status

### Focus Logs

* id, start_time, duration, points, subject

### User Profile

* key, value

### Achievements

* id, name, unlocked

---

## ⚙️ Tech Stack

| Layer         | Technology        |
| ------------- | ----------------- |
| Frontend      | Streamlit         |
| Backend       | Python            |
| AI            | Google Gemini API |
| Database      | SQLite            |
| Data Analysis | Pandas            |
| Notifications | SMTP              |
| Voice         | Speech / fallback |

---

## 🛠️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/Ullas204/smart-timetable-ai.git
cd smart-timetable-ai
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Set Environment Variables

Create `.env` file:

```
GEMINI_API_KEY=your_api_key_here
EMAIL_USER=your_email
EMAIL_PASS=your_password
```

---

### 4️⃣ Run Application

```bash
streamlit run app.py
```

---

## ▶️ How to Use

### 📅 Add Event

* Go to Calendar tab
* Enter title, date, time
* Click “Add Event”

---

### 🤖 Use AI Assistant

* Ask:
  *“Schedule physics at 6 PM”*
* AI will create event automatically

---

### 🧠 Start Focus Session

* Choose subject
* Set duration
* Start Pomodoro
* XP gets added automatically

---

### 📊 View Analytics

* Check dashboard
* View study patterns & progress

---

## 🧪 Test Cases

✔ Add event → appears in calendar
✔ Start focus → logs saved
✔ XP updates → level increases
✔ AI query → returns response
✔ Tasks → update correctly

---

## 🔐 Security

* API keys stored in `.env`
* No hardcoded secrets
* Safe DB operations
* Error handling everywhere

---

## 🚀 Future Enhancements

* 📱 Mobile App (React Native)
* ☁️ Cloud DB (PostgreSQL / Supabase)
* 👥 Group Study Feature
* 📄 PDF Notes + AI Tutor (RAG)
* 🔄 Multi-device sync

---

## 👨‍💻 Author

**Ullas204**

---

## ⭐ Final Note

This is a **fully functional AI-powered academic system** — not a demo.

👉 Built with production-level architecture
👉 Handles real-world failures (API, DB, UI)
👉 Designed for scalability & extensibility

---

💡 *“Plan smarter. Study better. Achieve more.”*

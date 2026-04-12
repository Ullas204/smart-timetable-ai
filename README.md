# 🎓 Smart Academic OS (Smart Timetable Assistant AI)

An **AI-powered academic operating system** that helps students manage schedules, optimize study time, track productivity, and automate academic workflows — all in one place.

---

## 🚀 Project Overview

Smart Academic OS is an upgraded version of a Smart Timetable Assistant that combines:

* 📅 Intelligent scheduling
* 🤖 AI-powered assistance
* 📊 Productivity tracking
* 🎯 Focus & gamification
* 🔗 Integration with external platforms

It acts as a **personal academic assistant** that not only schedules tasks but also helps you **study smarter**.

---

## ✨ Features

### 📅 Smart Calendar System

* View all events in an interactive calendar
* Add, update, and manage events
* Conflict detection with smart suggestions
* Google Calendar integration (sync enabled)

---

### 🤖 AI Assistant (Working)

* Natural language scheduling
  *Example: "Schedule math study at 5 PM"*
* AI-based study plan generation
* Fallback logic if API fails (ensures reliability)

---

### 🧠 Predictive Study Optimizer

* Learns your study patterns
* Suggests best time slots for productivity
* Avoids low-energy periods

---

### 📊 Analytics Dashboard

* Total study hours tracking
* Focus session insights
* Performance trends

---

### 🧩 Task Management (Kanban Board)

* Add tasks and assignments
* Track status:

  * Pending
  * In Progress
  * Completed

---

### 🎮 Gamification System

* Earn XP for focus sessions
* Track streaks
* Motivation through rewards

---

### ⏱️ Focus Tracking (Pomodoro)

* Track study sessions
* Log focus time automatically
* Improves discipline and consistency

---

### 🎤 Voice Assistant (with fallback)

* Voice → Text → Action
* Works even if microphone fails (text fallback)

---

### 🔔 Notification System

* Email alerts for events
* Smart reminders

---

### 🔗 LMS Integration (Optional)

* Fetch assignments automatically
* Supports:

  * Canvas
  * Moodle
  * Google Classroom (extendable)

---

## 🛠️ Tech Stack

| Component     | Technology          |
| ------------- | ------------------- |
| Frontend      | Streamlit           |
| Backend       | Python              |
| AI Engine     | Gemini API          |
| Database      | SQLite              |
| Calendar API  | Google Calendar API |
| Notifications | SMTP (Email)        |

---

## 📁 Project Structure

```
smart-timetable-ai/
│── track-a/
│   │── app.py
│   │── ai_agent.py
│   │── scheduler_pro.py
│   │── models.py
│   │── db.py
│   │── analytics.py
│   │── gamification.py
│   │── voice_module.py
│   │── lms_sync.py
│   │── notification_engine.py
│   │── requirements.txt
│
│── track-b/
│   │── backend/
│   │── frontend_streamlit/
│
│── .env
│── .gitignore
│── README.md
```

---

## 🧠 Database Schema (Additive)

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    due_date TEXT,
    status TEXT
);

CREATE TABLE focus_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    duration INTEGER,
    points INTEGER
);

CREATE TABLE user_profile (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    unlocked INTEGER
);
```

---

## ⚙️ Setup Instructions

### 🔹 1. Clone Repository

```bash
git clone https://github.com/Ullas204/smart-timetable-ai.git
cd smart-timetable-ai/track-a
```

---

### 🔹 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 🔹 3. Configure Environment Variables

Create a `.env` file:

```
GEMINI_API_KEY=your_api_key
EMAIL_USER=your_email
EMAIL_PASS=your_password
```

---

### 🔹 4. Run Application

```bash
streamlit run app.py
```

---

## ✅ Functional Checks

* ✔ Calendar loads with events
* ✔ AI assistant responds
* ✔ Tasks update in Kanban board
* ✔ Focus sessions are logged
* ✔ Dashboard updates dynamically

---

## ⚡ Performance Optimizations

* Caching using Streamlit
* Efficient database queries
* API fallback mechanisms

---

## 🔐 Security

* Environment variables for sensitive data
* No hardcoded API keys
* `.env` excluded via `.gitignore`

---

## 🚀 Future Enhancements

* 🌐 Multi-device sync (cloud database)
* 📱 Mobile app version
* 🧑‍🤝‍🧑 Collaborative study groups
* 📚 AI Tutor with PDF-based RAG
* 🔊 Advanced voice assistant

---

## 🤝 Contributing

Contributions are welcome!
Feel free to fork the repo and submit a pull request.

---

## 📜 License

This project is open-source and available under the MIT License.

---


---

⭐ If you like this project, give it a star!


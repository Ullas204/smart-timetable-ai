# Database Schema

## Overview

Smart Academic OS uses SQLite with 10 tables. The schema is managed by `db.py` with automatic table creation on import and column migration via `ensure_column_exists()`.

## Tables

### 1. events
```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    start_time TEXT,
    end_time TEXT
);
```

### 2. tasks
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    due_date TEXT,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending'
);
```

### 3. focus_logs
```sql
CREATE TABLE focus_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    duration INTEGER,    -- minutes
    points INTEGER,      -- XP earned
    subject TEXT
);
```

### 4. user_profile
```sql
CREATE TABLE user_profile (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

### 5. achievements
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    unlocked INTEGER DEFAULT 0,
    description TEXT DEFAULT ''
);
```

### 6. subjects
```sql
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    color TEXT,
    priority INTEGER
);
```

### 7. exams
```sql
CREATE TABLE exams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    date TEXT,
    weight REAL
);
```

### 8. attendance
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    date TEXT,
    status TEXT
);
```

### 9. notifications
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    message TEXT,
    read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 10. documents (Phase 3: RAG)
```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,        -- SHA256-based doc ID
    filename TEXT,
    file_path TEXT,
    file_type TEXT,
    file_size INTEGER,
    chunk_count INTEGER DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'indexed'
);
```

## Entity Relationships

```
events ──────────────────────┐
tasks ───────────────────────┤
focus_logs ──────────────────┤
subjects ──────┐             ├──→ gamification (XP, levels)
exams ─────────┤             │
attendance ────┤             │
user_profile ──┤             │
achievements ──┘             │
notifications ───────────────┘
documents ───→ FAISS index (separate file-based storage)
```

## CRUD Operations

| Table | Create | Read | Update | Delete |
|-------|--------|------|--------|--------|
| events | `insert_event()` | `fetch_events()` | - | - |
| tasks | `insert_task()` | `fetch_tasks()` | `update_task_status()` | - |
| focus_logs | `log_focus()` | `fetch_focus_logs()` | - | - |
| user_profile | `set_profile()` | `get_profile()` | `set_profile()` (upsert) | - |
| achievements | `unlock_achievement()` | `fetch_achievements()` | `unlock_achievement()` (upsert) | - |
| subjects | `insert_subject()` | `fetch_subjects()` | `update_subject_syllabus()` | - |
| exams | `insert_exam()` | `fetch_exams()` | - | - |
| attendance | `insert_attendance()` | `fetch_attendance()` | - | - |
| notifications | `insert_notification()` | `fetch_notifications()` | `mark_notification_read()` | - |
| documents | `insert_document()` | `fetch_documents()`, `get_document()` | `update_document_chunks()` | `delete_document()` |

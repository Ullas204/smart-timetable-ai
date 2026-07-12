"""
SQLite database layer for Smart Academic OS.

Provides CRUD operations for all 10 tables with connection pooling,
proper error handling, and structured logging.
"""

import sqlite3
import os
import logging
import threading
from contextlib import contextmanager
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "db.sqlite3")

# Thread-local storage for connection pooling
_local = threading.local()


@contextmanager
def get_connection():
    """Thread-safe context manager for SQLite connections.

    Reuses connections within the same thread and ensures proper cleanup.
    Yields a connection object; commits on success, rolls back on error.
    """
    conn = getattr(_local, "conn", None)
    owns_connection = conn is None

    if owns_connection:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn

    try:
        yield conn
        if owns_connection:
            conn.commit()
    except Exception as e:
        if owns_connection:
            conn.rollback()
        raise
    finally:
        if owns_connection:
            conn.close()
            _local.conn = None


def _execute(sql: str, params: tuple = (), fetch: str = "none") -> Any:
    """Execute a SQL statement with proper error handling.

    Parameters
    ----------
    sql : str
        SQL statement with ? placeholders.
    params : tuple
        Parameter values.
    fetch : str
        "none" for INSERT/UPDATE/DELETE, "one" for single row, "all" for all rows.

    Returns
    -------
    Any
        Query results or rowcount.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if fetch == "one":
                return cursor.fetchone()
            elif fetch == "all":
                return cursor.fetchall()
            else:
                return cursor.rowcount
    except sqlite3.Error as e:
        logger.error("DB error executing %s: %s", sql[:80], e)
        raise


# -------------------------------
# MIGRATION HELPER
# -------------------------------
def ensure_column_exists(table: str, column: str, definition: str) -> None:
    """Safely adds a column if it does not exist."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            if column not in columns:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                logger.info("Migrated: added %s.%s (%s)", table, column, definition)
    except sqlite3.Error as e:
        logger.error("Migration failed for %s.%s: %s", table, column, e)


# -------------------------------
# INPUT VALIDATION
# -------------------------------
def _validate_string(value: str, name: str, max_len: int = 500) -> str:
    """Sanitize and validate a string parameter."""
    if not isinstance(value, str):
        value = str(value)
    value = value.strip()
    if len(value) > max_len:
        logger.warning("String '%s' truncated from %d to %d chars", name, len(value), max_len)
        value = value[:max_len]
    return value


def _validate_email(email: str) -> bool:
    """Basic email format validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_email_or_none(email: str) -> Optional[str]:
    """Return email if valid, None otherwise."""
    if email and _validate_email(email):
        return email
    if email:
        logger.warning("Invalid email format: %s", email[:30])
    return None


# -------------------------------
# INITIALIZE DATABASE
# -------------------------------
def init_db() -> None:
    """Create all tables and run migrations."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            start TEXT,
            end TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            due_date TEXT,
            priority INTEGER DEFAULT 1,
            status TEXT DEFAULT 'pending'
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS focus_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profile (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            color TEXT DEFAULT '#4285F4',
            priority INTEGER DEFAULT 1,
            syllabus_completion REAL DEFAULT 0.0
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            exam_date TEXT,
            weight REAL DEFAULT 1.0,
            syllabus_covered REAL DEFAULT 0.0,
            score REAL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            date TEXT,
            status TEXT DEFAULT 'present'
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            message TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            read INTEGER DEFAULT 0
        )
        """)

        cursor.execute("""
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
        """)

    # Migrations
    ensure_column_exists("focus_logs", "duration", "INTEGER DEFAULT 0")
    ensure_column_exists("focus_logs", "points", "INTEGER DEFAULT 0")
    ensure_column_exists("focus_logs", "subject", "TEXT")
    ensure_column_exists("achievements", "unlocked", "INTEGER DEFAULT 0")
    ensure_column_exists("achievements", "description", "TEXT DEFAULT ''")
    ensure_column_exists("tasks", "priority", "INTEGER DEFAULT 1")


# -------------------------------
# EVENTS
# -------------------------------
def insert_event(title: str, start: str, end: str) -> int:
    title = _validate_string(title, "event_title", 200)
    start = _validate_string(start, "event_start", 50)
    end = _validate_string(end, "event_end", 50)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (title, start, end) VALUES (?, ?, ?)",
            (title, start, end),
        )
        return cursor.lastrowid


def fetch_events() -> List:
    return _execute("SELECT * FROM events", fetch="all")


# -------------------------------
# TASKS
# -------------------------------
def insert_task(title: str, due_date: str, status: str = "pending") -> int:
    title = _validate_string(title, "task_title", 200)
    due_date = _validate_string(due_date, "task_due_date", 50)
    if status not in ("pending", "in_progress", "completed"):
        status = "pending"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, due_date, status) VALUES (?, ?, ?)",
            (title, due_date, status),
        )
        return cursor.lastrowid


def fetch_tasks() -> List:
    return _execute("SELECT * FROM tasks", fetch="all")


def update_task_status(task_id: int, status: str) -> int:
    if status not in ("pending", "in_progress", "completed"):
        logger.warning("Invalid task status: %s", status)
        return 0
    return _execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (status, task_id),
    )


# -------------------------------
# FOCUS LOGS
# -------------------------------
def log_focus(start_time: str, duration: int, points: int, subject: str) -> None:
    subject = _validate_string(subject, "focus_subject", 100)
    _execute(
        "INSERT INTO focus_logs (start_time, duration, points, subject) VALUES (?, ?, ?, ?)",
        (start_time, int(duration), int(points), subject),
    )


def fetch_focus_logs() -> List:
    return _execute("SELECT * FROM focus_logs", fetch="all")


# -------------------------------
# USER PROFILE
# -------------------------------
def set_profile(key: str, value: str) -> None:
    key = _validate_string(key, "profile_key", 100)
    value = _validate_string(value, "profile_value", 2000)
    _execute(
        "INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)",
        (key, value),
    )


def get_profile(key: str, default: str = None) -> Optional[str]:
    row = _execute(
        "SELECT value FROM user_profile WHERE key = ?",
        (key,),
        fetch="one",
    )
    return row[0] if row else default


# -------------------------------
# ACHIEVEMENTS
# -------------------------------
def unlock_achievement(name: str, description: str = "") -> None:
    name = _validate_string(name, "achievement_name", 100)
    description = _validate_string(description, "achievement_desc", 500)
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO achievements (name, description, unlocked) VALUES (?, ?, 0)",
                (name, description),
            )
        except sqlite3.OperationalError:
            # Fallback if description column doesn't exist yet
            cursor.execute(
                "INSERT OR IGNORE INTO achievements (name) VALUES (?)",
                (name,),
            )
        cursor.execute(
            "UPDATE achievements SET unlocked = 1 WHERE name = ?",
            (name,),
        )


def fetch_achievements() -> List:
    return _execute("SELECT * FROM achievements", fetch="all")


# -------------------------------
# SUBJECTS
# -------------------------------
def insert_subject(name: str, color: str = "#4285F4", priority: int = 1) -> None:
    name = _validate_string(name, "subject_name", 100)
    _execute(
        "INSERT OR IGNORE INTO subjects (name, color, priority) VALUES (?, ?, ?)",
        (name, color, priority),
    )


def fetch_subjects() -> List:
    return _execute("SELECT * FROM subjects ORDER BY priority", fetch="all")


def get_subject_names() -> List[str]:
    """Return a list of all subject names (dynamic, no hardcoded defaults)."""
    rows = _execute("SELECT name FROM subjects ORDER BY priority", fetch="all")
    return [row[0] for row in rows] if rows else []


def update_subject_syllabus(name: str, completion: float) -> None:
    _execute(
        "UPDATE subjects SET syllabus_completion = ? WHERE name = ?",
        (completion, name),
    )


# -------------------------------
# EXAMS
# -------------------------------
def insert_exam(subject: str, exam_date: str, weight: float = 1.0) -> None:
    subject = _validate_string(subject, "exam_subject", 100)
    exam_date = _validate_string(exam_date, "exam_date", 50)
    _execute(
        "INSERT INTO exams (subject, exam_date, weight) VALUES (?, ?, ?)",
        (subject, exam_date, weight),
    )


def fetch_exams() -> List:
    return _execute("SELECT * FROM exams ORDER BY exam_date", fetch="all")


# -------------------------------
# ATTENDANCE
# -------------------------------
def insert_attendance(subject: str, date: str, status: str = "present") -> None:
    subject = _validate_string(subject, "attendance_subject", 100)
    date = _validate_string(date, "attendance_date", 50)
    if status not in ("present", "absent", "late"):
        status = "present"
    _execute(
        "INSERT INTO attendance (subject, date, status) VALUES (?, ?, ?)",
        (subject, date, status),
    )


def fetch_attendance(subject: Optional[str] = None) -> List:
    if subject:
        return _execute(
            "SELECT * FROM attendance WHERE subject = ? ORDER BY date",
            (subject,),
            fetch="all",
        )
    return _execute("SELECT * FROM attendance ORDER BY date", fetch="all")


# -------------------------------
# NOTIFICATIONS
# -------------------------------
def insert_notification(type_: str, message: str) -> None:
    type_ = _validate_string(type_, "notif_type", 50)
    message = _validate_string(message, "notif_message", 2000)
    _execute(
        "INSERT INTO notifications (type, message) VALUES (?, ?)",
        (type_, message),
    )


def fetch_notifications(unread_only: bool = False) -> List:
    if unread_only:
        return _execute(
            "SELECT * FROM notifications WHERE read = 0 ORDER BY created_at DESC",
            fetch="all",
        )
    return _execute(
        "SELECT * FROM notifications ORDER BY created_at DESC LIMIT 50",
        fetch="all",
    )


def mark_notification_read(note_id: int) -> None:
    _execute("UPDATE notifications SET read = 1 WHERE id = ?", (note_id,))


# -------------------------------
# DOCUMENTS (Phase 3: RAG)
# -------------------------------
def insert_document(doc_id: str, filename: str, file_path: str,
                    file_type: str, file_size: int, chunk_count: int = 0) -> None:
    filename = _validate_string(filename, "doc_filename", 200)
    _execute(
        "INSERT OR REPLACE INTO documents (id, filename, file_path, file_type, file_size, chunk_count) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (doc_id, filename, file_path, file_type, int(file_size), int(chunk_count)),
    )


def fetch_documents() -> List:
    return _execute("SELECT * FROM documents ORDER BY uploaded_at DESC", fetch="all")


def get_document(doc_id: str):
    return _execute(
        "SELECT * FROM documents WHERE id = ?",
        (doc_id,),
        fetch="one",
    )


def delete_document(doc_id: str) -> bool:
    return _execute("DELETE FROM documents WHERE id = ?", (doc_id,)) > 0


def update_document_chunks(doc_id: str, chunk_count: int) -> None:
    _execute(
        "UPDATE documents SET chunk_count = ? WHERE id = ?",
        (int(chunk_count), doc_id),
    )


# -------------------------------
# INIT ON START
# -------------------------------
init_db()

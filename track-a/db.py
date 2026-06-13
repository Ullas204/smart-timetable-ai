import sqlite3
import os

DB_PATH = "db.sqlite3"


# -------------------------------
# DB CONNECTION
# -------------------------------
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


# -------------------------------
# MIGRATION HELPER
# -------------------------------
def ensure_column_exists(table, column, definition):
    """
    Safely adds a column if it does not exist
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]

        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            print(f"[OK] Added column: {table}.{column}")

        conn.commit()

    except Exception as e:
        print(f"[ERROR] Migration error ({table}.{column}):", e)

    finally:
        conn.close()


# -------------------------------
# INITIALIZE DATABASE
# -------------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # EVENTS TABLE (Calendar)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        start TEXT,
        end TEXT
    )
    """)

    # TASKS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        due_date TEXT,
        priority INTEGER DEFAULT 1,
        status TEXT DEFAULT 'pending'
    )
    """)

    # FOCUS LOGS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS focus_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT
    )
    """)

    # USER PROFILE TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # ACHIEVEMENTS TABLE (BASE SAFE VERSION)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    # SUBJECTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        color TEXT DEFAULT '#4285F4',
        priority INTEGER DEFAULT 1,
        syllabus_completion REAL DEFAULT 0.0
    )
    """)

    # EXAMS TABLE
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

    # ATTENDANCE TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        date TEXT,
        status TEXT DEFAULT 'present'
    )
    """)

    # NOTIFICATIONS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        message TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        read INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

    # -------------------------------
    # SAFE MIGRATIONS (CRITICAL)
    # -------------------------------
    ensure_column_exists("focus_logs", "duration", "INTEGER DEFAULT 0")
    ensure_column_exists("focus_logs", "points", "INTEGER DEFAULT 0")
    ensure_column_exists("focus_logs", "subject", "TEXT")

    ensure_column_exists("achievements", "unlocked", "INTEGER DEFAULT 0")
    ensure_column_exists("achievements", "description", "TEXT DEFAULT ''")

    ensure_column_exists("tasks", "priority", "INTEGER DEFAULT 1")


# -------------------------------
# EVENTS
# -------------------------------
def insert_event(title, start, end):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (title, start, end) VALUES (?, ?, ?)",
        (title, start, end)
    )
    conn.commit()
    conn.close()


def fetch_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    conn.close()
    return rows


# -------------------------------
# TASKS
# -------------------------------
def insert_task(title, due_date, status='pending'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, due_date, status) VALUES (?, ?, ?)",
        (title, due_date, status)
    )
    conn.commit()
    conn.close()


def fetch_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_task_status(task_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        (status, task_id)
    )
    conn.commit()
    conn.close()


# -------------------------------
# FOCUS LOGS
# -------------------------------
def log_focus(start_time, duration, points, subject):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO focus_logs (start_time, duration, points, subject)
            VALUES (?, ?, ?, ?)
        """, (start_time, int(duration), int(points), str(subject)))
    except Exception as e:
        print("Error logging focus:", e)

    conn.commit()
    conn.close()


def fetch_focus_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM focus_logs")
    rows = cursor.fetchall()
    conn.close()
    return rows


# -------------------------------
# USER PROFILE
# -------------------------------
def set_profile(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()
    conn.close()


def get_profile(key, default=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default


# -------------------------------
# ACHIEVEMENTS
# -------------------------------
def unlock_achievement(name):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO achievements (name, unlocked) VALUES (?, 0)",
            (name,)
        )
    except:
        cursor.execute(
            "INSERT OR IGNORE INTO achievements (name) VALUES (?)",
            (name,)
        )

    try:
        cursor.execute(
            "UPDATE achievements SET unlocked = 1 WHERE name = ?",
            (name,)
        )
    except:
        pass

    conn.commit()
    conn.close()


def fetch_achievements():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM achievements")
    rows = cursor.fetchall()
    conn.close()
    return rows


# -------------------------------
# SUBJECTS
# -------------------------------
def insert_subject(name, color="#4285F4", priority=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO subjects (name, color, priority) VALUES (?, ?, ?)",
        (name, color, priority)
    )
    conn.commit()
    conn.close()

def fetch_subjects():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM subjects ORDER BY priority")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_subject_syllabus(name, completion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE subjects SET syllabus_completion = ? WHERE name = ?",
        (completion, name)
    )
    conn.commit()
    conn.close()

# -------------------------------
# EXAMS
# -------------------------------
def insert_exam(subject, exam_date, weight=1.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO exams (subject, exam_date, weight) VALUES (?, ?, ?)",
        (subject, exam_date, weight)
    )
    conn.commit()
    conn.close()

def fetch_exams():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exams ORDER BY exam_date")
    rows = cursor.fetchall()
    conn.close()
    return rows

# -------------------------------
# ATTENDANCE
# -------------------------------
def insert_attendance(subject, date, status="present"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (subject, date, status) VALUES (?, ?, ?)",
        (subject, date, status)
    )
    conn.commit()
    conn.close()

def fetch_attendance(subject=None):
    conn = get_connection()
    cursor = conn.cursor()
    if subject:
        cursor.execute("SELECT * FROM attendance WHERE subject = ? ORDER BY date", (subject,))
    else:
        cursor.execute("SELECT * FROM attendance ORDER BY date")
    rows = cursor.fetchall()
    conn.close()
    return rows

# -------------------------------
# NOTIFICATIONS
# -------------------------------
def insert_notification(type_, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notifications (type, message) VALUES (?, ?)",
        (type_, message)
    )
    conn.commit()
    conn.close()

def fetch_notifications(unread_only=False):
    conn = get_connection()
    cursor = conn.cursor()
    if unread_only:
        cursor.execute("SELECT * FROM notifications WHERE read = 0 ORDER BY created_at DESC")
    else:
        cursor.execute("SELECT * FROM notifications ORDER BY created_at DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_notification_read(note_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET read = 1 WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

# -------------------------------
# INIT ON START
# -------------------------------
init_db()

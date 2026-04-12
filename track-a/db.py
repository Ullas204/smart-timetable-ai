import sqlite3
import os

DB_PATH = "db.sqlite3"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Events Table (Existing compatibility)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        start TEXT,
        end TEXT
    )
    """)

    # 2. Tasks Table (As requested: title, due_date, status)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        due_date TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    # 3. Focus Logs Table (As requested: start_time, duration, points)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS focus_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT,
        duration INTEGER,
        points INTEGER,
        subject TEXT
    )
    """)

    # 4. User Profile Table (As requested: key, value)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # 5. Achievements Table (As requested: name, unlocked)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        unlocked INTEGER DEFAULT 0,
        description TEXT
    )
    """)
    
    conn.commit()
    conn.close()

# --- HELPER FUNCTIONS ---

def insert_event(title, start, end):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (title, start, end) VALUES (?, ?, ?)", (title, start, end))
    conn.commit()
    conn.close()

def fetch_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_task(title, due_date, status='pending'):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, due_date, status) VALUES (?, ?, ?)", (title, due_date, status))
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
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()

def log_focus(start_time, duration, points, subject):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO focus_logs (start_time, duration, points, subject) VALUES (?, ?, ?, ?)", 
                   (start_time, duration, points, subject))
    conn.commit()
    conn.close()

def fetch_focus_logs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM focus_logs")
    rows = cursor.fetchall()
    conn.close()
    return rows

def set_profile(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_profile(key, default=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def unlock_achievement(name, description=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO achievements (name, unlocked, description) VALUES (?, 1, ?)", (name, description))
    cursor.execute("UPDATE achievements SET unlocked = 1 WHERE name = ?", (name,))
    conn.commit()
    conn.close()

def fetch_achievements():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM achievements")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Initialize on import
init_db()

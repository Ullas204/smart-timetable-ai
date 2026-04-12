import sqlite3

conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
cursor = conn.cursor()

# Existing table
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    start TEXT,
    end TEXT
)
""")

# New: Tasks for Kanban
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    due_date TEXT,
    priority INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending'
)
""")

# New: Focus Tracking for Pomodoro
cursor.execute("""
CREATE TABLE IF NOT EXISTS focus_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    duration_minutes INTEGER,
    subject TEXT,
    points_earned INTEGER
)
""")

# New: User Profile for Settings
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_profile (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

# New: Achievements for Gamification
cursor.execute("""
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    unlocked_at TEXT
)
""")

conn.commit()


# Existing functions
def insert_event(title, start, end):
    cursor.execute(
        "INSERT INTO events (title, start, end) VALUES (?, ?, ?)",
        (title, start, end)
    )
    conn.commit()


def fetch_events():
    cursor.execute("SELECT * FROM events")
    return cursor.fetchall()


# New: Task functions
def insert_task(title, due_date, priority=1):
    cursor.execute(
        "INSERT INTO tasks (title, due_date, priority) VALUES (?, ?, ?)",
        (title, due_date, priority)
    )
    conn.commit()


def fetch_tasks():
    cursor.execute("SELECT * FROM tasks")
    return cursor.fetchall()


def update_task_status(task_id, status):
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()


# New: Focus log functions
def log_focus_session(duration, subject, points):
    import datetime
    start_time = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO focus_logs (start_time, duration_minutes, subject, points_earned) VALUES (?, ?, ?, ?)",
        (start_time, duration, subject, points)
    )
    conn.commit()


def fetch_focus_logs():
    cursor.execute("SELECT * FROM focus_logs")
    return cursor.fetchall()


# New: Profile functions
def get_profile_value(key, default=None):
    cursor.execute("SELECT value FROM user_profile WHERE key = ?", (key,))
    row = cursor.fetchone()
    return row[0] if row else default


def set_profile_value(key, value):
    cursor.execute(
        "INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)",
        (key, value)
    )
    conn.commit()


# New: Achievement functions
def unlock_achievement(name, description):
    import datetime
    unlocked_at = datetime.datetime.now().isoformat()
    cursor.execute(
        "INSERT INTO achievements (name, description, unlocked_at) VALUES (?, ?, ?)",
        (name, description, unlocked_at)
    )
    conn.commit()


def fetch_achievements():
    cursor.execute("SELECT * FROM achievements")
    return cursor.fetchall()

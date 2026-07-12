from db import (
    insert_event, fetch_events, insert_task, fetch_tasks, update_task_status,
    log_focus, fetch_focus_logs, set_profile, get_profile,
    unlock_achievement as db_unlock_achievement, fetch_achievements,
    insert_subject, fetch_subjects, update_subject_syllabus,
    insert_exam, fetch_exams,
    insert_attendance, fetch_attendance,
    insert_notification, fetch_notifications, mark_notification_read,
    insert_document, fetch_documents, get_document, delete_document, update_document_chunks,
)
import datetime

def log_focus_session(duration, subject, points):
    start_time = datetime.datetime.now().isoformat()
    log_focus(start_time, duration, points, subject)
    try:
        from gamification import invalidate_xp_cache
        invalidate_xp_cache()
    except ImportError:
        pass

def unlock_achievement(name, description=""):
    db_unlock_achievement(name, description)

def get_profile_value(key, default=None):
    return get_profile(key, default)

def set_profile_value(key, value):
    set_profile(key, value)

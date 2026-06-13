"""
Tests for Smart Academic OS.
Run with: python -m pytest tests.py -v
"""
import os
import sys
import datetime
import tempfile

os.environ["GEMINI_API_KEY"] = "test-key"
os.environ["EMAIL"] = "test@test.com"
os.environ["EMAIL_PASSWORD"] = "test-pass"

sys.path.insert(0, os.path.dirname(__file__))

# Override DB to use temp file for tests
import db
db.DB_PATH = os.path.join(tempfile.gettempdir(), "test_smart_os.db")
db.init_db()

from agents import planner_agent, rescheduler_agent, readiness_agent, wellness_agent, analytics_agent
from models import (
    insert_task, fetch_tasks, update_task_status,
    insert_event, fetch_events,
    log_focus_session, fetch_focus_logs,
    insert_subject, fetch_subjects, update_subject_syllabus,
    insert_exam, fetch_exams,
    insert_notification, fetch_notifications,
    get_profile_value, set_profile_value,
    fetch_achievements, unlock_achievement,
)
import gamification


def test_task_crud():
    insert_task("Test Task", "2026-12-31")
    tasks = fetch_tasks()
    assert len(tasks) >= 1
    task = tasks[-1]
    assert task[1] == "Test Task"
    assert task[3] == "pending" or task[3] is None

    update_task_status(task[0], "completed")
    updated = fetch_tasks()
    match = [t for t in updated if t[0] == task[0]]
    assert match
    assert match[0][3] == "completed"


def test_event_crud():
    insert_event("Test Event", "2026-12-31T09:00", "2026-12-31T10:00")
    events = fetch_events()
    assert len(events) >= 1
    assert events[-1][1] == "Test Event"


def test_focus_log_and_xp():
    log_focus_session(30, "Math", 60)
    logs = fetch_focus_logs()
    assert len(logs) >= 1
    xp = gamification.calculate_xp()
    assert xp >= 60
    level = gamification.get_user_level()
    assert level >= 1
    progress = gamification.get_progress_to_next_level()
    assert 0.0 <= progress <= 1.0


def test_profile():
    set_profile_value("test_key", "test_value")
    val = get_profile_value("test_key")
    assert val == "test_value"
    val2 = get_profile_value("nonexistent", "default")
    assert val2 == "default"


def test_achievements():
    unlock_achievement("Test Achievement")
    achievements = fetch_achievements()
    names = [a[1] for a in achievements]
    assert "Test Achievement" in names


def test_subjects():
    insert_subject("Math", "#FF0000", 1)
    insert_subject("Physics", "#00FF00", 2)
    subjects = fetch_subjects()
    names = [s[1] for s in subjects]
    assert "Math" in names
    assert "Physics" in names


def test_exams():
    insert_exam("Math", "2026-12-31", 1.0)
    exams = fetch_exams()
    assert len(exams) >= 1
    assert exams[-1][1] == "Math"


def test_notifications():
    insert_notification("test", "Test notification message")
    notes = fetch_notifications()
    assert len(notes) >= 1
    assert notes[-1][1] == "test"


def test_gamification():
    xp = gamification.calculate_xp()
    assert isinstance(xp, int)
    level = gamification.get_user_level()
    assert isinstance(level, int) and level >= 1
    assert gamification.get_achievements() is not None


def test_agent_readiness():
    log_focus_session(60, "Math", 120)
    score = readiness_agent.get_readiness_score("Math")
    assert 0 <= score <= 100
    summary = readiness_agent.get_readiness_summary()
    assert "avg_score" in summary
    assert 0 <= summary["avg_score"] <= 100


def test_agent_wellness():
    status = wellness_agent.get_wellness_status()
    assert "energy_level" in status
    assert 0 <= status["energy_level"] <= 100
    assert "today_minutes" in status
    assert "recommendation" in status
    trend = wellness_agent.get_weekly_trend()
    assert isinstance(trend, list)


def test_agent_analytics():
    report = analytics_agent.generate_report()
    assert "streak" in report
    assert "completion_rate" in report
    assert "recommendations" in report
    rate = analytics_agent.get_completion_rate()
    assert 0 <= rate <= 100
    streak = analytics_agent.get_study_streak()
    assert isinstance(streak, int)


def test_agent_planner():
    plan = planner_agent.generate_plan(
        subjects=["Math", "Physics"],
        hours_per_day=4,
        priority_subject="Math"
    )
    assert "Optimized Study Plan" in plan
    assert "Math" in plan
    assert "Physics" in plan


def test_agent_rescheduler():
    missed = rescheduler_agent.detect_missed_sessions()
    assert isinstance(missed, list)


def cleanup():
    try:
        os.remove(db.DB_PATH)
    except:
        pass


if __name__ == "__main__":
    test_task_crud()
    test_event_crud()
    test_focus_log_and_xp()
    test_profile()
    test_achievements()
    test_subjects()
    test_exams()
    test_notifications()
    test_gamification()
    test_agent_readiness()
    test_agent_wellness()
    test_agent_analytics()
    test_agent_planner()
    test_agent_rescheduler()
    print("✅ All tests passed!")
    cleanup()

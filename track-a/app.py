import sys
import os
_vendor = os.path.join(os.path.dirname(__file__), "vendor")
if os.path.isdir(_vendor) and _vendor not in sys.path:
    sys.path.insert(0, _vendor)

import streamlit as st
import datetime
import pandas as pd
import time
import json
import logging
import db

from core.logging_config import setup_logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))

from ai_agent import process_query
from models import (
    insert_event, fetch_events, insert_task, fetch_tasks, update_task_status,
    log_focus_session, fetch_focus_logs, get_profile_value, set_profile_value,
    fetch_achievements, unlock_achievement, fetch_notifications,
    fetch_documents, delete_document, get_document, insert_document
)
from streamlit_calendar import calendar
from study_planner import generate_study_plan
from google_calendar import (
    create_event as g_create_event,
    get_events as g_get_events,
    check_conflict
)
from email_utils import send_email
from notification_engine import notify_event_creation

import analytics
import gamification
import scheduler_pro
import lms_sync
import voice_module
import calendar_utils
import notification_engine as notify
from agents import (
    planner_agent, rescheduler_agent, readiness_agent,
    wellness_agent, analytics_agent
)

# LangChain Agentic AI Core (Phase 1 + Phase 2: Tool Binding)
try:
    from core.agent_executor import AcademicAgent
    from core.memory import ChatMemory
    from core.tools import get_tool_execution_log, clear_tool_execution_log
    from langchain_core.messages import HumanMessage, AIMessage
    _has_langchain_agent = True
except ImportError:
    _has_langchain_agent = False

# Phase 3: RAG / Knowledge Base
try:
    from core.rag import get_rag_pipeline
    from core.rag.document_processor import DocumentProcessor
    _has_rag = True
except ImportError:
    _has_rag = False

st.set_page_config(page_title="Smart Academic OS", page_icon="\U0001f393", layout="wide")

CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa, #e4e9f2);
    }

    html, body, .stApp, p, span, div, label, .stMarkdown, .stText {
        color: #2d3748 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif !important;
    }

    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }

    h1, h2, h3, h4, h5, h6, .st-emotion-cache-1inwz65, .st-emotion-cache-1mi2ry5 {
        font-weight: 700 !important;
        color: #1a202c !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif !important;
        letter-spacing: -0.02em;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.7);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 6px;
        border: 1px solid rgba(0,0,0,0.06);
        margin-bottom: 1.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 8px 18px;
        font-weight: 500;
        font-size: 0.85rem;
        color: #718096 !important;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    }

    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background: rgba(0,0,0,0.04);
        color: #2d3748 !important;
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 8px 24px;
        border: none;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(102,126,234,0.25);
        transition: all 0.3s ease;
        letter-spacing: 0.3px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102,126,234,0.4);
    }

    div.stButton > button:active {
        transform: translateY(0);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
        border-radius: 10px;
    }

    .stProgress > div > div {
        background: rgba(0,0,0,0.06) !important;
        border-radius: 10px;
        overflow: hidden;
        height: 12px !important;
    }

    div.stMetric {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 16px;
        padding: 16px !important;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    div.stMetric:hover {
        transform: translateY(-3px);
        border-color: rgba(102,126,234,0.3);
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    }

    div.stMetric label {
        color: #718096 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div.stMetric [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #1a202c !important;
    }

    .stExpander {
        background: rgba(255,255,255,0.85) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0,0,0,0.06) !important;
        border-radius: 14px !important;
        margin-bottom: 8px;
        transition: all 0.3s ease;
    }

    .stExpander:hover {
        border-color: rgba(102,126,234,0.3) !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }

    .stExpander summary {
        font-weight: 600 !important;
        color: #2d3748 !important;
        padding: 10px 16px !important;
        display: flex !important;
        align-items: center;
        gap: 8px;
    }

    .stExpander summary::-webkit-details-marker {
        display: none !important;
    }

    .stExpander summary::before {
        content: "\u25b6" !important;
        font-size: 0.7rem;
        color: #667eea;
        transition: transform 0.2s ease;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    .stExpander[open] summary::before {
        transform: rotate(90deg);
    }

    .stExpander [data-testid="stExpanderContent"] {
        padding: 0 16px 12px !important;
    }

    div.stAlert {
        border-radius: 14px;
        border: none !important;
        background: rgba(255,255,255,0.8) !important;
        backdrop-filter: blur(10px);
        border-left: 4px solid !important;
    }

    div[data-testid="stAlert"] > div:first-child {
        color: #2d3748 !important;
    }

    .stInfo { border-left-color: #4299E1 !important; }
    .stWarning { border-left-color: #ED8936 !important; }
    .stSuccess { border-left-color: #48BB78 !important; }
    .stError { border-left-color: #F56565 !important; }

    div[data-testid="stSidebar"] {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(0,0,0,0.06);
    }

    div[data-testid="stSidebarUserContent"] {
        padding: 1.5rem 1rem;
    }

    div[data-testid="stTextInputRootElement"] {
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        background: rgba(255,255,255,0.8) !important;
        transition: all 0.3s ease;
    }

    div[data-testid="stTextInputRootElement"]:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }

    div[data-testid="stTextInputRootElement"] input {
        color: #2d3748 !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        background: rgba(255,255,255,0.8) !important;
        color: #2d3748 !important;
    }

    .stSlider [data-baseweb="slider"] {
        margin-top: 8px;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    .element-container iframe {
        border-radius: 14px !important;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .glow-card {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 20px;
        padding: 24px;
        transition: all 0.4s ease;
        height: 100%;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }

    .glow-card:hover {
        transform: translateY(-5px);
        border-color: rgba(102,126,234,0.3);
        box-shadow: 0 12px 40px rgba(0,0,0,0.08);
    }

    .glow-card h3 {
        margin-top: 0;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(0,0,0,0.06);
        color: #1a202c !important;
    }

    hr {
        border-color: rgba(0,0,0,0.06) !important;
        margin: 1.5rem 0 !important;
    }

    textarea, input, select, div[role="combobox"] {
        color: #2d3748 !important;
    }

    .st-bd, .st-bf, .st-bg, .st-cf, .st-dj, .st-cn, .st-dc {
        border-color: rgba(0,0,0,0.06) !important;
    }

    .stNumberInput input {
        color: #2d3748 !important;
    }

    div[data-testid="stNumberInput"] input {
        color: #2d3748 !important;
    }

    .stDateInput div[data-baseweb="input"] input {
        color: #2d3748 !important;
    }

    .stTimeInput div[data-baseweb="input"] input {
        color: #2d3748 !important;
    }

    .stSlider div[data-testid="stThumbValue"] {
        color: #2d3748 !important;
    }

    .stSlider div[data-baseweb="slider"] div[role="slider"] {
        background-color: #667eea !important;
    }

    p, li, .stMarkdown p {
        color: #4a5568 !important;
        line-height: 1.6;
    }

    strong {
        color: #1a202c !important;
    }

    span[data-testid="stMetricValue"] {
        color: #1a202c !important;
    }

    div[data-testid="stNotificationContent"] {
        color: #2d3748 !important;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Pomodoro session state
if "pomo" not in st.session_state:
    st.session_state.pomo = {
        "running": False, "done": False, "paused": False,
        "end": None, "subject": "Math", "duration": 25,
    }

# Initialize LangChain Agent Memory (Phase 1)
if _has_langchain_agent:
    if "chat_memory" not in st.session_state:
        st.session_state.chat_memory = ChatMemory()



# ===============================
# SIDEBAR
# ===============================
st.sidebar.markdown('<div style="text-align:center; padding: 0.5rem 0;">'
                    '<h1 style="font-size:1.5rem;">\U0001f680 Smart Academic OS</h1>'
                    '<p style="color:#a0aec0; font-size:0.75rem; margin-top:-8px;">'
                    'AI-Powered Learning Platform</p></div>',
                    unsafe_allow_html=True)
st.sidebar.divider()

user_name = get_profile_value("user_name", "Student")
st.sidebar.markdown(f'<div style="text-align:center; margin-bottom:1rem;">'
                    f'<span style="font-size:2.5rem;">\U0001f44b</span>'
                    f'<p style="font-size:1.1rem; font-weight:600; margin-top:4px;">Hello, {user_name}!</p></div>',
                    unsafe_allow_html=True)

level = gamification.get_user_level()
xp = gamification.calculate_xp()
progress = gamification.get_progress_to_next_level()

st.sidebar.markdown('<div class="glow-card">', unsafe_allow_html=True)
st.sidebar.metric("Current Level", f"Lvl {level}")
st.sidebar.metric("Total XP", f"{xp:,} pts")
st.sidebar.progress(progress, text=f"Next Level: {int(progress*100)}%")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

st.sidebar.divider()

unread = fetch_notifications(unread_only=True)
if unread:
    st.sidebar.markdown(
        f'<div style="background:#FED7D7; border:1px solid #FEB2B2; border-radius:12px; '
        f'padding:8px 12px; margin-bottom:12px; display:flex; align-items:center; gap:8px;">'
        f'<span style="font-size:1.1rem;">\U0001f514</span>'
        f'<span style="font-size:0.85rem; font-weight:600; color:#C53030;">'
        f'{len(unread)} unread notification(s)</span></div>',
        unsafe_allow_html=True)

st.sidebar.markdown('<p style="font-weight:600; font-size:0.9rem;">\U0001f3af Quick Actions</p>',
                    unsafe_allow_html=True)
if st.sidebar.button("Sync LMS Assignments", width="stretch"):
    with st.spinner("Syncing with LMS..."):
        try:
            new_count = lms_sync.sync_assignments_to_db()
            st.sidebar.success(f"Fetched {new_count} new tasks!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"LMS Sync Failed: {e}")

# ===============================
# MAIN TABS
# ===============================
tabs = st.tabs([
    "\U0001f3e0 Dashboard", "\U0001f4c5 Calendar", "\U0001f4cb Tasks", "\U0001f4ca Analytics",
    "\U0001f916 AI Agents", "\U0001f399\ufe0f Voice", "\U0001f9e0 AI Assistant",
    "\U0001f4da Knowledge Base", "\u2699\ufe0f Settings"
])
tab_dash, tab_cal, tab_tasks, tab_stats, tab_agents, tab_voice, tab_ai, tab_kb, tab_settings = tabs

# ===============================
# DASHBOARD
# ===============================
with tab_dash:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">\U0001f5d3\ufe0f Upcoming Events</p>', unsafe_allow_html=True)
        try:
            g_events = g_get_events()
            if g_events:
                for e in g_events[:5]:
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    st.markdown(
                        f'<div style="display:flex; align-items:center; gap:12px; '
                        f'padding:8px 12px; margin-bottom:4px; border-radius:10px; '
                        f'background:#f7fafc; border:1px solid #e2e8f0;">'
                        f'<span style="font-size:1.2rem;">\U0001f4cc</span>'
                        f'<div><strong style="color:#2d3748;">{e.get("summary")}</strong><br>'
                        f'<span style="font-size:0.8rem; color:#718096;">{start}</span></div>'
                        f'</div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color:#a0aec0;">No upcoming Google events.</p>',
                            unsafe_allow_html=True)
        except Exception as _gc_err:
            logging.getLogger(__name__).debug("Google Calendar unavailable: %s", _gc_err)
            st.markdown('<p style="color:#a0aec0;">Google Calendar unavailable.</p>',
                        unsafe_allow_html=True)
            local_events = fetch_events()
            if local_events:
                for e in local_events[-5:]:
                    st.markdown(
                        f'<div style="display:flex; align-items:center; gap:12px; padding:8px 12px; '
                        f'margin-bottom:4px; border-radius:10px; background:#f7fafc; border:1px solid #e2e8f0;">'
                        f'<span style="font-size:1.2rem;">\U0001f4cc</span>'
                        f'<div><strong style="color:#2d3748;">{e[1]}</strong><br>'
                        f'<span style="font-size:0.8rem; color:#718096;">{e[2]}</span></div>'
                        f'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">\U0001f525 Daily Focus Goal</p>', unsafe_allow_html=True)
        stats = analytics.get_study_stats()
        today_mins = stats['total_focus_time']
        daily_goal = 300
        pct = min(1.0, today_mins / daily_goal)
        st.progress(pct, text=f"{today_mins}m / {daily_goal}m Focused")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">\U0001f916 AI Agent Insights</p>', unsafe_allow_html=True)
        ai_col1, ai_col2, ai_col3 = st.columns(3)
        readiness = readiness_agent.get_readiness_summary()
        wellness = wellness_agent.get_wellness_status()
        ai_col1.metric("\U0001f4da Readiness", f"{readiness['avg_score']:.0f}%")
        ai_col2.metric("\u26a1 Energy Level", f"{wellness['energy_level']:.0f}%")
        ai_col3.metric("\U0001f4ca Tasks Done", f"{analytics_agent.get_completion_rate():.0f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">\U0001f680 Pomodoro Timer</p>', unsafe_allow_html=True)

        pomo = st.session_state.pomo
        if not pomo["running"]:
            _pomo_subjects = db.get_subject_names() or ["Math", "Physics", "Computer Science", "History"]
            _pomo_subjects.append("Other")
            subj = st.selectbox("Subject", _pomo_subjects, key="pomo_subj")
            dur = st.number_input("Minutes", 1, 120, 25, key="pomo_dur")
            if st.button("\u25b6\ufe0f Start Focus Session", width="stretch", key="pomo_start"):
                st.session_state.pomo = {
                    "running": True, "done": False, "paused": False,
                    "end": datetime.datetime.now() + datetime.timedelta(minutes=dur),
                    "subject": subj, "duration": dur,
                }
                st.rerun()
        else:
            end = pomo["end"]
            now = datetime.datetime.now()
            remaining = (end - now).total_seconds()

            if remaining <= 0 and not pomo["done"]:
                st.session_state.pomo["done"] = True
                subj = pomo["subject"]
                dur = pomo["duration"]
                points = dur * 2
                log_focus_session(dur, subj, points)
                unlock_achievement("Deep Work Initiate", "Completed a focus session")
                st.balloons()
                st.success(f"\U0001f389 Session complete! {dur} mins logged, +{points} XP")
                st.session_state.pomo["running"] = False

            elif pomo["running"]:
                mins, secs = divmod(max(0, int(remaining)), 60)
                pct = max(0, min(1.0, 1.0 - remaining / (pomo["duration"] * 60)))

                st.markdown(
                    f'<div style="text-align:center;padding:8px 0;">'
                    f'<div style="font-size:2.8rem;font-weight:800;color:#667eea;'
                    f'letter-spacing:2px;">{mins:02d}:{secs:02d}</div>'
                    f'</div>', unsafe_allow_html=True)
                st.progress(pct, text=f"Focusing on {pomo['subject']}")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("\u23f9\ufe0f Stop", width="stretch", key="pomo_stop"):
                        st.session_state.pomo["running"] = False
                        st.rerun()
                with c2:
                    if st.button("\U0001f504 Reset", width="stretch", key="pomo_reset"):
                        st.session_state.pomo["running"] = False
                        st.rerun()

                if pomo["running"] and remaining > 0:
                    time.sleep(1)
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">\U0001f525 Productivity Summary</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:2rem; font-weight:800; text-align:center; margin:8px 0; color:#2d3748;">'
            f'{today_mins}<span style="font-size:1rem; font-weight:400; '
            f'color:#a0aec0;"> mins</span></p>',
            unsafe_allow_html=True)
        st.progress(pct, text="Daily Goal Progress")
        st.markdown('</div>', unsafe_allow_html=True)

        if stats.get('subject_distribution'):
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">\U0001f4ca Subject Breakdown</p>', unsafe_allow_html=True)
            df_dist = pd.DataFrame(
                list(stats['subject_distribution'].items()),
                columns=["Subject", "Minutes"]
            )
            st.bar_chart(df_dist.set_index("Subject"), color="#f5af19")
            st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# CALENDAR
# ===============================
with tab_cal:
    st.markdown('<div class="glow-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">\U0001f4c5 Smart Calendar</p>', unsafe_allow_html=True)
    calendar_events = []

    try:
        g_events = g_get_events()
        for e in g_events:
            calendar_events.append({
                "title": f"\u2601\ufe0f {e.get('summary', 'No Title')}",
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end": e["end"].get("dateTime", e["end"].get("date")),
                "color": "#4285F4"
            })
    except Exception as _gc_err:
        logging.getLogger(__name__).debug("GC event load failed: %s", _gc_err)

    try:
        db_events = fetch_events()
        for e in db_events:
            calendar_events.append({
                "title": f"\U0001f4cc {e[1]}",
                "start": e[2],
                "end": e[3],
                "color": "#34A853"
            })
    except Exception as e:
        st.error(f"Error loading local events: {e}")

    try:
        if calendar_events:
            calendar(events=calendar_events)
        else:
            st.markdown('<p style="color:#a0aec0; text-align:center; padding:2rem;">'
                        'No events to display.</p>', unsafe_allow_html=True)
    except Exception as e:
        st.warning("Calendar render failed. Using list view.")
        if calendar_events:
            st.dataframe(pd.DataFrame(calendar_events)[["title", "start", "end"]],
                        width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    with st.expander("\u2795 Add Event Manually"):
        with st.form("add_event"):
            e_title = st.text_input("Event Title")
            col_a, col_b = st.columns(2)
            e_date = col_a.date_input("Date", value=datetime.date.today())
            e_start_t = col_a.time_input("Start Time", value=datetime.time(9, 0))
            e_end_t = col_b.time_input("End Time", value=datetime.time(10, 0))
            send_notify = st.checkbox("Send email notification", value=False)
            if st.form_submit_button("Save Event", width="stretch"):
                if e_title:
                    try:
                        start_dt = datetime.datetime.combine(e_date, e_start_t).isoformat()
                        end_dt = datetime.datetime.combine(e_date, e_end_t).isoformat()

                        conflict, conflict_title, source = calendar_utils.detect_all_conflicts(start_dt, end_dt)
                        if conflict:
                            st.warning(f"\u26a0\ufe0f Time conflict with '{conflict_title}' ({source})")

                        insert_event(e_title, start_dt, end_dt)
                        st.success("Event saved locally!")

                        if send_notify:
                            ok, msg = notify.notify_event_creation(e_title, start_dt, end_dt)
                            if ok:
                                st.info("\U0001f4e7 Email notification sent.")
                            else:
                                st.warning(f"\U0001f4e7 Email: {msg}")

                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save event: {e}")
                else:
                    st.warning("Please provide a title.")

# ===============================
# KANBAN TASKS
# ===============================
with tab_tasks:
    st.markdown('<p class="section-title">\U0001f4cb Academic Kanban Board</p>', unsafe_allow_html=True)

    with st.expander("\u2795 Quick Add Task"):
        with st.form("add_task"):
            t_title = st.text_input("Task Title")
            t_due = st.date_input("Due Date")
            if st.form_submit_button("Add Task", width="stretch"):
                if t_title:
                    insert_task(t_title, t_due.isoformat())
                    st.success("Task added!")
                    st.rerun()
                else:
                    st.warning("Please provide a title.")

    tasks = fetch_tasks()
    col_todo, col_progress, col_done = st.columns(3)

    status_styles = {
        'pending': {'color': '#E53E3E', 'bg': '#FFF5F5', 'label': '\U0001f534 To Do'},
        'in_progress': {'color': '#D69E2E', 'bg': '#FFFFF0', 'label': '\U0001f7e1 In Progress'},
        'completed': {'color': '#38A169', 'bg': '#F0FFF4', 'label': '\U0001f7e2 Completed'},
    }

    for col, sk in [(col_todo, 'pending'), (col_progress, 'in_progress'), (col_done, 'completed')]:
        with col:
            s = status_styles[sk]
            st.markdown(
                f'<div style="background:{s["bg"]};border-radius:14px;padding:10px;margin-bottom:12px;'
                f'text-align:center;border:1px solid {s["color"]}40;">'
                f'<span style="font-weight:700;color:{s["color"]};">{s["label"]}</span></div>',
                unsafe_allow_html=True)

            column_tasks = [t for t in tasks if
                            (sk == 'pending' and ((len(t) > 4 and t[4] == 'pending') or (len(t) > 3 and t[3] == 'pending') or t[3] is None)) or
                            (sk != 'pending' and ((len(t) > 4 and t[4] == sk) or t[3] == sk))]

            if not column_tasks:
                st.caption(f"No tasks in this column.")
                continue

            for t in column_tasks:
                due_str = f"Due: {t[2]}" if t[2] else "No due date"
                st.markdown(
                    f'<div style="background:#fff;border-radius:12px;padding:10px 14px;margin-bottom:6px;'
                    f'border-left:4px solid {s["color"]};box-shadow:0 1px 3px rgba(0,0,0,0.06);">'
                    f'<div style="font-weight:600;font-size:0.9rem;color:#2d3748;">{t[1]}</div>'
                    f'<div style="font-size:0.75rem;color:#a0aec0;margin-top:2px;">{due_str}</div>'
                    f'</div>', unsafe_allow_html=True)

                if sk == 'pending':
                    if st.button("\u25b6 Start", key=f"start_{t[0]}", width="stretch"):
                        update_task_status(t[0], 'in_progress')
                        st.rerun()
                elif sk == 'in_progress':
                    if st.button("\u2713 Finish", key=f"finish_{t[0]}", width="stretch"):
                        update_task_status(t[0], 'completed')
                        log_focus_session(0, t[1], 50)
                        st.rerun()

# ===============================
# ANALYTICS
# ===============================
with tab_stats:
    st.markdown('<p class="section-title">\U0001f4ca Productivity Insights</p>', unsafe_allow_html=True)
    stats = analytics.get_study_stats()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Focus Time", f"{stats['total_focus_time']} mins")
    m2.metric("XP Gained", f"{xp:,} pts")
    m3.metric("OS Level", f"Lvl {level}")

    if stats.get('subject_distribution'):
        st.markdown('<div class="glow-card" style="margin-top:1rem;">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">\U0001f4ca Subject Breakdown</p>', unsafe_allow_html=True)
        df_dist = pd.DataFrame(
            list(stats['subject_distribution'].items()),
            columns=["Subject", "Minutes"]
        )
        st.bar_chart(df_dist.set_index("Subject"), color="#f5af19")
        st.markdown('</div>', unsafe_allow_html=True)

    if stats.get('recent_logs'):
        st.markdown('<div class="glow-card" style="margin-top:1rem;">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">\u23f1\ufe0f Recent Focus Sessions</p>', unsafe_allow_html=True)
        df_logs = pd.DataFrame(stats['recent_logs'])
        _col_map = {"id": "ID", "start_time": "Time", "duration": "Duration (min)", "points": "XP", "subject": "Subject"}
        df_logs = df_logs.rename(columns={k: v for k, v in _col_map.items() if k in df_logs.columns})
        _drop = [c for c in ["ID"] if c in df_logs.columns]
        st.dataframe(df_logs.drop(columns=_drop, errors="ignore"), width="stretch", hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# AI AGENTS
# ===============================
with tab_agents:
    st.markdown('<p class="section-title">\U0001f916 AI Agent Command Center</p>', unsafe_allow_html=True)

    agent_tabs = st.tabs(["\U0001f4cb Planner", "\U0001f504 Rescheduler", "\U0001f4da Readiness", "\U0001f9d8 Wellness", "\U0001f4c8 Analytics"])

    with agent_tabs[0]:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown("Generate an optimized study schedule based on your workload.")
        subj_input = st.text_input("Subjects (comma-separated)", "Math, Physics, CS, History")
        hours_per_day = st.slider("Available study hours per day", 1, 12, 4)
        priority_subject = st.text_input("Priority subject (if any)", "Math")
        if st.button("Generate Study Plan", width="stretch"):
            subjects = [s.strip() for s in subj_input.split(",") if s.strip()]
            with st.spinner("Planner agent is optimizing your schedule..."):
                plan = planner_agent.generate_plan(
                    subjects=subjects, hours_per_day=hours_per_day,
                    priority_subject=priority_subject
                )
            st.markdown(
                f'<div style="background:#ffffff; border-radius:14px; border:1px solid #e2e8f0; '
                f'padding:16px; margin-top:12px; white-space:pre-wrap;">{plan}</div>',
                unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with agent_tabs[1]:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown("Automatically reschedule missed sessions and rebalance workload.")
        missed_sessions = rescheduler_agent.detect_missed_sessions()
        if missed_sessions:
            st.warning(f"Found {len(missed_sessions)} missed session(s).")
            for ms in missed_sessions:
                st.markdown(
                    f'<div style="display:flex; align-items:center; gap:8px; padding:8px 12px; '
                    f'background:#FFF5F5; border:1px solid #FED7D7; border-radius:10px; margin-bottom:4px;">'
                    f'<span style="font-size:1rem;">\u26a0\ufe0f</span>'
                    f'<span><strong>{ms["title"]}</strong> \u2014 {ms["scheduled_time"]}</span></div>',
                    unsafe_allow_html=True)
            if st.button("Auto-Reschedule All", width="stretch"):
                result = rescheduler_agent.auto_reschedule(missed_sessions)
                st.success(result)
                st.rerun()
        else:
            st.success("No missed sessions detected. You're on track!")
        st.markdown('</div>', unsafe_allow_html=True)

    with agent_tabs[2]:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown("Predict your exam readiness based on study data.")
        _subjects = db.get_subject_names() or ["Math", "Physics", "Computer Science", "History"]
        for subj in _subjects:
            score = readiness_agent.get_readiness_score(subj)
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f'<p style="margin-bottom:2px;"><strong>{subj}</strong></p>',
                            unsafe_allow_html=True)
                st.progress(score / 100)
            with col_b:
                st.metric("Score", f"{score:.0f}%")
        summary = readiness_agent.get_readiness_summary()
        st.info(f"**Overall Readiness:** {summary['avg_score']:.0f}% \u2014 {summary['recommendation']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with agent_tabs[3]:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        status = wellness_agent.get_wellness_status()
        w1, w2, w3 = st.columns(3)
        w1.metric("Energy Level", f"{status['energy_level']:.0f}%")
        w2.metric("Today's Study", f"{status['today_minutes']} min")
        w3.metric("Breaks Taken", f"{status['breaks_taken']}")

        if status['alerts']:
            for alert in status['alerts']:
                st.warning(f"\u26a0\ufe0f {alert}")
        if status['recommendation']:
            st.success(f"\U0001f4a1 {status['recommendation']}")
        if status['energy_level'] < 40:
            st.error("\U0001f6a8 Burnout risk detected! Take a longer break or stop for today.")

        st.divider()
        st.markdown('<p style="font-weight:600;">Weekly Trend</p>', unsafe_allow_html=True)
        weekly_data = wellness_agent.get_weekly_trend()
        if weekly_data:
            df_w = pd.DataFrame(weekly_data)
            if not df_w.empty and 'date' in df_w.columns:
                st.line_chart(df_w.set_index('date'), color="#f5af19")
        st.markdown('</div>', unsafe_allow_html=True)

    with agent_tabs[4]:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        report = analytics_agent.generate_report()
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Study Streak", f"{report.get('streak', 0)} days")
        a2.metric("Completion Rate", f"{report.get('completion_rate', 0):.0f}%")
        a3.metric("Avg Daily Focus", f"{report.get('avg_daily_minutes', 0):.0f} min")
        a4.metric("Sessions Missed", f"{report.get('missed_sessions', 0)}")
        if report.get('trends'):
            st.markdown('<p class="section-title">\U0001f4c8 Study Trends</p>', unsafe_allow_html=True)
            df_t = pd.DataFrame(report['trends'])
            if not df_t.empty and 'date' in df_t.columns:
                st.line_chart(df_t.set_index('date'), color="#f5af19")
        if report.get('recommendations'):
            st.markdown('<p class="section-title">\U0001f4a1 Recommendations</p>', unsafe_allow_html=True)
            for rec in report['recommendations']:
                st.info(f"\U0001f4a1 {rec}")
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# VOICE
# ===============================
with tab_voice:
    st.markdown('<div class="glow-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">\U0001f399\ufe0f Voice Command Center</p>', unsafe_allow_html=True)
    st.info("Type your command below. It will be processed as voice input via the LangChain agent.")
    v_query = st.text_input("Speak/Type your command...",
                           key="voice_input_field",
                           placeholder="e.g. 'Schedule math at 5 PM'")
    if st.button("Process Command", width="stretch"):
        if v_query:
            with st.spinner("Processing voice command..."):
                result = voice_module.process_voice_command(v_query)
            st.markdown('<p style="font-weight:600; margin-top:12px;">\U0001f916 AI Intent Detected:</p>',
                       unsafe_allow_html=True)
            st.json(result)
        else:
            st.warning("Please enter a command.")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# AI ASSISTANT
# ===============================
with tab_ai:
    st.markdown('<div class="glow-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">\U0001f9e0 Intelligence Hub</p>', unsafe_allow_html=True)

    # Chat History Display
    if _has_langchain_agent and "chat_memory" in st.session_state:
        _chat_mem = st.session_state.chat_memory
        _history = _chat_mem.get_history()
        if _history:
            st.markdown(
                '<p style="font-weight:600; margin-bottom:8px; font-size:0.9rem;">Chat History</p>',
                unsafe_allow_html=True)
            for _msg in _history[-10:]:
                if isinstance(_msg, HumanMessage):
                    st.markdown(
                        f'<div style="background:#EBF4FF; border-radius:10px; padding:8px 12px; '
                        f'margin-bottom:4px; border-left:3px solid #4299E1;">'
                        f'<strong style="color:#2B6CB0;">You:</strong> '
                        f'<span style="color:#2D3748;">{_msg.content}</span></div>',
                        unsafe_allow_html=True)
                elif isinstance(_msg, AIMessage):
                    _full = _msg.content
                    _truncated = _full[:400] + ("..." if len(_full) > 400 else "")
                    st.markdown(
                        f'<div style="background:#F0FFF4; border-radius:10px; padding:8px 12px; '
                        f'margin-bottom:4px; border-left:3px solid #48BB78;">'
                        f'<strong style="color:#276749;">AI:</strong> '
                        f'<span style="color:#2D3748;">{_truncated}</span></div>',
                        unsafe_allow_html=True)
            c_hist1, c_hist2 = st.columns([1, 1])
            with c_hist1:
                if st.button("\U0001f5d1\ufe0f Clear Chat History", width="stretch"):
                    _chat_mem.clear()
                    st.rerun()
            with c_hist2:
                st.caption(f"{_chat_mem.message_count} messages in memory")
            st.divider()

    query = st.text_input(
        "\U0001f4ac Ask the OS (e.g., 'Suggest a study time for Math')",
        placeholder="Type your academic query here...",
    )

    col_exec, col_new = st.columns([3, 1])
    with col_exec:
        execute_clicked = st.button("Execute AI Command", width="stretch")
    with col_new:
        if _has_langchain_agent and st.button("\U0001f4dd New Chat", width="stretch"):
            if "chat_memory" in st.session_state:
                st.session_state.chat_memory.clear()
                st.rerun()

    if execute_clicked:
        if query:
            _status = st.empty()
            _status.info("Routing your query...")
            try:
                _agent_response = None
                if _has_langchain_agent:
                    _chat_mem = st.session_state.get("chat_memory")
                    _agent = AcademicAgent()
                    _status.info("AI is analyzing your request...")
                    _agent_response = _agent.execute(query, memory=_chat_mem)
                    if _chat_mem:
                        _chat_mem.add_user_message(query)
                        _chat_mem.add_ai_message(_agent_response.message)
                    result = _agent_response.raw_action
                else:
                    result = process_query(query)

                _status.empty()

                if _agent_response and _agent_response.tools_used:
                    _tool_names = [t.tool_name for t in _agent_response.tools_used]
                    _kb_used = "search_knowledge_base" in _tool_names
                    _tool_badges = " ".join(
                        [f'<span style="background:#EDF2F7; border-radius:6px; '
                         f'padding:2px 8px; font-size:0.75rem; color:#4A5568; '
                         f'margin-right:4px;">{tn}</span>' for tn in _tool_names]
                    )
                    st.markdown(
                        f'<div style="margin-bottom:8px;">'
                        f'<span style="font-weight:600; font-size:0.85rem; color:#4A5568;">Actions: </span>'
                        f'{_tool_badges}</div>',
                        unsafe_allow_html=True)
                    if _kb_used:
                        st.markdown(
                            '<span style="background:#EBF8FF; border-radius:6px; padding:2px 8px; '
                            'font-size:0.75rem; color:#2B6CB0; font-weight:600;">'
                            '\U0001f4da Knowledge Base Searched</span>',
                            unsafe_allow_html=True)

                if _agent_response and _agent_response.message:
                    st.markdown(_agent_response.message)

                if _agent_response and _agent_response.tools_used:
                    with st.expander("\U0001f527 Tool Execution Details", expanded=False):
                        for _tool_exec in _agent_response.tools_used:
                            _icon = "\u2705" if _tool_exec.success else "\u274c"
                            st.markdown(f"**{_icon} {_tool_exec.tool_name}**")
                            st.code(_tool_exec.input_data, language="json")
                            st.code(_tool_exec.output_data, language="json")
                            st.markdown("---")

                        _exec_log = get_tool_execution_log()
                        if _exec_log:
                            st.markdown("**Recent Execution Log:**")
                            for _log_entry in reversed(_exec_log[-5:]):
                                _ts = _log_entry.get("timestamp", "")[:19]
                                _tn = _log_entry.get("tool_name", "")
                                _ok = "\u2705" if _log_entry.get("success") else "\u274c"
                                st.markdown(f"- {_ok} `{_ts}` **{_tn}**")

                if _agent_response and _agent_response.tools_used:
                    _kb_used = any(
                        t.tool_name == "search_knowledge_base" for t in _agent_response.tools_used
                    )
                    if _kb_used:
                        for _t_exec in _agent_response.tools_used:
                            if _t_exec.tool_name == "search_knowledge_base":
                                try:
                                    _kb_data = json.loads(_t_exec.output_data)
                                    if _kb_data.get("found") and _kb_data.get("sources"):
                                        st.markdown(
                                            '<p style="font-weight:600; margin-top:12px;">'
                                            '\U0001f4da Sources from Knowledge Base:</p>',
                                            unsafe_allow_html=True)
                                        for _src in _kb_data["sources"]:
                                            _page = f" (p.{_src['page']})" if "page" in _src else ""
                                            st.markdown(
                                                f'<div style="background:#EBF8FF; border-radius:8px; '
                                                f'padding:6px 12px; margin-bottom:4px; '
                                                f'border-left:3px solid #4299E1; font-size:0.85rem;">'
                                                f'\U0001f4c4 <strong>{_src["filename"]}</strong>{_page}</div>',
                                                unsafe_allow_html=True)
                                except (json.JSONDecodeError, KeyError):
                                    pass

                action = result.get("action")

                if action == "create":
                    title = result.get("title", "Event")
                    start = result.get("start", datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"))
                    end = result.get("end", (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)).isoformat().replace("+00:00", "Z"))
                    try:
                        conflict, alt = scheduler_pro.resolve_conflict_pro(title, start, end)
                        if conflict:
                            st.error(f"\u26a0\ufe0f Conflict with '{conflict}'")
                            if alt and alt[0]:
                                st.info(f"\U0001f449 Suggesting Alternative: {alt[0]}")
                                if st.button("Accept Suggestion"):
                                    insert_event(title, alt[0], alt[1])
                                    try: g_create_event(title, alt[0], alt[1])
                                    except Exception as _ge: logging.getLogger(__name__).debug("GC create failed: %s", _ge)
                                    st.success("Scheduled alternative!")
                        else:
                            insert_event(title, start, end)
                            try: g_create_event(title, start, end)
                            except Exception as _ge: logging.getLogger(__name__).debug("GC create failed: %s", _ge)
                            st.success("Event added!")
                    except Exception as _ce_err:
                        logging.getLogger(__name__).warning("Conflict check failed: %s", _ce_err)
                        insert_event(title, start, end)
                        st.success("Event added (conflict check skipped)!")

                elif action == "recommend":
                    subj = result.get("subject", "Study")
                    try:
                        s, e = scheduler_pro.suggest_optimal_study_time(subj)
                        if s:
                            st.success(f"Best time for {subj}: **{s}**")
                            if st.button("Schedule Now"):
                                insert_event(f"Study: {subj}", s, e)
                                try: g_create_event(f"Study: {subj}", s, e)
                                except Exception as _ge: logging.getLogger(__name__).debug("GC create failed: %s", _ge)
                                st.success("Optimized session booked!")
                    except Exception as _opt_err:
                        logging.getLogger(__name__).debug("Optimal time calc failed: %s", _opt_err)
                        st.info("Could not calculate optimal time. Try manual scheduling.")

                elif action == "study_plan":
                    subjects = result.get("subjects", ["All"])
                    plan = generate_study_plan(", ".join(subjects))
                    st.markdown(f"### \U0001f4cb Generated Plan\n{plan}")

                elif action == "task":
                    insert_task(result.get("title", "New Task"),
                               result.get("due_date", datetime.date.today().isoformat()))
                    st.success("Task added to Kanban!")

                elif action == "focus":
                    st.info(f"Starting focus session for {result.get('subject', 'Study')} "
                           f"({result.get('duration', 25)} mins)")

                elif action == "stats":
                    st.info("View your stats in the Analytics tab!")

                elif action == "unknown":
                    st.warning(result.get("response", "I'm not sure how to help with that."))

            except Exception as e:
                _status.empty()
                st.error(f"AI Error: {e}")
        else:
            st.warning("Please enter a query.")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# KNOWLEDGE BASE (Phase 3: RAG)
# ===============================
with tab_kb:
    st.markdown('<p class="section-title">\U0001f4da Knowledge Base</p>', unsafe_allow_html=True)

    if not _has_rag:
        st.error("RAG module not available. Install required dependencies: `pip install faiss-cpu langchain-community langchain-text-splitters pypdf docx2txt`")
    else:
        kb_col1, kb_col2 = st.columns([2, 1])

        with kb_col1:
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<p style="font-weight:600; margin-bottom:8px;">\U0001f4c1 Upload Documents</p>',
                       unsafe_allow_html=True)
            st.markdown(
                '<p style="color:#718096; font-size:0.85rem; margin-bottom:12px;">'
                'Upload PDF, TXT, or DOCX files to build your academic Knowledge Base. '
                'The AI assistant will use these documents to answer questions '
                'with source citations.</p>',
                unsafe_allow_html=True)

            uploaded_files = st.file_uploader(
                "Choose files",
                type=["pdf", "txt", "docx"],
                accept_multiple_files=True,
                key="kb_uploader",
                help="Supported: PDF, TXT, DOCX (max 50MB each)"
            )

            if uploaded_files:
                if st.button("\U0001f4e4 Upload & Process", width="stretch", key="kb_process"):
                    processor = DocumentProcessor()
                    rag_pipeline = get_rag_pipeline()

                    progress_bar = st.progress(0, text="Processing documents...")
                    total = len(uploaded_files)
                    success_count = 0
                    skip_count = 0
                    error_count = 0

                    for i, uploaded_file in enumerate(uploaded_files):
                        filename = uploaded_file.name
                        file_size = uploaded_file.size

                        progress_bar.progress(
                            (i) / total,
                            text=f"Processing {filename}..."
                        )

                        is_valid, error_msg = processor.validate_file(filename, file_size)
                        if not is_valid:
                            st.warning(f"\u26a0\ufe0f {filename}: {error_msg}")
                            skip_count += 1
                            continue

                        doc_id = processor.generate_doc_id(filename, file_size)
                        existing = get_document(doc_id)
                        if existing:
                            st.info(f"\U0001f504 {filename} already in Knowledge Base.")
                            skip_count += 1
                            continue

                        file_content = uploaded_file.read()
                        file_path = processor.save_uploaded_file(file_content, filename, doc_id)
                        if not file_path:
                            st.error(f"\u274c Failed to save {filename}")
                            error_count += 1
                            continue

                        try:
                            chunks = processor.process_file(file_path, doc_id)
                            if chunks:
                                rag_pipeline.vector_store.add_documents(chunks, doc_id)
                                insert_document(
                                    doc_id, filename, file_path,
                                    os.path.splitext(filename)[1].lower(),
                                    file_size, len(chunks)
                                )
                                st.success(f"\u2705 {filename}: {len(chunks)} chunks indexed")
                                success_count += 1
                            else:
                                st.warning(
                                    f"\u26a0\ufe0f {filename}: No content extracted. "
                                    f"This may be a scanned/image PDF (OCR not supported), "
                                    f"or the file has no readable text."
                                )
                                skip_count += 1
                        except Exception as e:
                            st.error(f"\u274c Error processing {filename}: {e}")
                            error_count += 1

                    progress_bar.progress(1.0, text="Done!")
                    st.caption(f"Processed: {success_count} indexed, {skip_count} skipped, {error_count} errors")
                    time.sleep(1)
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

            # Document list
            st.markdown('<div class="glow-card" style="margin-top:1rem;">', unsafe_allow_html=True)
            st.markdown('<p style="font-weight:600; margin-bottom:8px;">\U0001f4c4 Uploaded Documents</p>',
                       unsafe_allow_html=True)

            try:
                documents = fetch_documents()
                if documents:
                    for doc in documents:
                        doc_id_db = doc[0]
                        filename_db = doc[1]
                        file_type = doc[3]
                        file_size_db = doc[4]
                        chunk_count_db = doc[5]
                        uploaded_at = doc[6]
                        status = doc[7]

                        icon = {"pdf": "\U0001f4c4", "txt": "\U0001f4dd", "docx": "\U0001f4c3"}.get(file_type, "\U0001f4c4")
                        size_str = f"{file_size_db / 1024:.1f}KB" if file_size_db < 1024*1024 else f"{file_size_db / 1024 / 1024:.1f}MB"
                        status_icon = "\u2705" if status == "indexed" else "\u26a0\ufe0f"

                        col_name, col_info, col_del = st.columns([3, 2, 1])
                        with col_name:
                            st.markdown(f"**{icon} {filename_db}**")
                        with col_info:
                            st.caption(f"{chunk_count_db} chunks | {size_str} | {status_icon} {status}")
                        with col_del:
                            if st.button("\U0001f5d1\ufe0f", key=f"del_doc_{doc_id_db}", help="Delete document"):
                                try:
                                    import shutil
                                    doc_dir = os.path.dirname(doc[2])
                                    if os.path.exists(doc_dir):
                                        shutil.rmtree(doc_dir)
                                except OSError as _rm_err:
                                    logging.getLogger(__name__).warning("File cleanup failed: %s", _rm_err)
                                try:
                                    rag_p = get_rag_pipeline()
                                    rag_p.vector_store.delete_documents_by_id(doc_id_db)
                                except Exception as _faiss_err:
                                    logging.getLogger(__name__).warning("FAISS delete failed: %s", _faiss_err)
                                delete_document(doc_id_db)
                                st.success(f"Deleted {filename_db}")
                                st.rerun()
                else:
                    st.markdown(
                        '<p style="color:#a0aec0; text-align:center; padding:2rem;">'
                        'No documents uploaded yet. Upload PDF, TXT, or DOCX files above.</p>',
                        unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading documents: {e}")

            st.markdown('</div>', unsafe_allow_html=True)

        with kb_col2:
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<p style="font-weight:600; margin-bottom:8px;">\U0001f4ca Knowledge Base Stats</p>',
                       unsafe_allow_html=True)

            try:
                rag_p = get_rag_pipeline()
                kb_status = rag_p.get_status()

                st.metric("Documents", kb_status.get("total_documents", 0))
                st.metric("Indexed Chunks", kb_status.get("total_chunks", 0))

                idx_size = kb_status.get("index_size_bytes", 0)
                if idx_size > 1024*1024:
                    size_str = f"{idx_size / 1024 / 1024:.1f} MB"
                elif idx_size > 1024:
                    size_str = f"{idx_size / 1024:.1f} KB"
                else:
                    size_str = f"{idx_size} B"
                st.metric("Index Size", size_str)

                st.markdown("---")
                st.markdown(
                    f'<p style="color:#718096; font-size:0.8rem;">'
                    f'<strong>Embedding Model:</strong> Google Gemini Embedding 2 Preview<br>'
                    f'<strong>Vector Store:</strong> FAISS<br>'
                    f'<strong>Chunk Size:</strong> 1000 chars<br>'
                    f'<strong>Chunk Overlap:</strong> 200 chars<br>'
                    f'<strong>Retrieval Top-K:</strong> 4</p>',
                    unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading KB stats: {e}")

            st.markdown('</div>', unsafe_allow_html=True)

            # Clear KB
            st.markdown('<div class="glow-card" style="margin-top:1rem;">', unsafe_allow_html=True)
            st.markdown('<p style="font-weight:600; margin-bottom:8px;">\u26a0\ufe0f Danger Zone</p>',
                       unsafe_allow_html=True)
            if st.button("\U0001f5d1\ufe0f Clear Entire Knowledge Base", width="stretch", type="secondary"):
                st.session_state["confirm_clear_kb"] = True

            if st.session_state.get("confirm_clear_kb"):
                st.warning("This will permanently delete all uploaded documents and the FAISS index.")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("\u2705 Yes, Clear All", width="stretch"):
                        try:
                            # Clear FAISS index
                            rag_p = get_rag_pipeline()
                            rag_p.vector_store.clear_index()

                            # Clear uploaded files
                            import shutil
                            upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")
                            if os.path.exists(upload_dir):
                                shutil.rmtree(upload_dir)

                            # Clear DB records
                            with db.get_connection() as conn:
                                conn.cursor().execute("DELETE FROM documents")

                            st.session_state["confirm_clear_kb"] = False
                            st.success("Knowledge Base cleared!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error clearing KB: {e}")
                with c2:
                    if st.button("Cancel", width="stretch"):
                        st.session_state["confirm_clear_kb"] = False
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# SETTINGS
# ===============================
with tab_settings:
    st.markdown('<p class="section-title">\u2699\ufe0f OS Configuration</p>', unsafe_allow_html=True)

    tab_settings_col1, tab_settings_col2 = st.columns(2)
    with tab_settings_col1:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        new_name = st.text_input("User Name", value=user_name)
        new_email = st.text_input("Notification Email", value=get_profile_value("user_email", ""))
        if st.button("Save Profile", width="stretch"):
            set_profile_value("user_name", new_name)
            set_profile_value("user_email", new_email)
            st.success("Profile Updated!")
            st.rerun()

        st.divider()
        if st.button("\U0001f4e7 Test Email Notification", width="stretch"):
            email_to = get_profile_value("user_email", "")
            if email_to:
                ok, msg = notify.send_alert("Test from Smart OS", "This is a test notification. If you see this, email is working!")
                if ok:
                    st.success(f"\u2705 Test email sent to {email_to}")
                else:
                    st.error(f"\u274c Email failed: {msg}")
            else:
                st.warning("Set an email in the field above first.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_settings_col2:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p style="font-weight:600; margin-bottom:8px;">\U0001f3c6 Achievements</p>',
                   unsafe_allow_html=True)
        achievements = fetch_achievements()
        if achievements:
            for a in achievements:
                unlocked = a[2] if len(a) > 2 else True
                icon = "\u2705" if unlocked else "\U0001f512"
                st.markdown(
                    f'<div style="display:flex; align-items:center; gap:10px; padding:8px 12px; '
                    f'background:{"#F0FFF4" if unlocked else "#f7fafc"}; '
                    f'border-radius:10px; margin-bottom:6px; border:1px solid #e2e8f0;">'
                    f'<span>{icon}</span>'
                    f'<span style="color:{"#2d3748" if unlocked else "#a0aec0"};">'
                    f'{a[1]}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color:#a0aec0;">No achievements yet. Start studying!</p>',
                       unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# ADMIN DEBUG PANEL (hidden by default)
# ===============================
if os.getenv("SMART_OS_DEBUG", "0") == "1":
    with st.expander("\U0001f527 Admin Debug Panel", expanded=False):
        st.markdown("**System Status**")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("DB Path", db.DB_PATH)
        col_b.metric("Tools Loaded", "Yes" if _has_langchain_agent else "No")
        col_c.metric("RAG Available", "Yes" if _has_rag else "No")

        st.markdown("**Tool Execution Log**")
        try:
            from core.tools import get_tool_execution_log
            _exec_log = get_tool_execution_log()
            if _exec_log:
                for entry in reversed(_exec_log[-10:]):
                    _icon = "\u2705" if entry.get("success") else "\u274c"
                    st.markdown(f"- {_icon} `{entry.get('timestamp', '')[:19]}` **{entry.get('tool_name', '')}**")
            else:
                st.caption("No tool executions yet.")
        except Exception as _tlog_err:
            st.caption(f"Tool log unavailable: {_tlog_err}")

        st.markdown("**Session State Keys**")
        st.code(list(st.session_state.keys()), language="python")

import streamlit as st
import datetime
import pandas as pd
import time

<<<<<<< HEAD
# Existing imports
=======
>>>>>>> 118f928 (Final Submission)
from ai_agent import process_query
from models import (
    insert_event, fetch_events, insert_task, fetch_tasks, update_task_status,
    log_focus_session, fetch_focus_logs, get_profile_value, set_profile_value,
<<<<<<< HEAD
    fetch_achievements, unlock_achievement
=======
    fetch_achievements, unlock_achievement, fetch_notifications
>>>>>>> 118f928 (Final Submission)
)
from streamlit_calendar import calendar
from study_planner import generate_study_plan
from google_calendar import (
    create_event as g_create_event,
    get_events as g_get_events,
    check_conflict
)
from email_utils import send_email
<<<<<<< HEAD

# New module imports
=======
from notification_engine import notify_event_creation

>>>>>>> 118f928 (Final Submission)
import analytics
import gamification
import scheduler_pro
import lms_sync
import voice_module
<<<<<<< HEAD
import notification_engine

<<<<<<< HEAD
st.set_page_config(page_title="Smart Academic OS", layout="wide")
=======
st.set_page_config(page_title="Smart Academic OS", layout="wide", page_icon="🎓")
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

# ===============================
# 🏆 SIDEBAR: GAMIFICATION & STATS
# ===============================
st.sidebar.title("🚀 Smart Academic OS")
st.sidebar.divider()

user_name = get_profile_value("user_name", "Student")
st.sidebar.header(f"👋 Hello, {user_name}!")

# Level & XP
=======
import calendar_utils
import notification_engine as notify
from agents import (
    planner_agent, rescheduler_agent, readiness_agent,
    wellness_agent, analytics_agent
)

st.set_page_config(page_title="Smart Academic OS", page_icon="🎓", layout="wide")

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
        content: "▶" !important;
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



# ===============================
# SIDEBAR
# ===============================
st.sidebar.markdown('<div style="text-align:center; padding: 0.5rem 0;">'
                    '<h1 style="font-size:1.5rem;">🚀 Smart Academic OS</h1>'
                    '<p style="color:#a0aec0; font-size:0.75rem; margin-top:-8px;">'
                    'AI-Powered Learning Platform</p></div>',
                    unsafe_allow_html=True)
st.sidebar.divider()

user_name = get_profile_value("user_name", "Student")
st.sidebar.markdown(f'<div style="text-align:center; margin-bottom:1rem;">'
                    f'<span style="font-size:2.5rem;">👋</span>'
                    f'<p style="font-size:1.1rem; font-weight:600; margin-top:4px;">Hello, {user_name}!</p></div>',
                    unsafe_allow_html=True)

>>>>>>> 118f928 (Final Submission)
level = gamification.get_user_level()
xp = gamification.calculate_xp()
progress = gamification.get_progress_to_next_level()

<<<<<<< HEAD
st.sidebar.metric("Current Level", f"Lvl {level}")
st.sidebar.metric("Total XP", f"{xp} pts")
st.sidebar.progress(progress, text=f"Next Level: {int(progress*100)}%")

st.sidebar.divider()
st.sidebar.subheader("🎯 Quick Actions")
if st.sidebar.button("Sync LMS Assignments"):
<<<<<<< HEAD
    with st.spinner("Syncing with Canvas..."):
        new_count = lms_sync.sync_assignments_to_db()
        st.sidebar.success(f"Fetched {new_count} new tasks!")
        time.sleep(1)
        st.rerun()
=======
=======
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
        f'<span style="font-size:1.1rem;">🔔</span>'
        f'<span style="font-size:0.85rem; font-weight:600; color:#C53030;">'
        f'{len(unread)} unread notification(s)</span></div>',
        unsafe_allow_html=True)

st.sidebar.markdown('<p style="font-weight:600; font-size:0.9rem;">🎯 Quick Actions</p>',
                    unsafe_allow_html=True)
if st.sidebar.button("Sync LMS Assignments", use_container_width=True):
>>>>>>> 118f928 (Final Submission)
    with st.spinner("Syncing with LMS..."):
        try:
            new_count = lms_sync.sync_assignments_to_db()
            st.sidebar.success(f"Fetched {new_count} new tasks!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"LMS Sync Failed: {e}")
<<<<<<< HEAD
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

# ===============================
# 📑 MAIN TABS
# ===============================
tab_dash, tab_cal, tab_tasks, tab_stats, tab_voice, tab_ai, tab_settings = st.tabs([
    "🏠 Dashboard", "📅 Calendar", "📋 Tasks", "📊 Analytics", "🎙️ Voice", "🧠 AI Assistant", "⚙️ Settings"
])

# ===============================
# 🏠 DASHBOARD
# ===============================
with tab_dash:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🗓️ Next Up")
<<<<<<< HEAD
        events = g_get_events()
        if events:
            for e in events[:3]:
                st.info(f"**{e.get('summary')}** | {e['start'].get('dateTime')}")
        else:
            st.write("No upcoming events.")
            
        st.subheader("🔥 Daily Focus Goal")
        st.progress(0.65, text="4h 30m / 7h Focused")

    with col2:
        st.subheader("🚀 Pomodoro Timer")
        subject = st.selectbox("Choose Subject", ["Math", "Physics", "Computer Science", "History"])
        timer_mins = st.number_input("Duration (mins)", value=25)
        if st.button("Start Deep Work"):
            st.warning(f"Focusing on {subject} for {timer_mins}m...")
            # Simulation of completion
            if st.button("End Session Early"):
                 st.write("Session stopped.")
            else:
                # Mocking a finished session for the UI
                log_focus_session(timer_mins, subject, timer_mins * 2)
                unlock_achievement("Deep Work Initiate", "Completed first 25m session")
                st.success("Session completed! +50 XP")
=======
        try:
            g_events = g_get_events()
            if g_events:
                for e in g_events[:3]:
                    st.info(f"**{e.get('summary')}** | {e['start'].get('dateTime', e['start'].get('date'))}")
            else:
                st.write("No upcoming Google events.")
        except:
            st.warning("Could not sync with Google Calendar. Showing local events.")
            l_events = fetch_events()
            if l_events:
                for e in l_events[-3:]:
                    st.info(f"**{e[1]}** | {e[2]}")
            
        st.subheader("🔥 Productivity Summary")
        stats = analytics.get_study_stats()
        st.write(f"Total Focus: **{stats['total_focus_time']} mins**")
        st.progress(min(1.0, stats['total_focus_time'] / 300), text="Daily Goal Progress")

    with col2:
        st.subheader("🚀 Pomodoro Timer")
        subject = st.selectbox("Choose Subject", ["Math", "Physics", "Computer Science", "History", "Other"])
        timer_mins = st.number_input("Duration (mins)", value=25, min_value=1)
        
        if st.button("Log Focus Session"):
            try:
                points = timer_mins * 2
                log_focus_session(timer_mins, subject, points)
                unlock_achievement("Deep Work Initiate", "Completed a focus session")
                st.success(f"Session logged! +{points} XP")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error logging session: {e}")
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

# ===============================
# 📅 CALENDAR
# ===============================
with tab_cal:
<<<<<<< HEAD
    st.subheader("📅 Interactive Schedule")
    try:
        g_events = g_get_events()
        calendar_events = []
        for e in g_events:
            calendar_events.append({
                "title": e.get("summary", "No Title"),
                "start": e["start"].get("dateTime"),
                "end": e["end"].get("dateTime"),
            })
        calendar(events=calendar_events)
    except Exception as e:
        st.warning(f"Calendar sync issue: {e}")
    
    st.divider()
    st.subheader("📌 Local Backup")
    local_events = fetch_events()
    for e in local_events[-5:]:
        st.write(f"📌 {e[1]} | {e[2]}")
=======
    st.subheader("📅 Smart Calendar")
    
    calendar_events = []
    
    # Load Google Events
=======

# ===============================
# MAIN TABS
# ===============================
tabs = st.tabs([
    "🏠 Dashboard", "📅 Calendar", "📋 Tasks", "📊 Analytics",
    "🤖 AI Agents", "🎙️ Voice", "🧠 AI Assistant", "⚙️ Settings"
])
tab_dash, tab_cal, tab_tasks, tab_stats, tab_agents, tab_voice, tab_ai, tab_settings = tabs

# ===============================
# DASHBOARD
# ===============================
with tab_dash:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🗓️ Upcoming Events</p>', unsafe_allow_html=True)
        try:
            g_events = g_get_events()
            if g_events:
                for e in g_events[:5]:
                    start = e['start'].get('dateTime', e['start'].get('date'))
                    st.markdown(
                        f'<div style="display:flex; align-items:center; gap:12px; '
                        f'padding:8px 12px; margin-bottom:4px; border-radius:10px; '
                        f'background:#f7fafc; border:1px solid #e2e8f0;">'
                        f'<span style="font-size:1.2rem;">📌</span>'
                        f'<div><strong style="color:#2d3748;">{e.get("summary")}</strong><br>'
                        f'<span style="font-size:0.8rem; color:#718096;">{start}</span></div>'
                        f'</div>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="color:#a0aec0;">No upcoming Google events.</p>',
                            unsafe_allow_html=True)
        except:
            st.markdown('<p style="color:#a0aec0;">Google Calendar unavailable.</p>',
                        unsafe_allow_html=True)
            local_events = fetch_events()
            if local_events:
                for e in local_events[-5:]:
                    st.markdown(
                        f'<div style="display:flex; align-items:center; gap:12px; padding:8px 12px; '
                        f'margin-bottom:4px; border-radius:10px; background:#f7fafc; border:1px solid #e2e8f0;">'
                        f'<span style="font-size:1.2rem;">📌</span>'
                        f'<div><strong style="color:#2d3748;">{e[1]}</strong><br>'
                        f'<span style="font-size:0.8rem; color:#718096;">{e[2]}</span></div>'
                        f'</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🔥 Daily Focus Goal</p>', unsafe_allow_html=True)
        stats = analytics.get_study_stats()
        today_mins = stats['total_focus_time']
        daily_goal = 300
        pct = min(1.0, today_mins / daily_goal)
        st.progress(pct, text=f"{today_mins}m / {daily_goal}m Focused")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🤖 AI Agent Insights</p>', unsafe_allow_html=True)
        ai_col1, ai_col2, ai_col3 = st.columns(3)
        readiness = readiness_agent.get_readiness_summary()
        wellness = wellness_agent.get_wellness_status()
        ai_col1.metric("📚 Readiness", f"{readiness['avg_score']:.0f}%")
        ai_col2.metric("⚡ Energy Level", f"{wellness['energy_level']:.0f}%")
        ai_col3.metric("📊 Tasks Done", f"{analytics_agent.get_completion_rate():.0f}%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🚀 Pomodoro Timer</p>', unsafe_allow_html=True)

        pomo = st.session_state.pomo
        if not pomo["running"]:
            subj = st.selectbox("Subject",
                                ["Math", "Physics", "Computer Science", "History", "Other"],
                                key="pomo_subj")
            dur = st.number_input("Minutes", 1, 120, 25, key="pomo_dur")
            if st.button("▶️ Start Focus Session", use_container_width=True, key="pomo_start"):
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
                st.success(f"🎉 Session complete! {dur} mins logged, +{points} XP")
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
                    if st.button("⏹️ Stop", use_container_width=True, key="pomo_stop"):
                        st.session_state.pomo["running"] = False
                        st.rerun()
                with c2:
                    if st.button("🔄 Reset", use_container_width=True, key="pomo_reset"):
                        st.session_state.pomo["running"] = False
                        st.rerun()

                if pomo["running"] and remaining > 0:
                    time.sleep(1)
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">🔥 Productivity Summary</p>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:2rem; font-weight:800; text-align:center; margin:8px 0; color:#2d3748;">'
            f'{today_mins}<span style="font-size:1rem; font-weight:400; '
            f'color:#a0aec0;"> mins</span></p>',
            unsafe_allow_html=True)
        st.progress(pct, text="Daily Goal Progress")
        st.markdown('</div>', unsafe_allow_html=True)

        if stats.get('subject_distribution'):
            st.markdown('<div class="glow-card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">📊 Subject Breakdown</p>', unsafe_allow_html=True)
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
    st.markdown('<p class="section-title">📅 Smart Calendar</p>', unsafe_allow_html=True)
    calendar_events = []

>>>>>>> 118f928 (Final Submission)
    try:
        g_events = g_get_events()
        for e in g_events:
            calendar_events.append({
                "title": f"☁️ {e.get('summary', 'No Title')}",
                "start": e["start"].get("dateTime", e["start"].get("date")),
                "end": e["end"].get("dateTime", e["end"].get("date")),
                "color": "#4285F4"
            })
    except:
        pass
<<<<<<< HEAD
        
    # Load Local DB Events
=======

>>>>>>> 118f928 (Final Submission)
    try:
        db_events = fetch_events()
        for e in db_events:
            calendar_events.append({
                "title": f"📌 {e[1]}",
                "start": e[2],
                "end": e[3],
                "color": "#34A853"
            })
    except Exception as e:
        st.error(f"Error loading local events: {e}")
<<<<<<< HEAD
        
    try:
        calendar(events=calendar_events)
    except Exception as e:
        st.warning("Advanced Calendar failed to render. Using simple list view.")
        if calendar_events:
            df_cal = pd.DataFrame(calendar_events)
            st.dataframe(df_cal[["title", "start", "end"]], use_container_width=True)
        else:
            st.write("No events scheduled.")
    
    st.divider()
    with st.expander("➕ Add Event Manually"):
        with st.form("add_event"):
            col_a, col_b = st.columns(2)
            e_title = st.text_input("Event Title")
            e_date = col_a.date_input("Date", value=datetime.date.today())
            e_start_t = col_b.time_input("Start Time", value=datetime.time(9, 0))
            e_end_t = col_b.time_input("End Time", value=datetime.time(10, 0))
            
            if st.form_submit_button("Save Event"):
=======

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
                        use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    with st.expander("➕ Add Event Manually"):
        with st.form("add_event"):
            e_title = st.text_input("Event Title")
            col_a, col_b = st.columns(2)
            e_date = col_a.date_input("Date", value=datetime.date.today())
            e_start_t = col_a.time_input("Start Time", value=datetime.time(9, 0))
            e_end_t = col_b.time_input("End Time", value=datetime.time(10, 0))
            send_notify = st.checkbox("Send email notification", value=False)
            if st.form_submit_button("Save Event", use_container_width=True):
>>>>>>> 118f928 (Final Submission)
                if e_title:
                    try:
                        start_dt = datetime.datetime.combine(e_date, e_start_t).isoformat()
                        end_dt = datetime.datetime.combine(e_date, e_end_t).isoformat()
<<<<<<< HEAD
                        insert_event(e_title, start_dt, end_dt)
                        st.success("Event saved locally!")
=======

                        conflict, conflict_title, source = calendar_utils.detect_all_conflicts(start_dt, end_dt)
                        if conflict:
                            st.warning(f"⚠️ Time conflict with '{conflict_title}' ({source})")

                        insert_event(e_title, start_dt, end_dt)
                        st.success("Event saved locally!")

                        if send_notify:
                            ok, msg = notify.notify_event_creation(e_title, start_dt, end_dt)
                            if ok:
                                st.info("📧 Email notification sent.")
                            else:
                                st.warning(f"📧 Email: {msg}")

>>>>>>> 118f928 (Final Submission)
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save event: {e}")
                else:
                    st.warning("Please provide a title.")
<<<<<<< HEAD
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

# ===============================
# 📋 KANBAN TASKS
# ===============================
with tab_tasks:
    st.subheader("📋 Academic Kanban Board")
<<<<<<< HEAD
=======
    
=======

# ===============================
# KANBAN TASKS
# ===============================
with tab_tasks:
    st.markdown('<p class="section-title">📋 Academic Kanban Board</p>', unsafe_allow_html=True)

>>>>>>> 118f928 (Final Submission)
    with st.expander("➕ Quick Add Task"):
        with st.form("add_task"):
            t_title = st.text_input("Task Title")
            t_due = st.date_input("Due Date")
<<<<<<< HEAD
            if st.form_submit_button("Add Task"):
                insert_task(t_title, t_due.isoformat())
                st.success("Task added!")
                st.rerun()
                
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)
    tasks = fetch_tasks()
    
    col_todo, col_progress, col_done = st.columns(3)
    
    with col_todo:
        st.markdown("### 🔴 To Do")
<<<<<<< HEAD
        for t in [x for x in tasks if x[4] == 'pending']:
=======
        for t in [x for x in tasks if x[3] == 'pending' or x[3] is None]:
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)
            with st.expander(f"**{t[1]}**"):
                st.write(f"Due: {t[2]}")
                if st.button("Start", key=f"start_{t[0]}"):
                    update_task_status(t[0], 'in_progress')
                    st.rerun()

    with col_progress:
        st.markdown("### 🟡 In Progress")
<<<<<<< HEAD
        for t in [x for x in tasks if x[4] == 'in_progress']:
=======
        for t in [x for x in tasks if x[3] == 'in_progress']:
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)
            with st.expander(f"**{t[1]}**"):
                st.write(f"Due: {t[2]}")
                if st.button("Finish", key=f"done_{t[0]}"):
                    update_task_status(t[0], 'completed')
<<<<<<< HEAD
                    log_focus_session(60, t[1], 100) # Auto XP
=======
                    log_focus_session(60, t[1], 100) # Auto XP for finishing
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)
                    st.rerun()

    with col_done:
        st.markdown("### 🟢 Completed")
<<<<<<< HEAD
        for t in [x for x in tasks if x[4] == 'completed']:
=======
        for t in [x for x in tasks if x[3] == 'completed']:
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)
            st.success(f"✅ {t[1]}")

# ===============================
# 📊 ANALYTICS
# ===============================
with tab_stats:
<<<<<<< HEAD
    st.subheader("📊 Productivity Deep Dive")
=======
    st.subheader("📊 Productivity Insights")
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)
    stats = analytics.get_study_stats()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Focus Time", f"{stats['total_focus_time']} mins")
<<<<<<< HEAD
    m2.metric("Efficiency Score", "85%")
    m3.metric("Study Streak", "5 Days")
    
    if stats['subject_distribution']:
        st.write("### Subject Breakdown")
        df_dist = pd.DataFrame(list(stats['subject_distribution'].items()), columns=["Subject", "Minutes"])
        st.bar_chart(df_dist.set_index("Subject"))
=======
    m2.metric("XP Gained", f"{xp} pts")
    m3.metric("OS Level", f"Lvl {level}")
    
    if stats['recent_logs']:
        st.write("### Recent Focus Sessions")
        df_logs = pd.DataFrame(stats['recent_logs'], columns=["ID", "Time", "Duration", "XP", "Subject"])
        st.table(df_logs.drop(columns=["ID"]))
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

# ===============================
# 🎙️ VOICE ASSISTANT
# ===============================
with tab_voice:
<<<<<<< HEAD
    st.subheader("🎙️ Voice Command Center")
    st.info("Simulated Voice Input: Say something like 'Schedule math at 4 PM'")
    
    v_query = st.text_input("Transcription (Speak now...)", key="voice_input")
    if st.button("Process Voice"):
        if v_query:
            result = voice_module.process_voice_command(v_query)
            st.write("🤖 AI Intent Detected:", result)
            # Handle result same as AI Assistant
        else:
            st.warning("No audio detected.")
=======
    st.subheader("🎙️ Voice Command")
    st.info("Since this is a web app, type your command below. It will be processed as voice input.")
    
    v_query = st.text_input("Speak/Type your command...", key="voice_input_field", placeholder="e.g. 'Schedule math at 5 PM'")
    if st.button("Process Command"):
        if v_query:
            result = voice_module.process_voice_command(v_query)
            st.write("🤖 AI Intent Detected:")
            st.json(result)
            # Add action handling here if needed or just show the result
        else:
            st.warning("Please enter a command.")
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

# ===============================
# 🧠 AI ASSISTANT
# ===============================
with tab_ai:
    st.subheader("🧠 Intelligence Hub")
<<<<<<< HEAD
    query = st.text_input("💬 Ask the OS (e.g., 'Suggest a study time for AI Ethics')")
    
    if st.button("Execute"):
        if query:
            result = process_query(query)
            st.json(result)
            
            action = result.get("action")
            
            if action == "create":
                title = result.get("title", "Event")
                start = result.get("start", datetime.datetime.utcnow().isoformat() + "Z")
                end = result.get("end", (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat() + "Z")
                
                # Predictive Conflict Resolution
                conflict, alt = scheduler_pro.resolve_conflict_pro(title, start, end)
                if conflict:
                    st.error(f"⚠️ Conflict with '{conflict}'")
                    st.info(f"👉 Suggesting Alternative: {alt[0]}")
                    if st.button("Accept Suggestion"):
                        g_create_event(title, alt[0], alt[1])
                        insert_event(title, alt[0], alt[1])
                        notification_engine.notify_event_creation(title, alt[0], alt[1])
                        st.success("Event scheduled successfully!")
                else:
                    g_create_event(title, start, end)
                    insert_event(title, start, end)
                    notification_engine.notify_event_creation(title, start, end)
                    st.success("Event added!")

            elif action == "recommend":
                subj = result.get("subject", "Study")
                s, e = scheduler_pro.suggest_optimal_study_time(subj)
                st.success(f"Best time for {subj}: **{s}**")
                if st.button("Schedule Now"):
                    g_create_event(f"Study: {subj}", s, e)
                    st.success("Optimized session booked!")

            elif action == "study_plan":
                subjects = result.get("subjects", ["All"])
                plan = generate_study_plan(", ".join(subjects))
                st.markdown(f"### 📋 Generated Plan\n{plan}")
                
            elif action == "task":
                insert_task(result.get("title"), result.get("due_date"))
                st.success("Task added to Kanban!")
=======
    query = st.text_input("💬 Ask the OS (e.g., 'Suggest a study time for Math')")
    
    if st.button("Execute AI Command"):
=======
            if st.form_submit_button("Add Task", use_container_width=True):
                if t_title:
                    insert_task(t_title, t_due.isoformat())
                    st.success("Task added!")
                    st.rerun()
                else:
                    st.warning("Please provide a title.")

    tasks = fetch_tasks()
    col_todo, col_progress, col_done = st.columns(3)

    status_styles = {
        'pending': {'color': '#E53E3E', 'bg': '#FFF5F5', 'label': '🔴 To Do'},
        'in_progress': {'color': '#D69E2E', 'bg': '#FFFFF0', 'label': '🟡 In Progress'},
        'completed': {'color': '#38A169', 'bg': '#F0FFF4', 'label': '🟢 Completed'},
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
                    if st.button("▶ Start", key=f"start_{t[0]}", use_container_width=True):
                        update_task_status(t[0], 'in_progress')
                        st.rerun()
                elif sk == 'in_progress':
                    if st.button("✓ Finish", key=f"finish_{t[0]}", use_container_width=True):
                        update_task_status(t[0], 'completed')
                        log_focus_session(60, t[1], 100)
                        st.rerun()

# ===============================
# ANALYTICS
# ===============================
with tab_stats:
    st.markdown('<p class="section-title">📊 Productivity Insights</p>', unsafe_allow_html=True)
    stats = analytics.get_study_stats()

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Focus Time", f"{stats['total_focus_time']} mins")
    m2.metric("XP Gained", f"{xp:,} pts")
    m3.metric("OS Level", f"Lvl {level}")

    if stats.get('subject_distribution'):
        st.markdown('<div class="glow-card" style="margin-top:1rem;">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">📊 Subject Breakdown</p>', unsafe_allow_html=True)
        df_dist = pd.DataFrame(
            list(stats['subject_distribution'].items()),
            columns=["Subject", "Minutes"]
        )
        st.bar_chart(df_dist.set_index("Subject"), color="#f5af19")
        st.markdown('</div>', unsafe_allow_html=True)

    if stats.get('recent_logs'):
        st.markdown('<div class="glow-card" style="margin-top:1rem;">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">⏱️ Recent Focus Sessions</p>', unsafe_allow_html=True)
        df_logs = pd.DataFrame(
            stats['recent_logs'],
            columns=["ID", "Time", "Duration", "XP", "Subject"]
        )
        st.dataframe(df_logs.drop(columns=["ID"]), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# AI AGENTS
# ===============================
with tab_agents:
    st.markdown('<p class="section-title">🤖 AI Agent Command Center</p>', unsafe_allow_html=True)

    agent_tabs = st.tabs(["📋 Planner", "🔄 Rescheduler", "📚 Readiness", "🧘 Wellness", "📈 Analytics"])

    with agent_tabs[0]:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown("Generate an optimized study schedule based on your workload.")
        subj_input = st.text_input("Subjects (comma-separated)", "Math, Physics, CS, History")
        hours_per_day = st.slider("Available study hours per day", 1, 12, 4)
        priority_subject = st.text_input("Priority subject (if any)", "Math")
        if st.button("Generate Study Plan", use_container_width=True):
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
                    f'<span style="font-size:1rem;">⚠️</span>'
                    f'<span><strong>{ms["title"]}</strong> — {ms["scheduled_time"]}</span></div>',
                    unsafe_allow_html=True)
            if st.button("Auto-Reschedule All", use_container_width=True):
                result = rescheduler_agent.auto_reschedule(missed_sessions)
                st.success(result)
                st.rerun()
        else:
            st.success("No missed sessions detected. You're on track!")
        st.markdown('</div>', unsafe_allow_html=True)

    with agent_tabs[2]:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown("Predict your exam readiness based on study data.")
        subjects = ["Math", "Physics", "Computer Science", "History"]
        for subj in subjects:
            score = readiness_agent.get_readiness_score(subj)
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f'<p style="margin-bottom:2px;"><strong>{subj}</strong></p>',
                            unsafe_allow_html=True)
                st.progress(score / 100)
            with col_b:
                st.metric("Score", f"{score:.0f}%")
        summary = readiness_agent.get_readiness_summary()
        st.info(f"**Overall Readiness:** {summary['avg_score']:.0f}% — {summary['recommendation']}")
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
                st.warning(f"⚠️ {alert}")
        if status['recommendation']:
            st.success(f"💡 {status['recommendation']}")
        if status['energy_level'] < 40:
            st.error("🚨 Burnout risk detected! Take a longer break or stop for today.")

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
            st.markdown('<p class="section-title">📈 Study Trends</p>', unsafe_allow_html=True)
            df_t = pd.DataFrame(report['trends'])
            if not df_t.empty and 'date' in df_t.columns:
                st.line_chart(df_t.set_index('date'), color="#f5af19")
        if report.get('recommendations'):
            st.markdown('<p class="section-title">💡 Recommendations</p>', unsafe_allow_html=True)
            for rec in report['recommendations']:
                st.info(f"💡 {rec}")
        st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# VOICE
# ===============================
with tab_voice:
    st.markdown('<div class="glow-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🎙️ Voice Command Center</p>', unsafe_allow_html=True)
    st.info("Type your command below. It will be processed as voice input.")
    v_query = st.text_input("Speak/Type your command...",
                           key="voice_input_field",
                           placeholder="e.g. 'Schedule math at 5 PM'")
    if st.button("Process Command", use_container_width=True):
        if v_query:
            result = voice_module.process_voice_command(v_query)
            st.markdown('<p style="font-weight:600; margin-top:12px;">🤖 AI Intent Detected:</p>',
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
    st.markdown('<p class="section-title">🧠 Intelligence Hub</p>', unsafe_allow_html=True)
    query = st.text_input("💬 Ask the OS (e.g., 'Suggest a study time for Math')")
    if st.button("Execute AI Command", use_container_width=True):
>>>>>>> 118f928 (Final Submission)
        if query:
            with st.spinner("AI is thinking..."):
                try:
                    result = process_query(query)
<<<<<<< HEAD
                    st.write("🤖 AI Decision:")
                    st.json(result)
                    
                    action = result.get("action")
                    
=======
                    st.markdown('<p style="font-weight:600; margin-top:12px;">🤖 AI Decision:</p>',
                               unsafe_allow_html=True)
                    st.json(result)

                    action = result.get("action")

>>>>>>> 118f928 (Final Submission)
                    if action == "create":
                        title = result.get("title", "Event")
                        start = result.get("start", datetime.datetime.utcnow().isoformat() + "Z")
                        end = result.get("end", (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat() + "Z")
<<<<<<< HEAD
                        
                        # Conflict Resolution
=======
>>>>>>> 118f928 (Final Submission)
                        try:
                            conflict, alt = scheduler_pro.resolve_conflict_pro(title, start, end)
                            if conflict:
                                st.error(f"⚠️ Conflict with '{conflict}'")
                                if alt and alt[0]:
                                    st.info(f"👉 Suggesting Alternative: {alt[0]}")
                                    if st.button("Accept Suggestion"):
                                        insert_event(title, alt[0], alt[1])
<<<<<<< HEAD
                                        try: g_create_event(title, alt[0], alt[1]) 
=======
                                        try: g_create_event(title, alt[0], alt[1])
>>>>>>> 118f928 (Final Submission)
                                        except: pass
                                        st.success("Scheduled alternative!")
                            else:
                                insert_event(title, start, end)
                                try: g_create_event(title, start, end)
                                except: pass
                                st.success("Event added!")
                        except:
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
                                    except: pass
                                    st.success("Optimized session booked!")
                        except:
                            st.info("Could not calculate optimal time. Try manual scheduling.")

                    elif action == "study_plan":
                        subjects = result.get("subjects", ["All"])
                        plan = generate_study_plan(", ".join(subjects))
                        st.markdown(f"### 📋 Generated Plan\n{plan}")
<<<<<<< HEAD
                        
                    elif action == "task":
                        insert_task(result.get("title", "New Task"), result.get("due_date", datetime.date.today().isoformat()))
                        st.success("Task added to Kanban!")
                    
                    elif action == "focus":
                        st.info(f"Starting focus session for {result.get('subject', 'Study')} ({result.get('duration', 25)} mins)")
                        # In a real app we might redirect to dashboard or show a timer
                        
                    elif action == "stats":
                        st.info("View your stats in the Analytics tab!")
                        
=======

                    elif action == "task":
                        insert_task(result.get("title", "New Task"),
                                   result.get("due_date", datetime.date.today().isoformat()))
                        st.success("Task added to Kanban!")

                    elif action == "focus":
                        st.info(f"Starting focus session for {result.get('subject', 'Study')} "
                               f"({result.get('duration', 25)} mins)")

                    elif action == "stats":
                        st.info("View your stats in the Analytics tab!")

>>>>>>> 118f928 (Final Submission)
                    elif action == "unknown":
                        st.warning(result.get("response", "I'm not sure how to help with that."))
                except Exception as e:
                    st.error(f"AI Error: {e}")
<<<<<<< HEAD
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

# ===============================
# ⚙️ SETTINGS
# ===============================
with tab_settings:
    st.subheader("⚙️ OS Configuration")
    new_name = st.text_input("User Name", value=user_name)
    new_email = st.text_input("Notification Email", value=get_profile_value("user_email", ""))
    
    if st.button("Save Profile"):
        set_profile_value("user_name", new_name)
        set_profile_value("user_email", new_email)
        st.success("Profile Updated!")
=======
        else:
            st.warning("Please enter a query.")
    st.markdown('</div>', unsafe_allow_html=True)

# ===============================
# SETTINGS
# ===============================
with tab_settings:
    st.markdown('<p class="section-title">⚙️ OS Configuration</p>', unsafe_allow_html=True)

    tab_settings_col1, tab_settings_col2 = st.columns(2)
    with tab_settings_col1:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        new_name = st.text_input("User Name", value=user_name)
        new_email = st.text_input("Notification Email", value=get_profile_value("user_email", ""))
        if st.button("Save Profile", use_container_width=True):
            set_profile_value("user_name", new_name)
            set_profile_value("user_email", new_email)
            st.success("Profile Updated!")
            st.rerun()

        st.divider()
        if st.button("📧 Test Email Notification", use_container_width=True):
            email_to = get_profile_value("user_email", "ullasnullas204@gmail.com")
            if email_to:
                ok, msg = notify.send_alert("Test from Smart OS", "This is a test notification. If you see this, email is working!")
                if ok:
                    st.success(f"✅ Test email sent to {email_to}")
                else:
                    st.error(f"❌ Email failed: {msg}")
            else:
                st.warning("Set an email in the field above first.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_settings_col2:
        st.markdown('<div class="glow-card">', unsafe_allow_html=True)
        st.markdown('<p style="font-weight:600; margin-bottom:8px;">🏆 Achievements</p>',
                   unsafe_allow_html=True)
        achievements = fetch_achievements()
        if achievements:
            for a in achievements:
                unlocked = a[2] if len(a) > 2 else True
                icon = "✅" if unlocked else "🔒"
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
>>>>>>> 118f928 (Final Submission)

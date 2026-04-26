import streamlit as st
import datetime
import pandas as pd
import time

# Existing imports
from ai_agent import process_query
from models import (
    insert_event, fetch_events, insert_task, fetch_tasks, update_task_status,
    log_focus_session, fetch_focus_logs, get_profile_value, set_profile_value,
    fetch_achievements, unlock_achievement
)
from streamlit_calendar import calendar
from study_planner import generate_study_plan
from google_calendar import (
    create_event as g_create_event,
    get_events as g_get_events,
    check_conflict
)
from email_utils import send_email

# New module imports
import analytics
import gamification
import scheduler_pro
import lms_sync
import voice_module
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
level = gamification.get_user_level()
xp = gamification.calculate_xp()
progress = gamification.get_progress_to_next_level()

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
    with st.spinner("Syncing with LMS..."):
        try:
            new_count = lms_sync.sync_assignments_to_db()
            st.sidebar.success(f"Fetched {new_count} new tasks!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"LMS Sync Failed: {e}")
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
        
    # Load Local DB Events
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
                if e_title:
                    try:
                        start_dt = datetime.datetime.combine(e_date, e_start_t).isoformat()
                        end_dt = datetime.datetime.combine(e_date, e_end_t).isoformat()
                        insert_event(e_title, start_dt, end_dt)
                        st.success("Event saved locally!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to save event: {e}")
                else:
                    st.warning("Please provide a title.")
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)

# ===============================
# 📋 KANBAN TASKS
# ===============================
with tab_tasks:
    st.subheader("📋 Academic Kanban Board")
<<<<<<< HEAD
=======
    
    with st.expander("➕ Quick Add Task"):
        with st.form("add_task"):
            t_title = st.text_input("Task Title")
            t_due = st.date_input("Due Date")
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
        if query:
            with st.spinner("AI is thinking..."):
                try:
                    result = process_query(query)
                    st.write("🤖 AI Decision:")
                    st.json(result)
                    
                    action = result.get("action")
                    
                    if action == "create":
                        title = result.get("title", "Event")
                        start = result.get("start", datetime.datetime.utcnow().isoformat() + "Z")
                        end = result.get("end", (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat() + "Z")
                        
                        # Conflict Resolution
                        try:
                            conflict, alt = scheduler_pro.resolve_conflict_pro(title, start, end)
                            if conflict:
                                st.error(f"⚠️ Conflict with '{conflict}'")
                                if alt and alt[0]:
                                    st.info(f"👉 Suggesting Alternative: {alt[0]}")
                                    if st.button("Accept Suggestion"):
                                        insert_event(title, alt[0], alt[1])
                                        try: g_create_event(title, alt[0], alt[1]) 
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
                        
                    elif action == "task":
                        insert_task(result.get("title", "New Task"), result.get("due_date", datetime.date.today().isoformat()))
                        st.success("Task added to Kanban!")
                    
                    elif action == "focus":
                        st.info(f"Starting focus session for {result.get('subject', 'Study')} ({result.get('duration', 25)} mins)")
                        # In a real app we might redirect to dashboard or show a timer
                        
                    elif action == "stats":
                        st.info("View your stats in the Analytics tab!")
                        
                    elif action == "unknown":
                        st.warning(result.get("response", "I'm not sure how to help with that."))
                except Exception as e:
                    st.error(f"AI Error: {e}")
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

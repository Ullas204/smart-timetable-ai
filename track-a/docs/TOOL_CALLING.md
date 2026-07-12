# Tool Calling Architecture

## Overview

Smart Academic OS has **37 LangChain tools** across **14 domains**, all registered as `@tool`-decorated functions and bound to the LLM via LangChain's function calling.

## Tool Registry

| # | Group | Tools | Count |
|---|-------|-------|-------|
| 1 | Event Management | create_event, list_events, find_free_slots, resolve_event_conflict, suggest_study_time, sync_google_calendar | 6 |
| 2 | Task Management | create_task, list_tasks, update_task | 3 |
| 3 | Study Planning | generate_study_plan, get_workload | 2 |
| 4 | Rescheduling | detect_missed_sessions, auto_reschedule | 2 |
| 5 | Exam Readiness | check_exam_readiness, get_readiness_overview | 2 |
| 6 | Wellness | get_wellness_status, get_weekly_wellness_trend | 2 |
| 7 | Analytics | get_productivity_analytics, get_task_completion_rate, get_study_streak, get_focus_stats | 4 |
| 8 | Focus/Pomodoro | start_focus_session, log_completed_focus, get_gamification_status | 3 |
| 9 | Notifications | send_email_notification, send_event_notification | 2 |
| 10 | Attendance | mark_attendance, view_attendance | 2 |
| 11 | Profile | get_user_profile, update_user_profile | 2 |
| 12 | Subjects/Exams | add_subject, list_subjects, add_exam, list_exams | 4 |
| 13 | Voice | process_voice_command | 1 |
| 14 | Knowledge Base | search_knowledge_base, get_knowledge_base_status | 2 |
| | **Total** | | **37** |

## Tool Execution Flow

```
1. LLM receives user query + system prompt + chat history
2. LLM generates response with tool_calls
3. AgentExecutor iterates over tool_calls:
   a. Find tool by name in registry
   b. tool.invoke(args) → result (JSON string)
   c. Log to in-memory execution log (max 100 entries)
   d. Create ToolMessage(result)
4. All ToolMessages sent back to LLM
5. LLM produces final natural-language summary
6. AgentResponse returned with:
   - message: final summary
   - tools_used: list of ToolExecution records
   - raw_action: backward-compatible dict for app.py dispatcher
   - is_tool_call: True
```

## Tool Design Pattern

Every tool follows this pattern:
```python
@tool
def tool_name(param: type) -> str:
    """Docstring used by LLM for tool selection."""
    try:
        # Execute business logic
        result = do_something(param)
        return json.dumps({"success": True, ...})
    except Exception as e:
        logger.error("tool_name failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})
```

## Tool-to-Backend Mapping

| Tool | Backend Module |
|------|---------------|
| create_event, list_events | db.py (events table) |
| create_task, list_tasks, update_task | db.py (tasks table) |
| generate_study_plan | study_planner.py → Gemini |
| detect_missed_sessions, auto_reschedule | agents/rescheduler_agent.py |
| check_exam_readiness | agents/readiness_agent.py |
| get_wellness_status | agents/wellness_agent.py |
| get_productivity_analytics, etc. | agents/analytics_agent.py + analytics.py |
| start_focus_session, log_completed_focus | models.py → db.py (focus_logs) |
| send_email_notification | email_utils.py → SMTP |
| mark_attendance, view_attendance | db.py (attendance table) |
| get_user_profile, update_user_profile | db.py (user_profile table) |
| add_subject, list_subjects, etc. | db.py (subjects, exams tables) |
| process_voice_command | ai_agent.py (fallback_nlp) |
| search_knowledge_base | core/rag/pipeline.py → FAISS |
| get_knowledge_base_status | core/rag/pipeline.py |

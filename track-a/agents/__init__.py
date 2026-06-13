from agents import planner_agent, rescheduler_agent, readiness_agent, wellness_agent, analytics_agent

def get_all_agent_reports():
    return {
        "planner": planner_agent,
        "rescheduler": rescheduler_agent.detect_missed_sessions(),
        "readiness": readiness_agent.get_readiness_summary(),
        "wellness": wellness_agent.get_wellness_status(),
        "analytics": analytics_agent.generate_report(),
    }

def run_scheduled_agents():
    missed = rescheduler_agent.detect_missed_sessions()
    if missed:
        rescheduler_agent.auto_reschedule(missed)
    wellness_agent.get_wellness_status()

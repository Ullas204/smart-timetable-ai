from models import fetch_focus_logs, fetch_events
import pandas as pd

def get_study_stats():
    logs = fetch_focus_logs()
    if not logs:
        return {"total_focus_time": 0, "subject_distribution": {}, "recent_logs": []}
    
    df = pd.DataFrame(logs, columns=["id", "start_time", "duration", "subject", "points"])
    total_time = df["duration"].sum()
    subject_dist = df.groupby("subject")["duration"].sum().to_dict()
    
    return {
        "total_focus_time": total_time,
        "subject_distribution": subject_dist,
        "recent_logs": logs[-5:]
    }

def get_event_stats():
    events = fetch_events()
    return {"total_events": len(events)}

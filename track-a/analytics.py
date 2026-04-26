from models import fetch_focus_logs, fetch_events
import pandas as pd

<<<<<<< HEAD
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

=======
import pandas as pd
from models import fetch_focus_logs


def get_study_stats():
    logs = fetch_focus_logs()

    if not logs:
        return {
            "total_focus_time": 0,
            "subject_distribution": {},
            "recent_logs": []
        }

    # ✅ FIX: Normalize rows to expected 5 columns
    cleaned_logs = []

    for log in logs:
        # Take only first 5 columns safely
        row = list(log[:5])

        # Ensure length = 5
        while len(row) < 5:
            row.append(None)

        cleaned_logs.append(row)

    # ✅ Now safe for pandas
    df = pd.DataFrame(
        cleaned_logs,
        columns=["id", "start_time", "duration", "points", "subject"]
    )

    # Safe conversions
    df["duration"] = pd.to_numeric(df["duration"], errors='coerce').fillna(0)
    df["points"] = pd.to_numeric(df["points"], errors='coerce').fillna(0)

    # Analytics
    total_focus_time = int(df["duration"].sum())

    subject_distribution = (
        df.groupby("subject")["duration"].sum().to_dict()
        if "subject" in df else {}
    )

    recent_logs = df.tail(5).to_dict(orient="records")

    return {
        "total_focus_time": total_focus_time,
        "subject_distribution": subject_distribution,
        "recent_logs": recent_logs
    }
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)
def get_event_stats():
    events = fetch_events()
    return {"total_events": len(events)}

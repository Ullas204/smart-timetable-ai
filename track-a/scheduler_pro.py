from google_calendar import get_events, check_conflict
import datetime

def find_free_slots(duration_hours=1, days_ahead=3):
<<<<<<< HEAD
    events = get_events()
=======
    try:
        events = get_events()
    except Exception as e:
        print(f"Google Calendar access failed: {e}")
        events = []
    
>>>>>>> 6b82fad (🔥 Fixed DB issues, analytics, gamification, and focus tracking)
    now = datetime.datetime.utcnow()
    # Simple algorithm to find gaps
    # For simulation, we'll just check hours in the day
    free_slots = []
    
    current_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    
    for _ in range(24 * days_ahead):
        start = current_time.isoformat() + "Z"
        end = (current_time + datetime.timedelta(hours=duration_hours)).isoformat() + "Z"
        
        conflict, _ = check_conflict(start, end)
        if not conflict:
            free_slots.append((start, end))
            if len(free_slots) >= 5:
                break
        
        current_time += datetime.timedelta(hours=1)
        
    return free_slots

def suggest_optimal_study_time(subject):
    # In a real app, this would use ML on focus_logs
    # For now, it suggests the first available slot in "productive hours" (9 AM - 9 PM)
    slots = find_free_slots(duration_hours=2)
    for s, e in slots:
        dt = datetime.datetime.fromisoformat(s.replace("Z", ""))
        if 9 <= dt.hour <= 21:
            return s, e
    return slots[0] if slots else (None, None)

def resolve_conflict_pro(title, start, end):
    conflict, existing = check_conflict(start, end)
    if not conflict:
        return None, None
        
    # Find next best slot
    alt_start, alt_end = suggest_optimal_study_time(title)
    return existing, (alt_start, alt_end)

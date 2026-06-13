import datetime

def fetch_lms_assignments():
    """Simulates fetching assignments from Canvas/Moodle"""
    # In reality, you'd use canvasapi or a direct API request
    now = datetime.datetime.now()
    assignments = [
        {"title": "Math Quiz 1", "due_date": (now + datetime.timedelta(days=2)).isoformat(), "subject": "Math"},
        {"title": "CS Project Alpha", "due_date": (now + datetime.timedelta(days=5)).isoformat(), "subject": "CS"},
        {"title": "AI Ethics Paper", "due_date": (now + datetime.timedelta(days=7)).isoformat(), "subject": "AI"},
    ]
    return assignments

def sync_assignments_to_db():
    from models import insert_task, fetch_tasks
    existing_tasks = [t[1] for t in fetch_tasks()]
    new_assignments = fetch_lms_assignments()
    
    count = 0
    for assign in new_assignments:
        if assign["title"] not in existing_tasks:
            insert_task(assign["title"], assign["due_date"])
            count += 1
            
    return count

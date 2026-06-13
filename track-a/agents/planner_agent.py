import datetime
from models import fetch_tasks, fetch_events, fetch_focus_logs

def get_workload_distribution(subjects, hours_per_day):
    tasks = fetch_tasks()
    focus_logs = fetch_focus_logs()
    workload = {}

    for subject in subjects:
        task_count = sum(1 for t in tasks if subject.lower() in t[1].lower())
        focus_minutes = 0
        for log in focus_logs:
            try:
                if len(log) >= 4 and subject.lower() in str(log[3]).lower():
                    focus_minutes += int(log[2]) if log[2] else 0
            except (ValueError, IndexError):
                continue
        workload[subject] = {
            "pending_tasks": task_count,
            "focus_minutes": focus_minutes,
            "priority_weight": 0
        }

    return workload


def generate_plan(subjects, hours_per_day=4, priority_subject=None):
    workload = get_workload_distribution(subjects, hours_per_day)

    if priority_subject and priority_subject in workload:
        workload[priority_subject]["priority_weight"] = 2

    total_weight = sum(1 + w["priority_weight"] + w["pending_tasks"] * 0.5
                      for w in workload.values())
    if total_weight == 0:
        return "No workload data available. Add some tasks first!"

    lines = [f"### 📚 Optimized Study Plan", f"**Daily hours:** {hours_per_day}h", ""]

    for i in range(7):
        day_name = (datetime.date.today() + datetime.timedelta(days=i)).strftime("%A")
        lines.append(f"**{day_name}**")

        allocated = {}
        remaining = hours_per_day
        sorted_subjects = sorted(
            workload.items(),
            key=lambda x: x[1]["priority_weight"] + x[1]["pending_tasks"] * 0.5,
            reverse=True
        )

        for subject, data in sorted_subjects:
            weight = 1 + data["priority_weight"] + data["pending_tasks"] * 0.5
            hours = max(0.5, round((weight / total_weight) * hours_per_day, 1))
            hours = min(hours, remaining)
            if hours >= 0.5:
                allocated[subject] = hours
                remaining -= hours

        if allocated:
            for subject, hours in allocated.items():
                lines.append(f"  - **{subject}**: {hours}h")
        else:
            lines.append("  - *Free / Review Day*")
        lines.append("")

    lines.append("---")
    lines.append("💡 **Tips:**")
    lines.append("- Prioritize weak subjects early in the day")
    lines.append("- Take 5-10 min breaks between sessions")
    lines.append("- Review completed topics weekly")

    return "\n".join(lines)

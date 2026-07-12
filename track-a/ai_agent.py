"""
Legacy AI Agent — keyword NLP + Gemini fallback.
Used as a safety net when the LangChain agent is unavailable.
"""
import os
import json
import re
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE_DIR, '.env'))

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

try:
    import google.generativeai as genai
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        _model = genai.GenerativeModel("gemini-2.0-flash")
    else:
        _model = None
        logger.warning("GEMINI_API_KEY not found. AI Assistant will use fallback mode.")
except ImportError:
    _model = None


def fallback_nlp(query):
    query = query.lower()
    now = datetime.now()

    kb_keywords = [
        "what", "explain", "describe", "define", "list", "summarize",
        "tell me about", "how does", "how do", "why", "when", "where",
        "who", "which", "note", "notes", "syllabus", "chapter", "unit",
        "topic", "topics", "formula", "example", "definition", "formula",
        "regulation", "rule", "rules", "syllabi", "paper", "papers",
    ]
    is_kb_query = any(kw in query for kw in kb_keywords)

    if is_kb_query:
        try:
            from core.rag import get_rag_pipeline
            pipeline = get_rag_pipeline()
            result = pipeline.search(query, k=4)
            if result.get("found") and result.get("context"):
                sources = result.get("sources", [])
                source_names = list(set(s["filename"] for s in sources))
                source_str = ", ".join(source_names) if source_names else "uploaded documents"
                answer = (
                    f"**From your Knowledge Base ({source_str}):**\n\n"
                    f"{result['context'][:2000]}"
                )
                return {
                    "action": "conversation",
                    "response": answer,
                }
        except Exception as e:
            logger.debug("KB fallback search failed: %s", e)

    if "schedule" in query or "class" in query or "meeting" in query:
        title = query.replace("schedule", "").replace("class", "").replace("meeting", "").strip()
        start = (now + timedelta(hours=1)).isoformat() + "Z"
        end = (now + timedelta(hours=2)).isoformat() + "Z"
        return {"action": "create", "title": title or "New Event", "start": start, "end": end}

    if "task" in query or "todo" in query or "assignment" in query:
        title = query.replace("task", "").replace("todo", "").replace("assignment", "").replace("add", "").strip()
        due = (now + timedelta(days=1)).isoformat()
        return {"action": "task", "title": title or "New Task", "due_date": due}

    if "study" in query and "plan" in query:
        return {"action": "study_plan", "subjects": ["Math", "Physics", "CS"]}

    if "focus" in query or "pomodoro" in query:
        return {"action": "focus", "subject": "Study", "duration": 25}

    if "stats" in query or "analytics" in query:
        return {"action": "stats"}

    if "recommend" in query or "best time" in query or "suggest" in query or "study time" in query:
        subjects = ["Math", "Physics", "Computer Science", "History"]
        subject = "Study"
        for s in subjects:
            if s.lower() in query:
                subject = s
                break
        return {"action": "recommend", "subject": subject}

    known_subjects = ["math", "physics", "computer science", "history", "cs", "ai", "english"]
    for s in known_subjects:
        if s in query and ("study" in query or "schedule" in query or "plan" in query):
            return {"action": "study_plan", "subjects": [s.title()]}

    return {"action": "unknown", "response": "I'm in fallback mode. Try 'schedule math' or 'add task homework'."}


def extract_json(text):
    """Extract JSON from messy AI output."""
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, re.error):
        pass
    return None


def process_query(query):
    now = datetime.now().isoformat()

    if _model is None:
        return fallback_nlp(query)

    prompt = f"""
    You are a Smart Academic OS Assistant.
    Current Time: {now}

    Convert the user input into JSON ONLY.

    Possible Actions:
    - "create": Schedule an event/class (requires title, start, end)
    - "find": List upcoming events
    - "task": Add a new assignment or task (requires title, due_date)
    - "study_plan": Generate a study plan for subjects (requires subjects)
    - "focus": Start a focus session (requires subject, duration)
    - "stats": Show productivity analytics
    - "recommend": Suggest optimal study time

    Input: "{query}"

    Output format:
    {{
        "action": "string",
        "title": "string",
        "start": "string",
        "end": "string",
        "due_date": "string",
        "subjects": ["list"],
        "subject": "string",
        "duration": "int"
    }}

    RULES:
    - Output ONLY JSON
    - No explanation
    - No extra text
    - Use ISO 8601 for dates if possible
    """

    try:
        response = _model.generate_content(prompt)
        text = response.text.strip()
        data = extract_json(text)
        if data:
            return data
    except Exception as e:
        logger.warning("AI Error (switching to fallback): %s", e)

    return fallback_nlp(query)

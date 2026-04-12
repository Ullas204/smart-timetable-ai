import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import re
from datetime import datetime

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def extract_json(text):
    """Extract JSON from messy AI output"""
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None


def process_query(query):
    now = datetime.now().isoformat()
    
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
        response = model.generate_content(prompt)
        text = response.text.strip()
        data = extract_json(text)
        if data:
            return data
    except Exception as e:
        print(f"AI Error: {e}")

    return {"action": "unknown"}

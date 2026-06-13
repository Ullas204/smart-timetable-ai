import google.generativeai as genai
import os
from dotenv import load_dotenv

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE_DIR, '.env'))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_study_plan(subjects):
    prompt = f"""
    Create a weekly study timetable for:

    Subjects: {subjects}

    Include:
    - Daily schedule
    - Breaks
    - Balanced workload

    Keep it simple.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Study Planner AI Error: {e}")
        return f"""
        ### 📚 Standard Study Plan for {subjects}
        - **Monday - Friday**:
          - 09:00 - 11:00: Deep Work on {subjects}
          - 11:00 - 11:30: Break
          - 11:30 - 13:00: Review & Practice
        - **Weekend**:
          - 10:00 - 12:00: Weekly Recap
        """

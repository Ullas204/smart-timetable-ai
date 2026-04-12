import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


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

    response = model.generate_content(prompt)

    return response.text
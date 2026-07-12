"""
Study Planner — generates AI-powered weekly study timetables.
"""
import os
import logging

logger = logging.getLogger(__name__)

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import google.generativeai as genai
    from dotenv import load_dotenv

    load_dotenv(os.path.join(_BASE_DIR, '.env'))

    _key = os.getenv("GEMINI_API_KEY")
    if _key:
        genai.configure(api_key=_key)
        _model = genai.GenerativeModel("gemini-2.0-flash")
    else:
        _model = None
except ImportError:
    _model = None


def generate_study_plan(subjects):
    if _model is None:
        return _fallback_plan(subjects)

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
        response = _model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.warning("Study Planner AI Error: %s", e)
        return _fallback_plan(subjects)


def _fallback_plan(subjects):
    return f"""
    ### Standard Study Plan for {subjects}
    - **Monday - Friday**:
      - 09:00 - 11:00: Deep Work on {subjects}
      - 11:00 - 11:30: Break
      - 11:30 - 13:00: Review & Practice
    - **Weekend**:
      - 10:00 - 12:00: Weekly Recap
    """

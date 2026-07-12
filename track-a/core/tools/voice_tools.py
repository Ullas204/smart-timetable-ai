"""
LangChain tools for Voice Module.

Processes voice transcriptions through the same AI pipeline as text.
"""

import json
import logging

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def process_voice_command(transcription: str) -> str:
    """Process a voice command transcribed from speech. Use this when the user provides a voice input that needs to be interpreted and acted upon.

    Args:
        transcription: The transcribed text from voice input (e.g., "Schedule math at 5 PM").
    """
    try:
        if not transcription or not transcription.strip():
            return json.dumps({"success": False, "error": "No voice data provided."})

        from ai_agent import fallback_nlp
        result = fallback_nlp(transcription.strip())
        logger.info("Voice command processed: '%s' -> action=%s", transcription, result.get("action"))
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        logger.error("process_voice_command failed: %s", e)
        return json.dumps({"success": False, "error": str(e)})


VOICE_TOOLS = [process_voice_command]

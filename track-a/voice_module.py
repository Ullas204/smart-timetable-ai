"""
Voice Module - Routes voice commands through the LangChain Agent.

Phase 2: Now uses the AcademicAgent with tool binding for intelligent
voice command processing instead of the legacy keyword NLP.
"""

import logging

logger = logging.getLogger(__name__)


def process_voice_command(transcription):
    """
    Process a voice command through the LangChain agent with tool binding.

    Takes transcription text and routes it through the AcademicAgent,
    which automatically selects the appropriate tool based on intent.

    Falls back to the original ai_agent.process_query if LangChain is
    unavailable.
    """
    if not transcription:
        return {"action": "unknown", "error": "No voice data"}

    # Try LangChain agent first (Phase 2: Tool Binding)
    try:
        from core.agent_executor import AcademicAgent
        from core.memory import ChatMemory

        agent = AcademicAgent()
        response = agent.execute(transcription, memory=None)

        logger.info("Voice command processed via LangChain agent: action=%s", response.action.value)
        return response.raw_action
    except Exception as e:
        logger.warning("LangChain agent unavailable for voice, falling back: %s", e)

    # Fallback to original keyword NLP
    try:
        from ai_agent import process_query
        result = process_query(transcription)
        return result
    except Exception as e:
        logger.error("Voice processing failed completely: %s", e)
        return {"action": "unknown", "error": str(e)}

from ai_agent import process_query

def process_voice_command(transcription):
    """
    Simulates speech processing. In Streamlit, we get text from audio.
    This takes transcription and passes it to the AI agent.
    """
    if not transcription:
        return {"action": "unknown", "error": "No voice data"}
        
    result = process_query(transcription)
    return result

import whisper
from config import WHISPER_MODEL

def transcribe_audio(file_path, model, language=None):
    """Transcribe audio from a file path using the Whisper model."""
    try:
        transcribe_kwargs = {'language': language} if language else {}
        result = model.transcribe(file_path, **transcribe_kwargs)
        return result["text"]
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
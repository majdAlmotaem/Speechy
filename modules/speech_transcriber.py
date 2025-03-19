import whisper
from config import WHISPER_MODEL

def transcribe_audio(audio_data, model, language=None, is_file=True):
    try:
        transcribe_kwargs = {'language': language} if language else {}
        if is_file:
            result = model.transcribe(audio_data, **transcribe_kwargs)
        else:
            # Assuming audio_data is a NumPy array
            result = model.transcribe(audio_data, **transcribe_kwargs)
        return result["text"]
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
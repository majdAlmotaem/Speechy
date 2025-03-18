import whisper
from config import WHISPER_MODEL

def load_whisper_model(model_size=WHISPER_MODEL):
    """
    Load Whisper speech recognition model
    
    Args:
        model_size (str): Size of the Whisper model
    
    Returns:
        whisper model object
    """
    return whisper.load_model(model_size)

def transcribe_audio(audio_file, model=None, language=None):
    """
    Transcribe audio file to text
    
    Args:
        audio_file (str): Path to audio file
        model (whisper model, optional): Pre-loaded model
        language (str, optional): Language to force transcription
    
    Returns:
        str: Transcribed text
    """
    try:
        if model is None:
            model = load_whisper_model()
        
        # Transcription options
        transcribe_kwargs = {}
        if language:
            transcribe_kwargs['language'] = language
        
        result = model.transcribe(audio_file, **transcribe_kwargs)
        return result["text"]
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""

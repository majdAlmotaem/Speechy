import logging

SAMPLE_RATE = 16000
WHISPER_MODEL = "base"  # Default model, can be overridden by GUI selection
LOG_LEVEL = logging.INFO
SILENCE_THRESHOLD = 0.05  # Increased to filter out faint noise

# Model options that can be selected in the GUI
MODEL_OPTIONS = {
    "tiny": {"name": "Tiny (Fastest)", "description": "Fastest model, lower accuracy", "size_mb": 75},
    "base": {"name": "Base (Fast)", "description": "Good balance of speed and accuracy", "size_mb": 150},
    "small": {"name": "Small (Balanced)", "description": "Better accuracy, moderate speed", "size_mb": 500},
    "medium": {"name": "Medium (Accurate)", "description": "High accuracy, slower processing", "size_mb": 1500}
}

# Default language (can be overridden by GUI)
DEFAULT_LANGUAGE = "en"

# Supported languages with their display names
SUPPORTED_LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German", "it": "Italian",
    "pt": "Portuguese", "ru": "Russian", "zh": "Chinese", "ja": "Japanese", "ko": "Korean",
    "ar": "Arabic", None: "Auto Detect"
}

# Transcription prompt to bias Whisper toward expected commands
TRANSCRIPTION_PROMPT = (
    "Voice commands only: open notepad, scroll down, click, start typing, stop typing, "
    "exit, comma, new line"
)


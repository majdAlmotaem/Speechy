import sounddevice as sd
import wavio
from config import RECORDING_DURATION, SAMPLE_RATE, AUDIO_FILE

def audio_recorder(duration=RECORDING_DURATION, fs=SAMPLE_RATE):
    """
    Record audio and save to a file
    
    Args:
        duration (int): Recording duration in seconds
        fs (int): Sampling frequency
    
    Returns:
        str: Path to the recorded audio file
    """
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    print("Finished recording.")
    wavio.write(AUDIO_FILE, audio, fs, sampwidth=2)
    return AUDIO_FILE

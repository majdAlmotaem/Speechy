import whisper
import sounddevice as sd
import numpy as np
import threading
import webrtcvad
from config import WHISPER_MODEL, SAMPLE_RATE, SILENCE_THRESHOLD

class LiveTranscriber:
    def __init__(self, model_size=WHISPER_MODEL):
        self.model = whisper.load_model(model_size)
        self.sample_rate = SAMPLE_RATE
        self.vad = webrtcvad.Vad(1)
        self.is_speaking = False
        self.running = True

    def detect_speech(self, audio_chunk):
        audio_int16 = (audio_chunk * 32768).astype(np.int16).tobytes()
        return self.vad.is_speech(audio_int16, sample_rate=self.sample_rate)

    def transcribe_chunk(self, audio_chunk):
        try:
            audio_data = audio_chunk.flatten().astype(np.float32)
            result = self.model.transcribe(audio_data, language='en')
            return result['text']
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def live_transcribe(self, callback=print):
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            rms = np.sqrt(np.mean(indata**2))
            if self.detect_speech(indata):
                if not self.is_speaking:
                    self.is_speaking = True
                    print("Speech started")
                if not hasattr(self, 'audio_buffer'):
                    self.audio_buffer = indata.copy()
                else:
                    max_buffer_size = self.sample_rate * 5
                    if len(self.audio_buffer) < max_buffer_size:
                        self.audio_buffer = np.vstack((self.audio_buffer, indata))
            else:
                if self.is_speaking and hasattr(self, 'audio_buffer'):
                    audio_to_process = self.audio_buffer.copy()
                    threading.Thread(
                        target=self._process_audio,
                        args=(audio_to_process, callback),
                        daemon=True
                    ).start()
                    del self.audio_buffer
                    self.is_speaking = False

        def _restart_stream():
            try:
                stream = sd.InputStream(
                    callback=audio_callback,
                    channels=1,
                    samplerate=self.sample_rate,
                    dtype='float32',
                    blocksize=int(self.sample_rate * 0.02),  # 20ms for VAD
                    latency='high'
                )
                with stream:
                    print("Audio stream started")
                    while self.running:
                        sd.sleep(1000)
            except Exception as e:
                print(f"Stream error: {e}")
                if self.running:
                    print("Attempting to restart stream...")
                    _restart_stream()

        self.running = True
        streaming_thread = threading.Thread(target=_restart_stream, daemon=True)
        streaming_thread.start()
        try:
            while self.running:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("Stopping transcription...")
            self.running = False

    def _process_audio(self, audio_chunk, callback):
        transcription = self.transcribe_chunk(audio_chunk)
        print(f"Full transcription: '{transcription}'")
        if transcription.strip():
            callback(transcription)

    def stop(self):
        self.running = False
import whisper
import sounddevice as sd
import numpy as np
import threading
import webrtcvad
import torch
import queue
from config import WHISPER_MODEL, SAMPLE_RATE, SILENCE_THRESHOLD, TRANSCRIPTION_PROMPT

class LiveTranscriber:
    def __init__(self, model_size=WHISPER_MODEL, language="en"):
        print(f"Initializing with model: {model_size}, language: {language}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        self.model = whisper.load_model(model_size).to(self.device)
        if self.device == "cpu":
            torch.set_num_threads(4)
        self.sample_rate = SAMPLE_RATE
        self.vad = webrtcvad.Vad(3)  # Mode 3: most aggressive to reduce noise triggers
        self.is_speaking = False
        self.running = True
        self.rms_counter = 0
        self.language = language
        self.transcription_queue = queue.Queue(maxsize=1)
        self.transcription_thread = threading.Thread(target=self._transcription_worker, daemon=True)
        self.transcription_thread.start()
        self.prompt = TRANSCRIPTION_PROMPT
        self.speech_debounce = 0  # Counter to debounce speech detection

    def detect_speech(self, audio_chunk):
        audio_int16 = (audio_chunk * 32768).astype(np.int16).tobytes()
        return self.vad.is_speech(audio_int16, sample_rate=self.sample_rate)

    def transcribe_chunk(self, audio_chunk):
        try:
            audio_data = audio_chunk.flatten().astype(np.float32)
            if np.max(np.abs(audio_data)) > 0:
                audio_data /= np.max(np.abs(audio_data))
            rms = np.sqrt(np.mean(audio_data**2))
            if rms < SILENCE_THRESHOLD:
                print("Audio too quiet, skipping transcription")
                return ""
            print(f"Transcribing audio, length: {len(audio_data)}, RMS: {rms:.4f}")
            result = self.model.transcribe(
                audio_data,
                language=self.language,
                fp16=False,
                prompt=self.prompt,
                temperature=0.2  # Lower temperature for more deterministic output
            )
            transcription = result['text'].strip()
            print(f"Full transcription: '{transcription}'")
            return transcription
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def set_language(self, language):
        self.language = language
        print(f"Language set to: {language}")

    def set_model(self, model_size):
        print(f"Changing model to: {model_size}")
        self.model = None
        import gc
        gc.collect()
        self.model = whisper.load_model(model_size).to(self.device)
        print(f"Model changed to: {model_size}")

    def live_transcribe(self, callback=print):
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            indata_normalized = indata / np.max(np.abs(indata)) if np.max(np.abs(indata)) > 0 else indata
            rms = np.sqrt(np.mean(indata_normalized**2))
            self.rms_counter += 1
            if self.rms_counter % 50 == 0:
                print(f"RMS: {rms:.4f}, Length: {len(indata)}")

            is_speech = self.detect_speech(indata_normalized)
            if is_speech:
                self.speech_debounce += 1
                if self.speech_debounce >= 5:  # Require ~100ms of sustained speech
                    if not self.is_speaking:
                        self.is_speaking = True
                        print("Speech started")
                    if not hasattr(self, 'audio_buffer'):
                        self.audio_buffer = indata_normalized.copy()
                    else:
                        max_buffer_size = self.sample_rate * 2  # 2 seconds
                        if len(self.audio_buffer) < max_buffer_size:
                            self.audio_buffer = np.vstack((self.audio_buffer, indata_normalized))
                        else:
                            print("Buffer full, forcing processing")
                            audio_to_process = self.audio_buffer.copy()
                            self.process_buffer(audio_to_process, callback)
                            self.audio_buffer = indata_normalized.copy()
            else:
                self.speech_debounce = max(0, self.speech_debounce - 1)
                if self.is_speaking and hasattr(self, 'audio_buffer') and self.speech_debounce == 0:
                    print("Speech ended, processing")
                    audio_to_process = self.audio_buffer.copy()
                    self.process_buffer(audio_to_process, callback)
                    del self.audio_buffer
                    self.is_speaking = False

        def _restart_stream():
            try:
                stream = sd.InputStream(
                    callback=audio_callback,
                    channels=1,
                    samplerate=self.sample_rate,
                    dtype='float32',
                    blocksize=int(self.sample_rate * 0.02),
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

    def process_buffer(self, audio_chunk, callback):
        print("Processing buffer")
        try:
            if not self.transcription_queue.empty():
                self.transcription_queue.get_nowait()
            self.transcription_queue.put((audio_chunk, callback))
        except queue.Full:
            pass

    def _transcription_worker(self):
        while self.running:
            try:
                audio_chunk, callback = self.transcription_queue.get(timeout=1)
                transcription = self.transcribe_chunk(audio_chunk)
                if transcription:
                    callback(transcription)
            except queue.Empty:
                continue

    def stop(self):
        print("Stopping LiveTranscriber")
        self.running = False
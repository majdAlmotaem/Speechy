import whisper
import sounddevice as sd
import numpy as np
import wavio
import threading
from config import WHISPER_MODEL, SAMPLE_RATE

class LiveTranscriber:
    def __init__(self, model_size=WHISPER_MODEL):
        self.model = whisper.load_model(model_size)
        self.sample_rate = SAMPLE_RATE
        self.chunk_duration = 5  # seconds
        self.silence_threshold = 0.01  # Adjust based on your environment
        self.is_speaking = False
        self.running = True  # Flag to control the transcription loop

    def detect_speech(self, audio_chunk):
        """
        Detect if there's speech in the audio chunk
        """
        rms = np.sqrt(np.mean(audio_chunk**2))
        return rms > self.silence_threshold

    def transcribe_chunk(self, audio_chunk):
        """
        Transcribe a chunk of audio
        """
        try:
            # Save chunk to temporary file using wavio
            temp_file = "live_chunk.wav"
            wavio.write(temp_file, audio_chunk, self.sample_rate, sampwidth=2)
            
            # Transcribe
            result = self.model.transcribe(temp_file, language='en')
            return result['text']
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def live_transcribe(self, callback=print):
        """
        Continuous live transcription with improved error handling
        """
        def audio_callback(indata, frames, time, status):
            if status and status.name != 'input overflow':
                print(f"Status: {status}")
                return
            
            if status and status.name == 'input overflow':
                print(f"Status: {status}")
                # Don't return, try to continue processing
            
            # Detect speech
            if self.detect_speech(indata):
                if not self.is_speaking:
                    self.is_speaking = True
                    print("Speech started")
                
                # Accumulate audio
                if not hasattr(self, 'audio_buffer'):
                    self.audio_buffer = indata.copy()
                else:
                    # Limit buffer size to prevent memory issues
                    max_buffer_size = int(self.sample_rate * 5)  # 5 seconds max
                    if len(self.audio_buffer) < max_buffer_size:
                        self.audio_buffer = np.vstack((self.audio_buffer, indata))
            else:
                if self.is_speaking and hasattr(self, 'audio_buffer'):
                    # Process in a separate thread to avoid blocking
                    audio_to_process = self.audio_buffer.copy()
                    threading.Thread(
                        target=self._process_audio,
                        args=(audio_to_process, callback),
                        daemon=True
                    ).start()
                    
                    # Reset buffer
                    del self.audio_buffer
                    self.is_speaking = False

        def _restart_stream():
            """Helper function to restart the stream if it fails"""
            try:
                # Create a new stream with adjusted parameters
                stream = sd.InputStream(
                    callback=audio_callback, 
                    channels=1, 
                    samplerate=self.sample_rate,
                    dtype='float32',
                    blocksize=int(self.sample_rate * 0.2),  # Larger block size
                    latency='high'  # Higher latency for stability
                )
                
                with stream:
                    print("Audio stream started/restarted")
                    while self.running:
                        sd.sleep(1000)  # Check every second
                
            except Exception as e:
                print(f"Stream error: {e}")
                if self.running:
                    print("Attempting to restart stream...")
                    _restart_stream()

        # Start the streaming in a separate thread
        self.running = True
        streaming_thread = threading.Thread(target=_restart_stream, daemon=True)
        streaming_thread.start()
        
        # Keep the main thread alive
        try:
            while self.running:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("Stopping transcription...")
            self.running = False
        except Exception as e:
            print(f"Unexpected error in main loop: {e}")
            self.running = False

    def _process_audio(self, audio_chunk, callback):
        """Process audio in a separate thread"""
        transcription = self.transcribe_chunk(audio_chunk)
        if transcription.strip():
            callback(transcription)

    def stop(self):
        """Stop the transcription"""
        self.running = False

def live_transcribe(callback=print):
    transcriber = LiveTranscriber()
    try:
        transcriber.live_transcribe(callback)
    except Exception as e:
        print(f"Live transcription error: {e}")
    finally:
        transcriber.stop()

import os
from modules.audio_recorder import audio_recorder
from modules.speech_transcriber import transcribe_audio, load_whisper_model
from modules.command_executor import execute_command

# Ensure FFmpeg path is set
os.environ['PATH'] += os.pathsep + r'C:\ffmpeg-2025-03-17-git-5b9356f18e-full_build\bin'

def main():
    print("Voice control started. Say 'exit' to stop.")
    
    # Pre-load model for efficiency
    model = load_whisper_model(model_size="small")
    
    while True:
        # Record audio
        audio_file = audio_recorder()
        
        # Transcribe with English language hint
        command = transcribe_audio(
            audio_file, 
            model=model, 
            language='en'
        )

        print(f"You said: {command}")

        # Execute command
        continue_execution = execute_command(command)
        
        # Check if we should continue the loop
        if continue_execution is False:
            break

    print("Program stopped.")

if __name__ == "__main__":
    main()

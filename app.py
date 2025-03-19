import os
from modules.live_transcriber import live_transcribe
from modules.command_executor import execute_command

# Ensure FFmpeg path is set
os.environ['PATH'] += os.pathsep + r'C:\ffmpeg-2025-03-17-git-5b9356f18e-full_build\bin'

def main(output_callback=print):
    output_callback("Voice control started. Say 'exit' to stop.")
    
    def process_command(text):
        output_callback(f"You said: {text}")
        continue_execution = execute_command(text)
        
        # Check if we should continue the loop
        return continue_execution
    
    while True:
        if not live_transcribe(callback=process_command):
            break

    output_callback("Program stopped.")

if __name__ == "__main__":
    main()

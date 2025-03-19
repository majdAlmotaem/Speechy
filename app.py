import os
from modules.live_transcriber import live_transcribe
from modules.command_executor import execute_command

def main(output_callback=print):
    output_callback("Voice control started. Say 'exit' to stop.")
    
    def process_command(text):
        output_callback(f"You said: {text}")
        return execute_command(text)
    
    live_transcribe(callback=process_command)
    output_callback("Program stopped.")

if __name__ == "__main__":
    main()

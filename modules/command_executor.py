import pyautogui
import time

# Global variable to track typing state
is_typing_mode = False

def execute_command(text):
    """
    Execute voice commands
    
    Args:
        text (str): Transcribed command text
    
    Returns:
        bool: Whether to continue execution
    """
    global is_typing_mode
    text = text.lower().strip()
    print(f"Received command: {text}")

    command_actions = {
        "open notepad": lambda: (
            pyautogui.hotkey("win", "r"),
            pyautogui.typewrite("notepad"),
            pyautogui.press("enter")
        ),
        "scroll down": lambda: pyautogui.scroll(-100),
        "click": lambda: pyautogui.click(),
        "start typing": lambda: start_typing(),
        "stop typing": lambda: stop_typing(),
        "exit": lambda: False
    }

    # Check for specific commands first
    for command, action in command_actions.items():
        if command in text:
            return action()
    
    # If in typing mode, continue typing
    if is_typing_mode:
        pyautogui.typewrite(text + " ")
        return True
    
    print(f"Unrecognized command: {text}")
    return True

def start_typing():
    """
    Initiate typing mode
    """
    global is_typing_mode
    is_typing_mode = True
    print("Typing mode activated. Start speaking what you want to type.")
    return True

def stop_typing():
    """
    Stop typing mode
    """
    global is_typing_mode
    is_typing_mode = False
    print("Typing mode deactivated.")
    return True

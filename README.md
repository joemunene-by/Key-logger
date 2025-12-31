# Python Basic Key Logger

A simple Python key logger built for educational and cybersecurity research purposes. This tool captures keystrokes and logs them to a local file.

## ⚠️ Disclaimer

**This tool is for educational purposes only.**
Unauthorized use of key loggers is illegal and unethical. Ensure you have explicit permission from the device owner before running this software. The author is not responsible for any misuse of this tool.

## Prerequisites

- Python 3.x
- `pip` (Python package installer)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/joemunene-by/Key-logger.git
   cd Key-logger
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:

   ```bash
   python main.py
   ```

2. The script will start recording keystrokes.
3. Press `ESC` to stop the logging process.
4. Recorded keystrokes will be saved in `keylog.txt` in the same directory.

## Project Structure

- `main.py`: The main Python script that captures keystrokes.
- `requirements.txt`: List of Python dependencies.
- `keylog.txt`: Output file identifying captured keystrokes (created at runtime).

# Educational Keylogger and Log Analyzer

> **WARNING -- FOR AUTHORIZED SECURITY TESTING AND EDUCATIONAL PURPOSES ONLY.**
>
> Unauthorized use of keyloggers is **illegal** in virtually every jurisdiction. This includes, but is not limited to, violations of the Computer Fraud and Abuse Act (CFAA) in the United States, the Computer Misuse Act in the United Kingdom, and the General Data Protection Regulation (GDPR) in the European Union. **You must have explicit, written consent from the system owner before running this software.** The authors assume NO responsibility for any misuse.

---

## Description

This project is an educational keystroke logging toolkit designed for cybersecurity students, researchers, and authorized penetration testers. It demonstrates how keyloggers work at a technical level so that defenders can better understand and mitigate this class of threat.

The toolkit consists of two tools:

- **keylogger.py** -- A configurable keystroke logger with clipboard monitoring, log rotation, and structured output.
- **analyzer.py** -- A log analysis tool that computes typing statistics, extracts words, and generates summary reports.

## Features

### Keylogger (keylogger.py)

- Keystroke capture using pynput
- Optional clipboard monitoring via pyperclip
- JSON or plain-text structured log format with timestamps
- Configurable log rotation based on maximum file size
- Stop capture with keyboard shortcut (Ctrl+Shift+F12)
- Optional auto-stop after a specified duration
- Consent confirmation prompt before any logging begins
- Legal disclaimer printed at startup and embedded in every log entry

### Log Analyzer (analyzer.py)

- Parses both JSON and text format log files
- Computes statistics: total keystrokes, keystrokes per minute, key frequency
- Extracts typed words from keystroke sequences (handles backspace, space, enter)
- Displays session timeline with start/end markers
- Word frequency analysis
- Outputs reports in text or JSON format
- Legal disclaimers in all output

## Installation

### Prerequisites

- Python 3.8 or later
- Linux, macOS, or Windows

### Steps

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

### Keylogger

```bash
# Basic usage (JSON output, no clipboard monitoring)
python keylogger.py

# Full options
python keylogger.py --output keylog.json --format json --clipboard --duration 120 --max-size 2048
```

**Arguments:**

| Flag | Description | Default |
|------|-------------|---------|
| `--output`, `-o` | Output log file path | `keylog.json` |
| `--format`, `-f` | Log format: `json` or `text` | `json` |
| `--clipboard`, `-c` | Enable clipboard monitoring | off |
| `--duration`, `-d` | Auto-stop after N seconds | unlimited |
| `--max-size` | Max log file size in KB before rotation | 1024 |

**Stopping:** Press `Ctrl+Shift+F12` or send `SIGINT` (Ctrl+C).

### Log Analyzer

```bash
# Analyze a log file and print report to the terminal
python analyzer.py --input keylog.json

# Save report to a file
python analyzer.py --input keylog.json --output report.txt

# JSON output
python analyzer.py --input keylog.json --format json --output report.json
```

**Arguments:**

| Flag | Description | Default |
|------|-------------|---------|
| `--input`, `-i` | Path to the log file to analyze | required |
| `--output`, `-o` | Path to write the report | stdout |
| `--format`, `-f` | Output format: `text` or `json` | `text` |

## Legal and Ethical Guidelines

This software exists to serve the cybersecurity education community. To use it responsibly:

1. **Obtain written authorization.** Never run this tool on a system without the explicit, documented consent of the system owner.
2. **Limit scope.** Only capture data that is within the agreed scope of your security assessment or educational exercise.
3. **Protect captured data.** Keystroke logs may contain sensitive information. Store them securely and delete them when no longer needed.
4. **Know your laws.** Familiarize yourself with the computer crime and privacy laws in your jurisdiction before using any monitoring tool.
5. **Report findings responsibly.** If you discover vulnerabilities during authorized testing, follow responsible disclosure practices.
6. **Do not exfiltrate data.** This tool logs to local files only. Do not modify it to transmit captured data over a network without explicit authorization.

## Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. THE AUTHORS AND CONTRIBUTORS ARE NOT RESPONSIBLE FOR ANY DAMAGE, LEGAL CONSEQUENCES, OR OTHER LIABILITY ARISING FROM THE USE OR MISUSE OF THIS SOFTWARE.

**Using this tool without proper authorization is a criminal offense.** By downloading, installing, or executing this software, you acknowledge that you understand the legal implications and accept full responsibility for your actions.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

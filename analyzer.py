#!/usr/bin/env python3
"""
Keylog Analyzer - FOR AUTHORIZED SECURITY TESTING AND EDUCATIONAL PURPOSES ONLY.

LEGAL DISCLAIMER:
    This tool analyzes log files produced by the educational keylogger.
    It is intended solely for authorized security auditing and educational
    research. Analyzing intercepted keystrokes without authorization is
    illegal in most jurisdictions. The authors accept NO liability for misuse.

Usage:
    python analyzer.py --input keylog.json --output report.txt
"""

import argparse
import collections
import datetime
import json
import os
import sys

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init(autoreset=True)
except ImportError:
    class _NoColor:
        RED = YELLOW = GREEN = CYAN = MAGENTA = RESET = ""
    class _NoStyle:
        BRIGHT = RESET_ALL = ""
    Fore = _NoColor()
    Style = _NoStyle()


DISCLAIMER = (
    "DISCLAIMER: This analyzer is for EDUCATIONAL and AUTHORIZED security "
    "testing purposes only. Unauthorized analysis of intercepted data is illegal."
)


def parse_log_file(path):
    """
    Parse a keylogger output file (JSON-lines or text format).

    Returns a list of entry dicts with at least 'timestamp', 'type', 'value'.
    """
    entries = []

    if not os.path.exists(path):
        sys.exit(f"Error: file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            # Try JSON first
            try:
                entry = json.loads(line)
                entries.append(entry)
                continue
            except json.JSONDecodeError:
                pass

            # Fallback: text format  [timestamp] [type] value
            if line.startswith("["):
                try:
                    parts = line.split("]", 2)
                    ts = parts[0].lstrip("[").strip()
                    etype = parts[1].strip().lstrip("[").strip()
                    value = parts[2].strip() if len(parts) > 2 else ""
                    entries.append({
                        "timestamp": ts,
                        "type": etype,
                        "value": value,
                    })
                except (IndexError, ValueError):
                    pass  # Skip malformed lines

    return entries


def compute_statistics(entries):
    """Compute typing statistics from parsed log entries."""
    keystrokes = [e for e in entries if e.get("type") == "keystroke"]
    clipboard_events = [e for e in entries if e.get("type") == "clipboard"]

    # Parse timestamps
    timestamps = []
    for e in keystrokes:
        try:
            ts = datetime.datetime.fromisoformat(e["timestamp"])
            timestamps.append(ts)
        except (ValueError, KeyError):
            pass

    total_keys = len(keystrokes)

    # Duration
    if len(timestamps) >= 2:
        duration = (timestamps[-1] - timestamps[0]).total_seconds()
    else:
        duration = 0.0

    # Keystrokes per minute
    kpm = (total_keys / (duration / 60.0)) if duration > 0 else 0.0

    # Most common keys
    key_counter = collections.Counter(e.get("value", "") for e in keystrokes)
    most_common = key_counter.most_common(20)

    # Special key counts
    special_keys = sum(1 for e in keystrokes if e.get("value", "").startswith("["))
    printable_keys = total_keys - special_keys

    return {
        "total_keystrokes": total_keys,
        "printable_keys": printable_keys,
        "special_keys": special_keys,
        "duration_seconds": round(duration, 2),
        "keystrokes_per_minute": round(kpm, 2),
        "most_common_keys": most_common,
        "clipboard_events": len(clipboard_events),
        "first_timestamp": timestamps[0].isoformat() if timestamps else None,
        "last_timestamp": timestamps[-1].isoformat() if timestamps else None,
    }


def extract_words(entries):
    """
    Reconstruct typed words from a sequence of keystroke events.

    Splits on special keys like space, enter, tab, and backspace.
    """
    buffer = []
    words = []

    for e in entries:
        if e.get("type") != "keystroke":
            continue
        val = e.get("value", "")

        if val in ("[space]", " "):
            word = "".join(buffer).strip()
            if word:
                words.append(word)
            buffer.clear()
        elif val in ("[enter]", "[tab]"):
            word = "".join(buffer).strip()
            if word:
                words.append(word)
            buffer.clear()
        elif val == "[backspace]":
            if buffer:
                buffer.pop()
        elif not val.startswith("["):
            buffer.append(val)

    # Flush remaining buffer
    word = "".join(buffer).strip()
    if word:
        words.append(word)

    return words


def build_session_timeline(entries):
    """Build a timeline of session events."""
    timeline = []
    for e in entries:
        etype = e.get("type", "")
        if etype in ("session_start", "session_end"):
            timeline.append({
                "timestamp": e.get("timestamp", "unknown"),
                "event": e.get("value", etype),
                "details": {k: v for k, v in e.items()
                            if k not in ("timestamp", "type", "value", "disclaimer")}
            })
    return timeline


def format_report(stats, words, timeline):
    """Format the analysis into a human-readable report string."""
    lines = []
    lines.append("=" * 72)
    lines.append("  KEYLOG ANALYSIS REPORT")
    lines.append("  " + DISCLAIMER)
    lines.append("=" * 72)
    lines.append("")

    # Session timeline
    lines.append("SESSION TIMELINE")
    lines.append("-" * 40)
    if timeline:
        for event in timeline:
            lines.append(f"  [{event['timestamp']}] {event['event']}")
            for k, v in event["details"].items():
                lines.append(f"    {k}: {v}")
    else:
        lines.append("  No session markers found.")
    lines.append("")

    # Statistics
    lines.append("STATISTICS")
    lines.append("-" * 40)
    lines.append(f"  Total keystrokes:      {stats['total_keystrokes']}")
    lines.append(f"  Printable keys:        {stats['printable_keys']}")
    lines.append(f"  Special keys:          {stats['special_keys']}")
    lines.append(f"  Duration:              {stats['duration_seconds']}s")
    lines.append(f"  Keystrokes per minute:  {stats['keystrokes_per_minute']}")
    lines.append(f"  Clipboard events:      {stats['clipboard_events']}")
    if stats["first_timestamp"]:
        lines.append(f"  First keystroke:       {stats['first_timestamp']}")
        lines.append(f"  Last keystroke:        {stats['last_timestamp']}")
    lines.append("")

    # Most common keys
    lines.append("MOST COMMON KEYS (top 20)")
    lines.append("-" * 40)
    for key, count in stats["most_common_keys"]:
        display = key if key else "(empty)"
        bar = "#" * min(count, 50)
        lines.append(f"  {display:>15s}  {count:>5d}  {bar}")
    lines.append("")

    # Extracted words
    lines.append("EXTRACTED WORDS")
    lines.append("-" * 40)
    if words:
        # Show up to 100 words
        display_words = words[:100]
        lines.append(f"  Total words extracted: {len(words)}")
        lines.append(f"  First {len(display_words)} words:")
        lines.append("  " + " ".join(display_words))
        if len(words) > 100:
            lines.append(f"  ... and {len(words) - 100} more")
    else:
        lines.append("  No words extracted.")
    lines.append("")

    # Word frequency
    if words:
        lines.append("WORD FREQUENCY (top 20)")
        lines.append("-" * 40)
        word_counter = collections.Counter(w.lower() for w in words)
        for word, count in word_counter.most_common(20):
            lines.append(f"  {word:>20s}  {count:>5d}")
        lines.append("")

    lines.append("=" * 72)
    lines.append(f"  {DISCLAIMER}")
    lines.append("=" * 72)

    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Keylog Analyzer - FOR AUTHORIZED SECURITY TESTING AND EDUCATIONAL "
            "PURPOSES ONLY. Analyzes log files produced by the educational keylogger."
        ),
        epilog=DISCLAIMER,
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the keylogger log file to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Path to write the analysis report (default: stdout)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format: text or json (default: text)"
    )
    return parser.parse_args()


def main():
    """Entry point for the keylog analyzer."""
    print(f"\n{Fore.YELLOW}{DISCLAIMER}{Style.RESET_ALL}\n")

    args = parse_args()
    entries = parse_log_file(args.input)

    if not entries:
        print(f"{Fore.RED}No entries found in {args.input}{Style.RESET_ALL}")
        sys.exit(1)

    print(f"{Fore.GREEN}Parsed {len(entries)} entries from {args.input}{Style.RESET_ALL}")

    stats = compute_statistics(entries)
    words = extract_words(entries)
    timeline = build_session_timeline(entries)

    if args.format == "json":
        result = {
            "disclaimer": DISCLAIMER,
            "source_file": args.input,
            "statistics": stats,
            "extracted_words": words[:200],
            "word_count": len(words),
            "session_timeline": timeline,
        }
        # Convert Counter tuples to dicts for JSON
        result["statistics"]["most_common_keys"] = [
            {"key": k, "count": c} for k, c in stats["most_common_keys"]
        ]
        output_text = json.dumps(result, indent=2)
    else:
        output_text = format_report(stats, words, timeline)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text + "\n")
        print(f"{Fore.GREEN}Report written to {args.output}{Style.RESET_ALL}")
    else:
        print()
        print(output_text)


if __name__ == "__main__":
    main()

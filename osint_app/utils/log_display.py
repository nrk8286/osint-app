"""Live log display utilities for the CLI.

Provides:
- ``display_live_log(tail)``  — pretty-print the last N events from the JSONL file.
- ``watch_live_log(interval)`` — tail the log file in real time, refreshing every
  *interval* seconds (Ctrl-C to stop).
"""

import json
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from osint_app.core.config import config

_SENTIMENT_COLOURS = {
    "SEARCH_STARTED": "cyan",
    "SEARCH_DONE": "green",
    "SEARCH_ERROR": "red",
    "STEP": "yellow",
    "COLLECTION_STARTED": "magenta",
    "COLLECTION_DONE": "blue",
}

_SOURCE_ICONS = {
    "google": "🔍",
    "twitter": "🐦",
    "reddit": "🤖",
    "news": "📰",
    "github": "🐙",
    "hackernews": "🔶",
    "pastebin": "📋",
    "youtube": "▶️ ",
    "shodan": "🛰️ ",
    "telegram": "✈️ ",
    "rss": "📡",
    "monitor": "🖥️ ",
}


def _icon(source: str) -> str:
    return _SOURCE_ICONS.get(source.lower(), "🔎")


def _read_events(log_file: str, tail: int) -> list:
    """Read the last *tail* JSON lines from *log_file*."""
    path = Path(log_file)
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        events = []
        for line in lines[-tail:]:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return events
    except Exception:
        return []


def _render_table(events: list, console: Optional[object] = None) -> None:
    """Render events as a rich table or plain text."""
    if not events:
        if RICH_AVAILABLE and console:
            console.print("[yellow]No events logged yet.[/yellow]")
        else:
            print("No events logged yet.")
        return

    if RICH_AVAILABLE and console:
        table = Table(title="Agent Activity Log", show_lines=False, expand=True)
        table.add_column("Time", style="dim", width=10, no_wrap=True)
        table.add_column("Source", width=14, no_wrap=True)
        table.add_column("Event", width=20, no_wrap=True)
        table.add_column("Keyword", width=20)
        table.add_column("Count", justify="right", width=6)
        table.add_column("ms", justify="right", width=7)
        table.add_column("Detail", overflow="fold")

        for ev in events:
            event_type = ev.get("event_type", "")
            colour = _SENTIMENT_COLOURS.get(event_type, "white")
            ts = ev.get("timestamp", "")
            ts_short = ts[11:19] if len(ts) >= 19 else ts
            source = ev.get("source", "")
            icon = _icon(source)

            count_str = str(ev["count"]) if "count" in ev else ""
            dur_str = str(ev["duration_ms"]) if "duration_ms" in ev else ""
            detail = ev.get("detail", "")

            table.add_row(
                ts_short,
                f"{icon} {source}",
                Text(event_type, style=colour),
                ev.get("keyword", ""),
                count_str,
                dur_str,
                detail,
            )

        console.print(table)
    else:
        header = f"{'Time':<10}  {'Source':<14}  {'Event':<22}  {'Keyword':<20}  {'Cnt':>5}  {'ms':>7}  Detail"
        print(header)
        print("-" * len(header))
        for ev in events:
            ts = ev.get("timestamp", "")
            ts_short = ts[11:19] if len(ts) >= 19 else ts
            print(
                f"{ts_short:<10}  {ev.get('source',''):<14}  {ev.get('event_type',''):<22}  "
                f"{ev.get('keyword',''):<20}  {str(ev.get('count',''))!s:>5}  "
                f"{str(ev.get('duration_ms',''))!s:>7}  {ev.get('detail','')}"
            )


def display_live_log(tail: int = 50, log_file: Optional[str] = None) -> None:
    """Pretty-print the last *tail* events from the activity log.

    Args:
        tail: Number of most-recent events to show
        log_file: Path to the JSONL log file (defaults to config value)
    """
    log_path = log_file or config.log_file
    events = _read_events(log_path, tail)
    console = Console() if RICH_AVAILABLE else None
    _render_table(events, console)


def watch_live_log(interval: float = 1.0, tail: int = 30, log_file: Optional[str] = None) -> None:
    """Continuously tail and re-render the activity log.

    Refreshes every *interval* seconds.  Press Ctrl-C to stop.

    Args:
        interval: Refresh interval in seconds
        tail: Number of most-recent events to show per refresh
        log_file: Path to the JSONL log file (defaults to config value)
    """
    log_path = log_file or config.log_file
    console = Console() if RICH_AVAILABLE else None

    print(f"Watching {log_path}  (Ctrl-C to stop)")
    last_pos = 0

    try:
        while True:
            path = Path(log_path)
            if path.exists():
                current_pos = path.stat().st_size
                if current_pos != last_pos:
                    last_pos = current_pos
                    if RICH_AVAILABLE and console:
                        console.clear()
                    else:
                        # ANSI clear screen
                        sys.stdout.write("\033[2J\033[H")
                        sys.stdout.flush()
                    display_live_log(tail=tail, log_file=log_path)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped watching.")

"""Structured agent activity logger for real-time monitoring.

Provides a singleton ``AgentLogger`` that:
- Writes JSON-formatted events to a rotating JSONL file.
- Maintains an in-memory ring buffer for the REST API.
- Broadcasts events to subscribed asyncio queues for the SSE endpoint.
- Optionally persists events to the database.

Usage::

    from osint_app.utils.agent_logger import agent_logger

    agent_logger.agent_start("HackerNews", "python")
    agent_logger.agent_result("HackerNews", "python", count=7, duration_ms=320)
    agent_logger.agent_error("Shodan", "python", error="API quota exceeded")
"""

import asyncio
import json
import logging
import os
from collections import deque
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional


# ---------------------------------------------------------------------------
# ANSI colour helpers (used for stderr output)
# ---------------------------------------------------------------------------

_RESET = "\033[0m"
_BOLD = "\033[1m"
_COLOURS = {
    "SEARCH_STARTED": "\033[36m",   # cyan
    "SEARCH_DONE": "\033[32m",      # green
    "SEARCH_ERROR": "\033[31m",     # red
    "STEP": "\033[33m",             # yellow
    "COLLECTION_STARTED": "\033[35m",  # magenta
    "COLLECTION_DONE": "\033[34m",  # blue
}

_SOURCE_ICONS = {
    "google": "🔍",
    "twitter": "🐦",
    "reddit": "🤖",
    "news": "📰",
    "github": "🐙",
    "hackernews": "🔶",
    "pastebin": "📋",
    "youtube": "▶️",
    "shodan": "🛰️",
    "telegram": "✈️",
    "rss": "📡",
    "monitor": "🖥️",
}


def _icon(source: str) -> str:
    return _SOURCE_ICONS.get(source.lower(), "🔎")


# ---------------------------------------------------------------------------
# AgentLogger
# ---------------------------------------------------------------------------


class AgentLogger:
    """Singleton logger for agent activity events."""

    _instance: Optional["AgentLogger"] = None

    def __init__(self, log_file: str, ring_buffer_size: int, log_to_db: bool) -> None:
        self.log_file = log_file
        self.ring_buffer_size = ring_buffer_size
        self.log_to_db = log_to_db

        self._buffer: Deque[Dict[str, Any]] = deque(maxlen=ring_buffer_size)
        self._subscribers: List[asyncio.Queue] = []

        self._setup_file_logger()

    # ── Singleton ──────────────────────────────────────────────────────

    @classmethod
    def get_instance(cls) -> "AgentLogger":
        """Return the module-level singleton, creating it on first call."""
        if cls._instance is None:
            from osint_app.core.config import config

            cls._instance = cls(
                log_file=config.log_file,
                ring_buffer_size=config.log_ring_buffer_size,
                log_to_db=config.log_to_db,
            )
        return cls._instance

    # ── File logger setup ──────────────────────────────────────────────

    def _setup_file_logger(self) -> None:
        """Configure a rotating JSONL file handler."""
        self._logger = logging.getLogger("osint.agent")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        if self._logger.handlers:
            return  # already configured (e.g. reimport during tests)

        path = Path(self.log_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        self._logger.addHandler(file_handler)

    # ── Public API ─────────────────────────────────────────────────────

    def agent_start(self, source_name: str, keyword: str) -> None:
        """Log a SEARCH_STARTED event."""
        self._log_event("SEARCH_STARTED", source_name, keyword)

    def agent_result(
        self, source_name: str, keyword: str, count: int, duration_ms: float
    ) -> None:
        """Log a SEARCH_DONE event with result count and timing."""
        self._log_event(
            "SEARCH_DONE",
            source_name,
            keyword,
            count=count,
            duration_ms=round(duration_ms, 1),
        )

    def agent_error(self, source_name: str, keyword: str, error: str) -> None:
        """Log a SEARCH_ERROR event."""
        self._log_event("SEARCH_ERROR", source_name, keyword, detail=error)

    def agent_step(self, source_name: str, message: str, keyword: str = "") -> None:
        """Log a STEP event for fine-grained progress."""
        self._log_event("STEP", source_name, keyword, detail=message)

    def collection_started(self, keyword: str, sources: List[str]) -> None:
        """Log a COLLECTION_STARTED event."""
        self._log_event(
            "COLLECTION_STARTED", "monitor", keyword, detail=f"sources: {', '.join(sources)}"
        )

    def collection_done(self, keyword: str, total: int, duration_ms: float) -> None:
        """Log a COLLECTION_DONE event."""
        self._log_event(
            "COLLECTION_DONE",
            "monitor",
            keyword,
            count=total,
            duration_ms=round(duration_ms, 1),
        )

    # ── Retrieval ──────────────────────────────────────────────────────

    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return the most recent events from the in-memory ring buffer.

        Args:
            limit: Maximum number of events to return

        Returns:
            List of event dicts, newest last
        """
        events = list(self._buffer)
        return events[-limit:]

    def subscribe(self) -> "asyncio.Queue[Dict[str, Any]]":
        """Register a new subscriber queue for SSE streaming.

        Returns:
            A new asyncio.Queue that will receive all future events.
        """
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: "asyncio.Queue") -> None:
        """Remove a subscriber queue."""
        try:
            self._subscribers.remove(q)
        except ValueError:
            pass

    # ── Internal ───────────────────────────────────────────────────────

    def _log_event(
        self,
        event_type: str,
        source_name: str,
        keyword: str,
        count: Optional[int] = None,
        duration_ms: Optional[float] = None,
        detail: Optional[str] = None,
    ) -> None:
        """Build an event dict, write to file/buffer/subscribers, and print."""
        event: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "source": source_name,
            "keyword": keyword,
        }
        if count is not None:
            event["count"] = count
        if duration_ms is not None:
            event["duration_ms"] = duration_ms
        if detail is not None:
            event["detail"] = detail

        # Write JSON line to file
        try:
            self._logger.info(json.dumps(event, ensure_ascii=False))
        except Exception:
            pass

        # Add to ring buffer
        self._buffer.append(event)

        # Broadcast to SSE subscribers
        for q in list(self._subscribers):
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                pass

        # Optionally persist to DB (non-blocking best-effort)
        if self.log_to_db:
            self._persist_to_db(event)

        # Pretty-print to stderr
        self._print_event(event)

    def _persist_to_db(self, event: Dict[str, Any]) -> None:
        """Save event to database (best-effort; errors are suppressed)."""
        try:
            from osint_app.storage.database import DatabaseStorage

            db = DatabaseStorage()
            db.save_log_event(event)
        except Exception:
            pass

    def _print_event(self, event: Dict[str, Any]) -> None:
        """Print a colourised one-liner to stderr."""
        event_type = event["event_type"]
        colour = _COLOURS.get(event_type, "")
        icon = _icon(event["source"])
        ts = event["timestamp"][11:19]  # HH:MM:SS

        parts = [
            f"{ts}",
            f"{icon} {event['source']:<12}",
            f"{_BOLD}{colour}{event_type:<20}{_RESET}",
        ]
        if event.get("keyword"):
            parts.append(f"keyword={event['keyword']!r}")
        if event.get("count") is not None:
            parts.append(f"count={event['count']}")
        if event.get("duration_ms") is not None:
            parts.append(f"{event['duration_ms']}ms")
        if event.get("detail"):
            parts.append(event["detail"][:80])

        print("  ".join(parts), flush=True)


# ---------------------------------------------------------------------------
# Module-level singleton (import and use directly)
# ---------------------------------------------------------------------------

agent_logger: AgentLogger = AgentLogger.get_instance()

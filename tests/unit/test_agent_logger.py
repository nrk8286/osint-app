"""Unit tests for AgentLogger."""

import asyncio
import json
import os
import tempfile
from collections import deque
from unittest.mock import MagicMock, patch

import pytest

from osint_app.utils.agent_logger import AgentLogger


# ---------------------------------------------------------------------------
# Helper: create a fresh AgentLogger instance wired to a temp file
# ---------------------------------------------------------------------------


def _make_logger(tmp_dir: str, ring_size: int = 10) -> AgentLogger:
    log_file = os.path.join(tmp_dir, "test_agent.jsonl")
    logger = AgentLogger(log_file=log_file, ring_buffer_size=ring_size, log_to_db=False)
    return logger


class TestAgentLoggerEvents:
    """Tests for event creation and structure."""

    def test_agent_start_creates_correct_event(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        logger.agent_start("HackerNews", "python")
        events = logger.get_recent_events()
        assert len(events) == 1
        ev = events[0]
        assert ev["event_type"] == "SEARCH_STARTED"
        assert ev["source"] == "HackerNews"
        assert ev["keyword"] == "python"
        assert "timestamp" in ev

    def test_agent_result_includes_count_and_duration(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        logger.agent_result("GitHub", "osint", count=7, duration_ms=123.4)
        ev = logger.get_recent_events()[-1]
        assert ev["event_type"] == "SEARCH_DONE"
        assert ev["count"] == 7
        assert ev["duration_ms"] == 123.4

    def test_agent_error_includes_detail(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        logger.agent_error("Shodan", "http", error="quota exceeded")
        ev = logger.get_recent_events()[-1]
        assert ev["event_type"] == "SEARCH_ERROR"
        assert "quota exceeded" in ev["detail"]

    def test_agent_step_records_message(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        logger.agent_step("RSS", "fetching feed 1/3", keyword="security")
        ev = logger.get_recent_events()[-1]
        assert ev["event_type"] == "STEP"
        assert "fetching feed" in ev["detail"]

    def test_collection_started_event(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        logger.collection_started("malware", ["google", "hackernews"])
        ev = logger.get_recent_events()[-1]
        assert ev["event_type"] == "COLLECTION_STARTED"
        assert "google" in ev["detail"]

    def test_collection_done_event(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        logger.collection_done("exploit", total=15, duration_ms=2500.0)
        ev = logger.get_recent_events()[-1]
        assert ev["event_type"] == "COLLECTION_DONE"
        assert ev["count"] == 15


class TestRingBuffer:
    """Tests for in-memory ring buffer behaviour."""

    def test_buffer_respects_maxlen(self, tmp_path):
        logger = _make_logger(str(tmp_path), ring_size=3)
        for i in range(6):
            logger.agent_step("src", f"step {i}", keyword="k")
        events = logger.get_recent_events(limit=100)
        assert len(events) == 3  # only last 3 kept

    def test_get_recent_events_honours_limit(self, tmp_path):
        logger = _make_logger(str(tmp_path), ring_size=50)
        for i in range(20):
            logger.agent_step("src", f"step {i}", keyword="k")
        events = logger.get_recent_events(limit=5)
        assert len(events) == 5

    def test_get_recent_events_returns_newest_last(self, tmp_path):
        logger = _make_logger(str(tmp_path), ring_size=10)
        logger.agent_start("A", "kw1")
        logger.agent_start("B", "kw2")
        events = logger.get_recent_events(limit=2)
        assert events[-1]["source"] == "B"


class TestFileLogging:
    """Tests for JSONL file logging."""

    def test_events_written_to_file(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        logger.agent_start("Google", "test_kw")
        log_file = os.path.join(str(tmp_path), "test_agent.jsonl")
        assert os.path.exists(log_file)
        lines = open(log_file).read().strip().splitlines()
        assert len(lines) == 1
        ev = json.loads(lines[0])
        assert ev["source"] == "Google"

    def test_multiple_events_produce_multiple_lines(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        logger.agent_start("S1", "kw")
        logger.agent_result("S1", "kw", count=3, duration_ms=50.0)
        log_file = os.path.join(str(tmp_path), "test_agent.jsonl")
        lines = open(log_file).read().strip().splitlines()
        assert len(lines) == 2


class TestSSESubscriptions:
    """Tests for asyncio queue subscription / broadcast."""

    @pytest.mark.asyncio
    async def test_subscriber_receives_event(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        q = logger.subscribe()
        logger.agent_start("RSS", "feed_test")
        event = q.get_nowait()
        assert event["event_type"] == "SEARCH_STARTED"
        logger.unsubscribe(q)

    @pytest.mark.asyncio
    async def test_multiple_subscribers_all_receive_event(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        q1 = logger.subscribe()
        q2 = logger.subscribe()
        logger.agent_result("GitHub", "osint", count=5, duration_ms=100.0)
        ev1 = q1.get_nowait()
        ev2 = q2.get_nowait()
        assert ev1["count"] == ev2["count"] == 5
        logger.unsubscribe(q1)
        logger.unsubscribe(q2)

    @pytest.mark.asyncio
    async def test_unsubscribe_stops_delivery(self, tmp_path):
        logger = _make_logger(str(tmp_path))
        q = logger.subscribe()
        logger.unsubscribe(q)
        logger.agent_start("HN", "test")
        assert q.empty()

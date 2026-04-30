"""Unit tests for ReportGenerator."""

import json
import os
import tempfile

import pytest

from osint_app.utils.reporter import ReportGenerator


@pytest.fixture
def generator():
    return ReportGenerator()


@pytest.fixture
def sample_mentions():
    return [
        {
            "source": "twitter",
            "author": "user1",
            "text": "This is a great product!",
            "sentiment": {"sentiment": "positive", "polarity": 0.8},
        },
        {
            "source": "reddit",
            "author": "user2",
            "text": "I hate this terrible experience",
            "sentiment": {"sentiment": "negative", "polarity": -0.6},
        },
        {
            "source": "twitter",
            "author": "user3",
            "text": "Just a normal update",
            "sentiment": None,
        },
    ]


@pytest.fixture
def sample_stats():
    return {
        "total": 3,
        "positive": 1,
        "negative": 1,
        "neutral": 1,
        "avg_polarity": 0.1,
        "positive_pct": 33.3,
        "negative_pct": 33.3,
        "neutral_pct": 33.3,
    }


class TestGenerateSummary:
    """Tests for ReportGenerator.generate_summary."""

    def test_returns_string(self, generator, sample_mentions, sample_stats):
        report = generator.generate_summary(sample_mentions, sample_stats)
        assert isinstance(report, str)

    def test_contains_header(self, generator, sample_mentions, sample_stats):
        report = generator.generate_summary(sample_mentions, sample_stats)
        assert "OSINT MONITORING REPORT" in report

    def test_contains_total_count(self, generator, sample_mentions, sample_stats):
        report = generator.generate_summary(sample_mentions, sample_stats)
        assert "3" in report  # total from stats

    def test_contains_sentiment_section(self, generator, sample_mentions, sample_stats):
        report = generator.generate_summary(sample_mentions, sample_stats)
        assert "SENTIMENT ANALYSIS" in report
        assert "Positive" in report
        assert "Negative" in report

    def test_contains_sources_section(self, generator, sample_mentions, sample_stats):
        report = generator.generate_summary(sample_mentions, sample_stats)
        assert "SOURCES" in report
        assert "twitter" in report

    def test_contains_recent_mentions(self, generator, sample_mentions, sample_stats):
        report = generator.generate_summary(sample_mentions, sample_stats)
        assert "RECENT MENTIONS" in report

    def test_empty_mentions(self, generator, sample_stats):
        report = generator.generate_summary([], sample_stats)
        assert isinstance(report, str)
        assert "OSINT MONITORING REPORT" in report

    def test_text_truncated_at_100_chars(self, generator, sample_stats):
        long_text = "x" * 200
        mentions = [{"source": "web", "author": "u", "text": long_text}]
        report = generator.generate_summary(mentions, sample_stats)
        assert "..." in report


class TestGenerateJson:
    """Tests for ReportGenerator.generate_json."""

    def test_returns_valid_json(self, generator, sample_mentions, sample_stats):
        output = generator.generate_json(sample_mentions, sample_stats)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_json_contains_expected_keys(self, generator, sample_mentions, sample_stats):
        output = generator.generate_json(sample_mentions, sample_stats)
        parsed = json.loads(output)
        assert "generated_at" in parsed
        assert "summary" in parsed
        assert "mentions" in parsed

    def test_json_preserves_mention_count(self, generator, sample_mentions, sample_stats):
        output = generator.generate_json(sample_mentions, sample_stats)
        parsed = json.loads(output)
        assert len(parsed["mentions"]) == len(sample_mentions)

    def test_empty_mentions_produces_valid_json(self, generator, sample_stats):
        output = generator.generate_json([], sample_stats)
        parsed = json.loads(output)
        assert parsed["mentions"] == []


class TestSaveReport:
    """Tests for ReportGenerator.save_report."""

    def test_saves_content_to_file(self, generator):
        content = "Test report content"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            tmp_path = f.name

        try:
            generator.save_report(content, tmp_path)
            with open(tmp_path, encoding="utf-8") as f:
                saved = f.read()
            assert saved == content
        finally:
            os.unlink(tmp_path)

    def test_unicode_content_saved_correctly(self, generator):
        content = "Ünïcödë cönteñt 🎯"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            tmp_path = f.name

        try:
            generator.save_report(content, tmp_path)
            with open(tmp_path, encoding="utf-8") as f:
                saved = f.read()
            assert saved == content
        finally:
            os.unlink(tmp_path)

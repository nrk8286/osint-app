"""Unit tests for OSINTMonitor helper methods."""

import asyncio
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from osint_app.core.monitor import OSINTMonitor
from osint_app.models.schemas import Mention, SentimentScore, SourceType


@pytest.fixture
def monitor_no_db():
    """Monitor with no database and no sentiment analyzer."""
    return OSINTMonitor(use_database=False, enable_sentiment=False)


@pytest.fixture
def sample_mention():
    return Mention(
        source=SourceType.TWITTER,
        keyword="python",
        url="https://twitter.com/test/1",
        title="Python is great",
        content="I love python!",
        timestamp=datetime.now(),
        author="user1",
    )


class TestCalculateRelevance:
    """Tests for _calculate_relevance static method."""

    def test_exact_match_single_word(self):
        score = OSINTMonitor._calculate_relevance("python", "python is great")
        assert score > 0.0

    def test_no_match_returns_zero(self):
        score = OSINTMonitor._calculate_relevance("python", "java and ruby are cool")
        assert score == 0.0

    def test_empty_text_returns_zero(self):
        score = OSINTMonitor._calculate_relevance("python", "")
        assert score == 0.0

    def test_high_density_capped_at_one(self):
        # Text is almost entirely the keyword
        score = OSINTMonitor._calculate_relevance("x", "x x x x x x x x x x x x x x x x")
        assert score == 1.0

    def test_score_between_zero_and_one(self):
        score = OSINTMonitor._calculate_relevance("python", "python is a great python language")
        assert 0.0 <= score <= 1.0

    def test_case_insensitive(self):
        score_lower = OSINTMonitor._calculate_relevance("python", "Python rocks")
        score_upper = OSINTMonitor._calculate_relevance("PYTHON", "python rocks")
        assert score_lower > 0.0
        assert score_upper > 0.0


class TestDeduplicate:
    """Tests for _deduplicate static method."""

    def _make_mention(self, url: str, source=SourceType.GOOGLE, keyword="test") -> Mention:
        return Mention(source=source, keyword=keyword, url=url, title="Title", content="Content")

    def test_removes_exact_url_duplicates(self):
        m1 = self._make_mention("https://example.com/1")
        m2 = self._make_mention("https://example.com/1")
        m3 = self._make_mention("https://example.com/2")
        result = OSINTMonitor._deduplicate([m1, m2, m3])
        assert len(result) == 2

    def test_empty_list_stays_empty(self):
        assert OSINTMonitor._deduplicate([]) == []

    def test_no_duplicates_unchanged(self):
        mentions = [self._make_mention(f"https://example.com/{i}") for i in range(5)]
        result = OSINTMonitor._deduplicate(mentions)
        assert len(result) == 5

    def test_dedup_by_content_when_url_empty(self):
        m1 = Mention(source=SourceType.TWITTER, keyword="k", url="", title="A", content="abc")
        m2 = Mention(source=SourceType.TWITTER, keyword="k", url="", title="A", content="abc")
        result = OSINTMonitor._deduplicate([m1, m2])
        assert len(result) == 1

    def test_different_content_no_url_kept_separate(self):
        m1 = Mention(source=SourceType.TWITTER, keyword="k", url="", title="A", content="abc")
        m2 = Mention(source=SourceType.TWITTER, keyword="k", url="", title="B", content="xyz")
        result = OSINTMonitor._deduplicate([m1, m2])
        assert len(result) == 2


class TestFilterMentions:
    """Tests for filter_mentions method."""

    def setup_method(self):
        self.monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        self.monitor.mentions = [
            Mention(
                source=SourceType.TWITTER,
                keyword="python",
                url="https://twitter.com/1",
                title="Tweet 1",
                relevance_score=0.8,
            ),
            Mention(
                source=SourceType.GOOGLE,
                keyword="python",
                url="https://google.com/1",
                title="Google 1",
                relevance_score=0.3,
            ),
            Mention(
                source=SourceType.REDDIT,
                keyword="java",
                url="https://reddit.com/1",
                title="Reddit 1",
                relevance_score=0.5,
            ),
        ]

    def test_filter_by_source(self):
        results = self.monitor.filter_mentions(source="twitter")
        assert all(m.source == SourceType.TWITTER for m in results)
        assert len(results) == 1

    def test_filter_by_keyword(self):
        results = self.monitor.filter_mentions(keyword="java")
        assert all(m.keyword == "java" for m in results)
        assert len(results) == 1

    def test_filter_by_min_relevance(self):
        results = self.monitor.filter_mentions(min_relevance=0.5)
        assert all((m.relevance_score or 0) >= 0.5 for m in results)
        assert len(results) == 2

    def test_filter_combined(self):
        results = self.monitor.filter_mentions(source="twitter", min_relevance=0.5)
        assert len(results) == 1
        assert results[0].source == SourceType.TWITTER

    def test_no_filter_returns_all(self):
        results = self.monitor.filter_mentions()
        assert len(results) == 3


class TestSummaryReport:
    """Tests for summary_report method."""

    def test_empty_mentions_returns_empty_dict(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        report = monitor.summary_report()
        assert report == {}

    def test_report_keys_present(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.mentions = [
            Mention(source=SourceType.TWITTER, keyword="test", url="https://t.co/1"),
            Mention(source=SourceType.GOOGLE, keyword="test", url="https://g.co/1"),
        ]
        monitor.search_history = [{"keyword": "test", "timestamp": datetime.now().isoformat()}]
        report = monitor.summary_report()
        assert "total_mentions" in report
        assert "by_source" in report
        assert "by_keyword" in report
        assert report["total_mentions"] == 2

    def test_report_counts_by_source(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.mentions = [
            Mention(source=SourceType.TWITTER, keyword="k", url="https://t.co/1"),
            Mention(source=SourceType.TWITTER, keyword="k", url="https://t.co/2"),
            Mention(source=SourceType.GOOGLE, keyword="k", url="https://g.co/1"),
        ]
        report = monitor.summary_report()
        assert report["by_source"]["twitter"] == 2
        assert report["by_source"]["google"] == 1


class TestClearMentions:
    """Tests for clear_mentions method."""

    def test_clears_mentions_and_history(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.mentions = [
            Mention(source=SourceType.TWITTER, keyword="test", url="https://t.co/1")
        ]
        monitor.search_history = [{"keyword": "test"}]
        monitor.clear_mentions()
        assert monitor.mentions == []
        assert monitor.search_history == []


class TestGetStats:
    """Tests for get_stats method."""

    def test_without_db_returns_error(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        result = monitor.get_stats()
        assert "error" in result

    def test_with_db_returns_stats(self):
        from osint_app.storage.database import DatabaseStorage

        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.db = DatabaseStorage(db_url="sqlite:///:memory:")
        stats = monitor.get_stats(days=7)
        assert "total_mentions" in stats


class TestCollectMentions:
    """Tests for collect_mentions async method."""

    @pytest.mark.asyncio
    async def test_collect_returns_mentions(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)

        # Mock all sources to return no mentions
        for source in monitor.sources.values():
            source.enabled = False

        mentions = await monitor.collect_mentions(keyword="test")
        assert isinstance(mentions, list)

    @pytest.mark.asyncio
    async def test_collect_deduplicates(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)

        # Patch search_all_sources to return duplicates
        dup = Mention(source=SourceType.GOOGLE, keyword="test", url="https://example.com")
        monitor.search_all_sources = AsyncMock(return_value=[dup, dup])

        mentions = await monitor.collect_mentions(keyword="test")
        assert len(mentions) == 1

    @pytest.mark.asyncio
    async def test_collect_scores_relevance(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)

        m = Mention(
            source=SourceType.GOOGLE,
            keyword="python",
            url="https://example.com",
            title="python guide",
            content="python is cool",
        )
        monitor.search_all_sources = AsyncMock(return_value=[m])

        mentions = await monitor.collect_mentions(keyword="python")
        assert mentions[0].relevance_score is not None
        assert mentions[0].relevance_score > 0

    @pytest.mark.asyncio
    async def test_collect_adds_to_search_history(self):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.search_all_sources = AsyncMock(return_value=[])

        await monitor.collect_mentions(keyword="osint")
        assert len(monitor.search_history) == 1
        assert monitor.search_history[0]["keyword"] == "osint"


class TestSaveToJson:
    """Tests for save_to_json method."""

    def test_no_mentions_does_not_create_file(self, tmp_path):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        filename = str(tmp_path / "out.json")
        monitor.save_to_json(filename)
        assert not os.path.exists(filename)

    def test_saves_valid_json_file(self, tmp_path):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.mentions = [
            Mention(source=SourceType.TWITTER, keyword="test", url="https://t.co/1")
        ]
        filename = str(tmp_path / "out.json")
        monitor.save_to_json(filename)
        assert os.path.exists(filename)
        with open(filename) as f:
            data = json.load(f)
        assert "mentions" in data
        assert "metadata" in data
        assert len(data["mentions"]) == 1

    def test_auto_generates_filename_when_none(self, tmp_path, monkeypatch):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.mentions = [
            Mention(source=SourceType.GOOGLE, keyword="k", url="https://g.co/1")
        ]
        monkeypatch.chdir(tmp_path)
        monitor.save_to_json()
        json_files = list(tmp_path.glob("mentions_*.json"))
        assert len(json_files) == 1


class TestSaveToCsv:
    """Tests for save_to_csv method."""

    def test_no_mentions_does_not_create_file(self, tmp_path):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        filename = str(tmp_path / "out.csv")
        monitor.save_to_csv(filename)
        assert not os.path.exists(filename)

    def test_saves_csv_file(self, tmp_path):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.mentions = [
            Mention(source=SourceType.REDDIT, keyword="k", url="https://reddit.com/1")
        ]
        filename = str(tmp_path / "out.csv")
        monitor.save_to_csv(filename)
        assert os.path.exists(filename)
        content = open(filename).read()
        assert "source" in content  # CSV header

    def test_auto_generates_filename_when_none(self, tmp_path, monkeypatch):
        monitor = OSINTMonitor(use_database=False, enable_sentiment=False)
        monitor.mentions = [
            Mention(source=SourceType.GOOGLE, keyword="k", url="https://g.co/1")
        ]
        monkeypatch.chdir(tmp_path)
        monitor.save_to_csv()
        csv_files = list(tmp_path.glob("mentions_*.csv"))
        assert len(csv_files) == 1

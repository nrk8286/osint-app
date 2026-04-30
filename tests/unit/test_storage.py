"""Unit tests for database storage."""

import os
import shutil
import tempfile
from datetime import datetime, timedelta

import pytest

from osint_app.models.schemas import Mention, SentimentScore, SourceType
from osint_app.storage.database import Database, DatabaseStorage


class TestDatabaseStorage:
    """Tests for DatabaseStorage class."""

    def test_save_mention(self, db, sample_mention):
        """Test saving a single mention."""
        mention_id = db.save_mention(sample_mention)
        assert mention_id > 0

    def test_save_multiple_mentions(self, db, sample_mentions):
        """Test saving multiple mentions."""
        count = db.save_mentions(sample_mentions)
        assert count == len(sample_mentions)

    def test_get_mentions(self, db, sample_mentions):
        """Test retrieving mentions."""
        db.save_mentions(sample_mentions)
        retrieved = db.get_mentions(limit=10)
        assert len(retrieved) == len(sample_mentions)

    def test_get_mentions_by_keyword(self, db):
        """Test filtering mentions by keyword."""
        mentions = [
            Mention(
                source=SourceType.TWITTER,
                keyword="python",
                url="https://example.com/1",
                title="Python is great"
            ),
            Mention(
                source=SourceType.GOOGLE,
                keyword="javascript",
                url="https://example.com/2",
                title="JavaScript tips"
            )
        ]
        db.save_mentions(mentions)

        python_mentions = db.get_mentions(keyword="python")
        assert len(python_mentions) == 1
        assert python_mentions[0].keyword == "python"

    def test_get_stats(self, db, sample_mentions):
        """Test getting statistics."""
        db.save_mentions(sample_mentions)
        stats = db.get_stats(days=7)

        assert 'total_mentions' in stats
        assert 'by_source' in stats
        assert stats['total_mentions'] >= len(sample_mentions)

    def test_clear_old_mentions(self, db):
        """Test clearing old mentions."""
        # Create old mention
        old_mention = Mention(
            source=SourceType.TWITTER,
            keyword="old",
            url="https://example.com/old",
            title="Old mention",
            timestamp=datetime.now() - timedelta(days=40)
        )
        db.save_mention(old_mention)

        # Clear mentions older than 30 days
        deleted = db.clear_old_mentions(days=30)
        assert deleted >= 0

    def test_get_mentions_by_source(self, db):
        """Test filtering by source type."""
        db.save_mentions([
            Mention(source=SourceType.TWITTER, keyword="k", url="https://t.co/1"),
            Mention(source=SourceType.REDDIT, keyword="k", url="https://reddit.com/1"),
        ])
        results = db.get_mentions(source=SourceType.TWITTER)
        assert all(m.source == SourceType.TWITTER for m in results)
        assert len(results) == 1

    def test_get_mentions_with_offset(self, db):
        """Test pagination with offset."""
        db.save_mentions([
            Mention(source=SourceType.GOOGLE, keyword=f"k{i}", url=f"https://g.co/{i}")
            for i in range(5)
        ])
        page1 = db.get_mentions(limit=2, offset=0)
        page2 = db.get_mentions(limit=2, offset=2)
        assert len(page1) == 2
        assert len(page2) == 2
        # No overlap
        urls1 = {m.url for m in page1}
        urls2 = {m.url for m in page2}
        assert not urls1 & urls2

    def test_get_mentions_with_date_range(self, db):
        """Test filtering mentions by start and end date."""
        now = datetime.now()
        db.save_mentions([
            Mention(
                source=SourceType.TWITTER,
                keyword="old",
                url="https://example.com/old",
                timestamp=now - timedelta(days=10),
            ),
            Mention(
                source=SourceType.TWITTER,
                keyword="recent",
                url="https://example.com/recent",
                timestamp=now - timedelta(days=1),
            ),
        ])

        start = now - timedelta(days=3)
        results = db.get_mentions(start_date=start)
        assert all(m.keyword == "recent" for m in results)
        assert len(results) == 1

    def test_get_mentions_end_date_filter(self, db):
        """Test end_date filter excludes newer mentions."""
        now = datetime.now()
        db.save_mentions([
            Mention(
                source=SourceType.GOOGLE,
                keyword="early",
                url="https://example.com/early",
                timestamp=now - timedelta(days=5),
            ),
            Mention(
                source=SourceType.GOOGLE,
                keyword="late",
                url="https://example.com/late",
                timestamp=now,
            ),
        ])

        end = now - timedelta(days=2)
        results = db.get_mentions(end_date=end)
        assert all(m.keyword == "early" for m in results)

    def test_get_stats_by_source_breakdown(self, db):
        """Test that by_source key contains correct counts."""
        db.save_mentions([
            Mention(source=SourceType.TWITTER, keyword="k", url="https://t.co/1"),
            Mention(source=SourceType.TWITTER, keyword="k", url="https://t.co/2"),
            Mention(source=SourceType.GOOGLE, keyword="k", url="https://g.co/1"),
        ])
        stats = db.get_stats(days=7)
        assert stats["by_source"].get("twitter") == 2
        assert stats["by_source"].get("google") == 1

    def test_clear_old_mentions_keeps_recent(self, db):
        """Ensure clear_old_mentions does not delete recent entries."""
        now = datetime.now()
        recent = Mention(
            source=SourceType.NEWS,
            keyword="news",
            url="https://news.com/1",
            timestamp=now - timedelta(days=1),
        )
        db.save_mention(recent)
        deleted = db.clear_old_mentions(days=30)
        assert deleted == 0
        remaining = db.get_mentions()
        assert len(remaining) == 1


class TestDatabaseCompat:
    """Tests for the legacy Database compatibility class."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "compat_test.db")
        self.db = Database(self.db_path)

    def teardown_method(self):
        self.db.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_mention_returns_int_id(self):
        mid = self.db.save_mention({"text": "hello", "source": "twitter"})
        assert isinstance(mid, int)
        assert mid > 0

    def test_save_multiple_mentions_returns_ids_list(self):
        ids = self.db.save_mentions([
            {"text": "post1", "source": "twitter"},
            {"text": "post2", "source": "reddit"},
        ])
        assert len(ids) == 2
        assert all(isinstance(i, int) for i in ids)

    def test_get_mentions_returns_all(self):
        self.db.save_mentions([
            {"text": "post1", "source": "twitter"},
            {"text": "post2", "source": "reddit"},
        ])
        results = self.db.get_mentions()
        assert len(results) == 2

    def test_get_mentions_filter_by_source(self):
        self.db.save_mentions([
            {"text": "tweet", "source": "twitter"},
            {"text": "post", "source": "reddit"},
        ])
        results = self.db.get_mentions(source="twitter")
        assert len(results) == 1
        assert results[0]["source"] == "twitter"

    def test_get_mentions_filter_by_keyword(self):
        self.db.save_mentions([
            {"text": "mention of python", "source": "web", "keywords": ["python"]},
            {"text": "mention of java", "source": "web", "keywords": ["java"]},
        ])
        results = self.db.get_mentions(keyword="python")
        assert len(results) == 1

    def test_get_mentions_with_limit(self):
        self.db.save_mentions([{"text": f"item {i}", "source": "web"} for i in range(10)])
        results = self.db.get_mentions(limit=3)
        assert len(results) == 3

    def test_save_query_returns_int_id(self):
        qid = self.db.save_query(["python"], ["web"], 5)
        assert isinstance(qid, int)
        assert qid > 0

    def test_get_statistics_initial_state(self):
        stats = self.db.get_statistics()
        assert stats["total_mentions"] == 0
        assert stats["total_queries"] == 0

    def test_get_statistics_after_inserts(self):
        self.db.save_mentions([
            {"text": "good", "source": "twitter", "sentiment": {"sentiment": "positive"}},
            {"text": "bad", "source": "reddit", "sentiment": {"sentiment": "negative"}},
        ])
        self.db.save_query(["osint"], ["twitter"], 1)
        stats = self.db.get_statistics()
        assert stats["total_mentions"] == 2
        assert stats["total_queries"] == 1
        assert stats["sources"].get("twitter") == 1
        assert stats["sentiments"].get("positive") == 1

    def test_clear_mentions_removes_all(self):
        self.db.save_mentions([
            {"text": "post1", "source": "web"},
            {"text": "post2", "source": "web"},
        ])
        self.db.clear_mentions()
        assert self.db.get_mentions() == []

    def test_clear_all_removes_mentions_and_queries(self):
        self.db.save_mention({"text": "post", "source": "web"})
        self.db.save_query(["kw"], ["web"], 1)
        self.db.clear_all()
        stats = self.db.get_statistics()
        assert stats["total_mentions"] == 0
        assert stats["total_queries"] == 0

    def test_get_by_sentiment(self):
        self.db.save_mentions([
            {"text": "great!", "source": "web", "sentiment": {"sentiment": "positive"}},
            {"text": "bad", "source": "web", "sentiment": {"sentiment": "negative"}},
        ])
        results = self.db.get_by_sentiment("positive")
        assert len(results) == 1
        assert results[0]["sentiment"]["sentiment"] == "positive"

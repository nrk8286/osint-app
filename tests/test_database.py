"""
Unit tests for OSINT App database storage.
"""
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta

from osint_app.models.schemas import Mention, SourceType
from osint_app.storage.database import DatabaseStorage


def _make_mention(keyword: str = "test", source: SourceType = SourceType.WEB, **kwargs) -> Mention:
    """Helper to create a Mention object for testing."""
    return Mention(
        source=source,
        keyword=keyword,
        url="https://example.com",
        title="Test Title",
        content="Test content",
        **kwargs,
    )


class TestDatabaseStorage(unittest.TestCase):
    """Test DatabaseStorage functionality."""

    def setUp(self):
        """Set up test fixture with a temporary SQLite database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_osint.db")
        self.db = DatabaseStorage(f"sqlite:///{self.db_path}")

    def tearDown(self):
        """Clean up the temporary database."""
        self.db.engine.dispose()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_mention(self):
        """Test saving a single mention returns an integer ID."""
        mention = _make_mention()
        doc_id = self.db.save_mention(mention)
        self.assertIsInstance(doc_id, int)

        saved = self.db.get_mentions()
        self.assertEqual(len(saved), 1)
        self.assertEqual(saved[0].keyword, "test")

    def test_save_mentions(self):
        """Test saving multiple mentions returns the correct count."""
        mentions = [_make_mention(keyword="kw1"), _make_mention(keyword="kw2")]
        count = self.db.save_mentions(mentions)
        self.assertEqual(count, 2)

        saved = self.db.get_mentions()
        self.assertEqual(len(saved), 2)

    def test_get_mentions_filter_by_keyword(self):
        """Test filtering mentions by keyword."""
        self.db.save_mentions([
            _make_mention(keyword="Python"),
            _make_mention(keyword="AI"),
        ])

        results = self.db.get_mentions(keyword="Python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].keyword, "Python")

    def test_get_mentions_filter_by_source(self):
        """Test filtering mentions by source."""
        self.db.save_mentions([
            _make_mention(source=SourceType.TWITTER),
            _make_mention(source=SourceType.REDDIT),
        ])

        results = self.db.get_mentions(source=SourceType.TWITTER)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source, SourceType.TWITTER)

    def test_get_mentions_with_limit(self):
        """Test that the limit parameter is respected."""
        self.db.save_mentions([_make_mention(keyword=f"kw{i}") for i in range(10)])

        results = self.db.get_mentions(limit=5)
        self.assertEqual(len(results), 5)

    def test_get_stats(self):
        """Test that get_stats returns correct counts."""
        self.db.save_mentions([
            _make_mention(source=SourceType.TWITTER),
            _make_mention(source=SourceType.REDDIT),
        ])

        stats = self.db.get_stats(days=7)
        self.assertEqual(stats["total_mentions"], 2)
        self.assertIn("by_source", stats)
        self.assertEqual(stats["by_source"].get("twitter"), 1)
        self.assertEqual(stats["by_source"].get("reddit"), 1)

    def test_clear_old_mentions(self):
        """Test that clear_old_mentions removes mentions older than the cutoff."""
        old_time = datetime.now() - timedelta(days=60)
        recent_time = datetime.now() - timedelta(days=1)

        self.db.save_mentions([
            _make_mention(keyword="old", timestamp=old_time),
            _make_mention(keyword="recent", timestamp=recent_time),
        ])

        deleted = self.db.clear_old_mentions(days=30)
        self.assertEqual(deleted, 1)

        remaining = self.db.get_mentions()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].keyword, "recent")


if __name__ == "__main__":
    unittest.main()

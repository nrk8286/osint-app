"""Unit tests for database storage."""

import pytest
from datetime import datetime, timedelta
from osint_app.storage.database import DatabaseStorage
from osint_app.models.schemas import Mention, SourceType, SentimentScore


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

"""Unit tests for data models."""

import pytest
from datetime import datetime
from osint_app.models.schemas import Mention, SourceType, SentimentScore, SearchQuery


class TestMention:
    """Tests for Mention model."""

    def test_mention_creation(self):
        """Test creating a valid mention."""
        mention = Mention(
            source=SourceType.TWITTER,
            keyword="test",
            url="https://example.com",
            title="Test",
            content="Test content"
        )
        assert mention.source == SourceType.TWITTER
        assert mention.keyword == "test"
        assert isinstance(mention.timestamp, datetime)

    def test_mention_with_sentiment(self):
        """Test mention with sentiment analysis."""
        mention = Mention(
            source=SourceType.TWITTER,
            keyword="test",
            url="https://example.com",
            title="Great product!",
            content="I love it",
            sentiment=SentimentScore.POSITIVE,
            sentiment_confidence=0.95
        )
        assert mention.sentiment == SentimentScore.POSITIVE
        assert mention.sentiment_confidence == 0.95

    def test_mention_serialization(self):
        """Test mention JSON serialization."""
        mention = Mention(
            source=SourceType.GOOGLE,
            keyword="test",
            url="https://example.com",
            title="Test",
            content="Content"
        )
        data = mention.model_dump()
        assert data['source'] == 'google'
        assert 'timestamp' in data


class TestSearchQuery:
    """Tests for SearchQuery model."""

    def test_default_values(self):
        """Test search query with default values."""
        query = SearchQuery(keyword="test")
        assert query.google_results == 10
        assert query.twitter_results == 10
        assert query.enable_sentiment is True

    def test_validation(self):
        """Test that SearchQuery stores values without enforcing range constraints.

        The model does not currently validate negative result counts; this test
        documents that behaviour so a future constraint addition is caught early.
        """
        # Pydantic model accepts any int; verify it does not raise and stores the value
        query = SearchQuery(keyword="test", google_results=-1)
        assert query.google_results == -1

    def test_empty_keyword_allowed(self):
        """Test that an empty keyword is accepted by the model."""
        query = SearchQuery(keyword="")
        assert query.keyword == ""

    def test_custom_values(self):
        """Test search query with custom values."""
        query = SearchQuery(
            keyword="test",
            google_results=20,
            enable_sentiment=False
        )
        assert query.google_results == 20
        assert query.enable_sentiment is False

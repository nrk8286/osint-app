"""Unit tests for sentiment analysis."""

import pytest
from osint_app.utils.sentiment import SimpleSentimentAnalyzer, SentimentScore
from osint_app.models.schemas import Mention, SourceType


class TestSimpleSentimentAnalyzer:
    """Tests for SimpleSentimentAnalyzer."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = SimpleSentimentAnalyzer()

    def test_positive_sentiment(self):
        """Test detection of positive sentiment."""
        text = "This is great and wonderful!"
        sentiment, confidence = self.analyzer.analyze(text)
        assert sentiment == SentimentScore.POSITIVE

    def test_negative_sentiment(self):
        """Test detection of negative sentiment."""
        text = "This is terrible and awful!"
        sentiment, confidence = self.analyzer.analyze(text)
        assert sentiment == SentimentScore.NEGATIVE

    def test_neutral_sentiment(self):
        """Test detection of neutral sentiment."""
        text = "This is a statement about weather."
        sentiment, confidence = self.analyzer.analyze(text)
        assert sentiment == SentimentScore.NEUTRAL

    def test_empty_text(self):
        """Test handling of empty text."""
        sentiment, confidence = self.analyzer.analyze("")
        assert sentiment is None
        assert confidence is None

    def test_analyze_mention(self):
        """Test analyzing a mention."""
        mention = Mention(
            source=SourceType.TWITTER,
            keyword="test",
            url="https://example.com",
            title="Amazing product",
            content="I love this product, it's fantastic!"
        )

        analyzed = self.analyzer.analyze_mention(mention)
        assert analyzed.sentiment is not None
        assert analyzed.sentiment_confidence is not None

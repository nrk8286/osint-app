"""Unit tests for sentiment analysis."""

import pytest
from osint_app.utils.sentiment import SimpleSentimentAnalyzer, SentimentScore, get_sentiment_analyzer
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

    def test_mixed_positive_negative_resolves_to_neutral(self):
        """Equal positive and negative counts → neutral."""
        text = "good bad"  # one positive, one negative
        sentiment, confidence = self.analyzer.analyze(text)
        assert sentiment == SentimentScore.NEUTRAL
        assert confidence == 0.5

    def test_mostly_positive_words(self):
        """Heavily positive text should yield positive sentiment."""
        text = "great excellent amazing wonderful awesome love"
        sentiment, confidence = self.analyzer.analyze(text)
        assert sentiment == SentimentScore.POSITIVE
        assert confidence > 0.6

    def test_mostly_negative_words(self):
        """Heavily negative text should yield negative sentiment."""
        text = "terrible horrible awful hate disappointing useless"
        sentiment, confidence = self.analyzer.analyze(text)
        assert sentiment == SentimentScore.NEGATIVE
        assert confidence > 0.6

    def test_confidence_is_numeric(self):
        """Confidence value should be a float."""
        _, confidence = self.analyzer.analyze("This is good")
        assert isinstance(confidence, float)


class TestGetSentimentAnalyzer:
    """Tests for the get_sentiment_analyzer factory function."""

    def test_returns_simple_analyzer_when_transformers_disabled(self):
        analyzer = get_sentiment_analyzer(use_transformers=False)
        assert isinstance(analyzer, SimpleSentimentAnalyzer)

    def test_returns_simple_analyzer_when_transformers_unavailable(self):
        from unittest.mock import patch

        with patch("osint_app.utils.sentiment.TRANSFORMERS_AVAILABLE", False):
            analyzer = get_sentiment_analyzer(use_transformers=True)
        assert isinstance(analyzer, SimpleSentimentAnalyzer)

"""Sentiment analysis utilities."""

import logging
from typing import Any, Optional, Tuple, Union

try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from osint_app.models.schemas import Mention, SentimentScore


class SentimentAnalyzer:
    """Sentiment analysis using transformer models."""

    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        """Initialize sentiment analyzer.

        Args:
            model_name: Hugging Face model name for sentiment analysis
        """
        self.model_name = model_name
        self.pipeline: Optional[Any] = None
        self.enabled = TRANSFORMERS_AVAILABLE

        if self.enabled:
            try:
                self.pipeline = pipeline("sentiment-analysis", model=model_name)
            except Exception as e:
                logging.warning(f"Failed to load sentiment model: {e}")
                self.enabled = False

    def is_available(self) -> bool:
        """Check if sentiment analysis is available."""
        return self.enabled and self.pipeline is not None

    def analyze(self, text: str) -> Tuple[Optional[SentimentScore], Optional[float]]:
        """Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (sentiment, confidence_score)
        """
        if not self.is_available() or not text:
            return None, None

        try:
            # Truncate text to model's max length (512 tokens for BERT-based models)
            text = text[:512]

            # The is_available() check at the top of this method guarantees pipeline is not None
            assert self.pipeline is not None
            result = self.pipeline(text)[0]
            label = result["label"].upper()
            score = result["score"]

            # Map model output to our sentiment categories
            sentiment_map = {
                "POSITIVE": SentimentScore.POSITIVE,
                "NEGATIVE": SentimentScore.NEGATIVE,
                "NEUTRAL": SentimentScore.NEUTRAL,
                "MIXED": SentimentScore.MIXED,
            }

            sentiment = sentiment_map.get(label, SentimentScore.NEUTRAL)
            return sentiment, score

        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            return None, None

    def analyze_mention(self, mention: Mention) -> Mention:
        """Add sentiment analysis to a mention.

        Args:
            mention: Mention to analyze

        Returns:
            Mention with sentiment fields populated
        """
        if not self.is_available():
            return mention

        # Analyze title and content combined
        text = f"{mention.title} {mention.content}"
        sentiment, confidence = self.analyze(text)

        mention.sentiment = sentiment
        mention.sentiment_confidence = confidence

        return mention


# Lightweight sentiment analysis without transformers (fallback)
class SimpleSentimentAnalyzer:
    """Simple rule-based sentiment analysis as fallback."""

    def __init__(self):
        """Initialize simple sentiment analyzer."""
        self.positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "love",
            "best",
            "awesome",
            "happy",
            "perfect",
            "beautiful",
        }
        self.negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "worst",
            "hate",
            "poor",
            "disappointing",
            "sad",
            "angry",
            "annoying",
            "useless",
        }

    def analyze(self, text: str) -> Tuple[Optional[SentimentScore], Optional[float]]:
        """Analyze sentiment using word matching.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (sentiment, confidence_score)
        """
        if not text:
            return None, None

        text_lower = text.lower()
        words = text_lower.split()

        pos_count = sum(1 for word in words if word in self.positive_words)
        neg_count = sum(1 for word in words if word in self.negative_words)

        if pos_count == 0 and neg_count == 0:
            return SentimentScore.NEUTRAL, 0.5

        total = pos_count + neg_count
        pos_ratio = pos_count / total if total > 0 else 0.5

        if pos_ratio > 0.6:
            return SentimentScore.POSITIVE, pos_ratio
        elif pos_ratio < 0.4:
            return SentimentScore.NEGATIVE, 1 - pos_ratio
        else:
            return SentimentScore.NEUTRAL, 0.5

    def analyze_mention(self, mention: Mention) -> Mention:
        """Add sentiment analysis to a mention.

        Args:
            mention: Mention to analyze

        Returns:
            Mention with sentiment fields populated
        """
        text = f"{mention.title} {mention.content}"
        sentiment, confidence = self.analyze(text)

        mention.sentiment = sentiment
        mention.sentiment_confidence = confidence

        return mention


def get_sentiment_analyzer(
    use_transformers: bool = True,
) -> Union["SentimentAnalyzer", "SimpleSentimentAnalyzer"]:
    """Factory function to get appropriate sentiment analyzer.

    Args:
        use_transformers: Whether to use transformer-based analysis

    Returns:
        SentimentAnalyzer or SimpleSentimentAnalyzer instance
    """
    if use_transformers and TRANSFORMERS_AVAILABLE:
        analyzer = SentimentAnalyzer()
        if analyzer.is_available():
            return analyzer

    # Fallback to simple analyzer
    return SimpleSentimentAnalyzer()

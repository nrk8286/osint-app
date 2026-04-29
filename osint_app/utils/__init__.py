"""Utility functions and helpers."""

from typing import Optional

from osint_app.models.schemas import SentimentScore
from osint_app.utils.sentiment import SimpleSentimentAnalyzer


def analyze_sentiment(text: str) -> Optional[SentimentScore]:
    """Analyze sentiment of text using simple rule-based analysis.

    Args:
        text: Text to analyze

    Returns:
        SentimentScore or None if text is empty
    """
    analyzer = SimpleSentimentAnalyzer()
    sentiment, _ = analyzer.analyze(text)
    return sentiment


def format_engagement(likes: int = 0, shares: int = 0, comments: int = 0) -> Optional[int]:
    """Return total engagement count.

    Args:
        likes: Number of likes
        shares: Number of shares
        comments: Number of comments

    Returns:
        Total engagement count, or None if zero
    """
    total = likes + shares + comments
    return total if total > 0 else None

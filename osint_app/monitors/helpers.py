"""Local helpers for the legacy synthetic monitors; no external model calls."""

from typing import Dict, Optional

from osint_app.utils.sentiment import SimpleSentimentAnalyzer


def analyze_sentiment(text: str) -> Optional[str]:
    sentiment, _ = SimpleSentimentAnalyzer().analyze(text)
    return sentiment.value if sentiment is not None else None


def format_engagement(likes: int = 0, shares: int = 0, comments: int = 0) -> Dict[str, int]:
    return {
        "likes": likes,
        "shares": shares,
        "comments": comments,
        "total": likes + shares + comments,
    }

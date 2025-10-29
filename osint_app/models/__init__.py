"""Data models for OSINT app."""

from datetime import datetime
from typing import Optional, List, Dict, Any


class Mention:
    """Represents a social media mention."""
    
    def __init__(
        self,
        platform: str,
        content: str,
        author: str,
        url: str,
        timestamp: datetime,
        engagement: Optional[Dict[str, int]] = None,
        sentiment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.platform = platform
        self.content = content
        self.author = author
        self.url = url
        self.timestamp = timestamp
        self.engagement = engagement or {}
        self.sentiment = sentiment
        self.metadata = metadata or {}
    
    def to_dict(self) -> dict:
        """Convert mention to dictionary."""
        return {
            'platform': self.platform,
            'content': self.content,
            'author': self.author,
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'engagement': self.engagement,
            'sentiment': self.sentiment,
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        return f"Mention(platform={self.platform}, author={self.author}, timestamp={self.timestamp})"


class SearchQuery:
    """Represents a search query for monitoring."""
    
    def __init__(
        self,
        keywords: List[str],
        platforms: List[str],
        language: Optional[str] = None,
        max_results: int = 100
    ):
        self.keywords = keywords
        self.platforms = platforms
        self.language = language
        self.max_results = max_results
    
    def to_dict(self) -> dict:
        """Convert query to dictionary."""
        return {
            'keywords': self.keywords,
            'platforms': self.platforms,
            'language': self.language,
            'max_results': self.max_results
        }
    
    def __repr__(self) -> str:
        return f"SearchQuery(keywords={self.keywords}, platforms={self.platforms})"

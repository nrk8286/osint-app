"""Pydantic schemas shared across the OSINT monitoring platform."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SourceType(str, Enum):
    """Supported data source types."""

    GOOGLE = "google"
    TWITTER = "twitter"
    REDDIT = "reddit"
    NEWS = "news"
    GITHUB = "github"
    WEB = "web"
    RSS = "rss"


class SentimentScore(str, Enum):
    """Sentiment classification labels."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class Mention(BaseModel):
    """A single mention / search result collected from any source."""

    model_config = ConfigDict(extra="allow")

    id: Optional[str] = None
    source: SourceType
    keyword: str
    url: str = ""
    title: str = ""
    content: str = ""
    timestamp: datetime = Field(default_factory=datetime.now)
    author: Optional[str] = None
    sentiment: Optional[SentimentScore] = None
    sentiment_confidence: Optional[float] = None
    language: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: Optional[float] = None
    engagement: Optional[int] = None


class SearchQuery(BaseModel):
    """Parameters for a search request."""

    keyword: str = Field(min_length=1)
    google_results: int = Field(default=10, ge=0)
    twitter_results: int = Field(default=10, ge=0)
    reddit_results: int = Field(default=10, ge=0)
    news_results: int = Field(default=10, ge=0)
    github_results: int = Field(default=10, ge=0)

    # Per-source toggles used by the API
    enable_google: bool = True
    enable_twitter: bool = True
    enable_reddit: bool = True
    enable_news: bool = True
    enable_github: bool = True
    enable_sentiment: bool = True


class ReconResult(BaseModel):
    """Result from a reconnaissance operation (DNS, IP, headers)."""

    model_config = ConfigDict(extra="allow")

    target: str
    recon_type: str  # "dns", "ip_info", "headers"
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)

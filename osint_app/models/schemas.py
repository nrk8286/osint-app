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
    HACKERNEWS = "hackernews"
    PASTEBIN = "pastebin"
    YOUTUBE = "youtube"
    SHODAN = "shodan"
    TELEGRAM = "telegram"


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

    keyword: str
    google_results: int = 10
    twitter_results: int = 10
    reddit_results: int = 10
    news_results: int = 10
    github_results: int = 10
    hackernews_results: int = 10
    pastebin_results: int = 10
    youtube_results: int = 10
    shodan_results: int = 10
    telegram_results: int = 10
    rss_results: int = 10

    # Per-source toggles used by the API
    enable_google: bool = True
    enable_twitter: bool = True
    enable_reddit: bool = True
    enable_news: bool = True
    enable_github: bool = True
    enable_hackernews: bool = True
    enable_pastebin: bool = True
    enable_youtube: bool = True
    enable_shodan: bool = True
    enable_telegram: bool = True
    enable_rss: bool = True
    enable_sentiment: bool = True


class ReconResult(BaseModel):
    """Result from a reconnaissance operation (DNS, IP, headers)."""

    model_config = ConfigDict(extra="allow")

    target: str
    recon_type: str  # "dns", "ip_info", "headers"
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(default_factory=dict)

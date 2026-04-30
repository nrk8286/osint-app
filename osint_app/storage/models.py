"""Database models using SQLAlchemy."""

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class SourceTypeDB(str, enum.Enum):
    """Source types for database."""

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


class SentimentDB(str, enum.Enum):
    """Sentiment types for database."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class MentionDB(Base):
    """Database model for mentions."""

    __tablename__ = "mentions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sentiment_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Mention(id={self.id}, source={self.source}, keyword={self.keyword})>"


class AgentLogDB(Base):
    """Database model for agent activity log events."""

    __tablename__ = "agent_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return (
            f"<AgentLog(id={self.id}, event_type={self.event_type}, source={self.source})>"
        )


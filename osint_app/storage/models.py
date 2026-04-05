"""Database models using SQLAlchemy."""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, Float, Integer, JSON, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import enum


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class SourceTypeDB(str, enum.Enum):
    """Source types for database."""

    GOOGLE = "google"
    TWITTER = "twitter"
    REDDIT = "reddit"
    NEWS = "news"
    WEB = "web"
    RSS = "rss"


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
    source: Mapped[str] = mapped_column(SQLEnum(SourceTypeDB), nullable=False, index=True)
    keyword: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
    sentiment_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self) -> str:
        return f"<Mention(id={self.id}, source={self.source}, keyword={self.keyword})>"

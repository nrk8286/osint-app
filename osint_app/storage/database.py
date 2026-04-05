"""Database storage backend implementation."""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from osint_app.storage.models import Base, MentionDB
from osint_app.models.schemas import Mention, SourceType, SentimentScore
from osint_app.core.config import config


class DatabaseStorage:
    """Database storage backend using SQLAlchemy."""

    def __init__(self, db_url: Optional[str] = None):
        """Initialize database storage.

        Args:
            db_url: Database URL (defaults to config value)
        """
        self.db_url = db_url or config.database.url
        self.engine = create_engine(
            self.db_url,
            echo=config.database.echo,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        Base.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self):
        """Get a database session context manager."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save_mention(self, mention: Mention) -> int:
        """Save a single mention to database.

        Args:
            mention: Mention object to save

        Returns:
            ID of saved mention
        """
        with self.get_session() as session:
            db_mention = MentionDB(
                source=mention.source.value,
                keyword=mention.keyword,
                url=mention.url,
                title=mention.title,
                content=mention.content,
                timestamp=mention.timestamp,
                author=mention.author,
                sentiment=mention.sentiment.value if mention.sentiment else None,
                sentiment_confidence=mention.sentiment_confidence,
                language=mention.language,
                metadata=mention.metadata,
            )
            session.add(db_mention)
            session.flush()
            return db_mention.id

    def save_mentions(self, mentions: List[Mention]) -> int:
        """Save multiple mentions to database.

        Args:
            mentions: List of mentions to save

        Returns:
            Number of mentions saved
        """
        with self.get_session() as session:
            db_mentions = [
                MentionDB(
                    source=m.source.value,
                    keyword=m.keyword,
                    url=m.url,
                    title=m.title,
                    content=m.content,
                    timestamp=m.timestamp,
                    author=m.author,
                    sentiment=m.sentiment.value if m.sentiment else None,
                    sentiment_confidence=m.sentiment_confidence,
                    language=m.language,
                    metadata=m.metadata,
                )
                for m in mentions
            ]
            session.add_all(db_mentions)
            return len(db_mentions)

    def get_mentions(
        self,
        keyword: Optional[str] = None,
        source: Optional[SourceType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Mention]:
        """Retrieve mentions with filtering.

        Args:
            keyword: Filter by keyword
            source: Filter by source type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of mentions
        """
        with self.get_session() as session:
            query = select(MentionDB)

            if keyword:
                query = query.where(MentionDB.keyword == keyword)
            if source:
                query = query.where(MentionDB.source == source.value)
            if start_date:
                query = query.where(MentionDB.timestamp >= start_date)
            if end_date:
                query = query.where(MentionDB.timestamp <= end_date)

            query = query.order_by(MentionDB.timestamp.desc())
            query = query.offset(offset).limit(limit)

            results = session.execute(query).scalars().all()

            return [self._db_to_mention(m) for m in results]

    def get_stats(self, days: int = 7) -> dict:
        """Get statistics for recent mentions.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with statistics
        """
        with self.get_session() as session:
            cutoff = datetime.now() - timedelta(days=days)

            total = session.execute(
                select(func.count(MentionDB.id)).where(MentionDB.timestamp >= cutoff)
            ).scalar()

            by_source = session.execute(
                select(MentionDB.source, func.count(MentionDB.id))
                .where(MentionDB.timestamp >= cutoff)
                .group_by(MentionDB.source)
            ).all()

            by_sentiment = session.execute(
                select(MentionDB.sentiment, func.count(MentionDB.id))
                .where(MentionDB.timestamp >= cutoff)
                .where(MentionDB.sentiment.isnot(None))
                .group_by(MentionDB.sentiment)
            ).all()

            return {
                "total_mentions": total,
                "by_source": {source: count for source, count in by_source},
                "by_sentiment": {sent: count for sent, count in by_sentiment},
                "days": days,
            }

    def _db_to_mention(self, db_mention: MentionDB) -> Mention:
        """Convert database model to Mention schema.

        Args:
            db_mention: Database mention object

        Returns:
            Mention schema object
        """
        return Mention(
            id=str(db_mention.id),
            source=SourceType(db_mention.source),
            keyword=db_mention.keyword,
            url=db_mention.url,
            title=db_mention.title,
            content=db_mention.content,
            timestamp=db_mention.timestamp,
            author=db_mention.author,
            sentiment=SentimentScore(db_mention.sentiment) if db_mention.sentiment else None,
            sentiment_confidence=db_mention.sentiment_confidence,
            language=db_mention.language,
            metadata=db_mention.metadata,
        )

    def clear_old_mentions(self, days: int = 30) -> int:
        """Clear mentions older than specified days.

        Args:
            days: Keep mentions newer than this many days

        Returns:
            Number of mentions deleted
        """
        with self.get_session() as session:
            cutoff = datetime.now() - timedelta(days=days)
            result = session.execute(select(MentionDB).where(MentionDB.timestamp < cutoff))
                MentionDB.__table__.delete().where(MentionDB.timestamp < cutoff)
            )
            return result.rowcount or 0
"""
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from tinydb import TinyDB, Query


class Database:
    """Database manager for OSINT mentions."""

    def __init__(self, db_path: str = "./data/osint.db"):
        """
        Initialize the database.

        Args:
            db_path: Path to the database file
        """
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.db = TinyDB(db_path)
        self.mentions = self.db.table("mentions")
        self.queries = self.db.table("queries")

    def save_mention(self, mention: Dict[str, Any]) -> int:
        """
        Save a single mention to the database.

        Args:
            mention: Mention dictionary

        Returns:
            Document ID of the saved mention
        """
        mention["saved_at"] = datetime.now().isoformat()
        return self.mentions.insert(mention)

    def save_mentions(self, mentions: List[Dict[str, Any]]) -> List[int]:
        """
        Save multiple mentions to the database.

        Args:
            mentions: List of mention dictionaries

        Returns:
            List of document IDs
        """
        for mention in mentions:
            mention["saved_at"] = datetime.now().isoformat()
        return self.mentions.insert_multiple(mentions)

    def get_mentions(
        self,
        limit: Optional[int] = None,
        source: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve mentions from the database.

        Args:
            limit: Maximum number of mentions to retrieve
            source: Filter by source platform
            keyword: Filter by keyword

        Returns:
            List of mentions
        """
        Mention = Query()

        if source and keyword:
            results = self.mentions.search(
                (Mention.source == source) & (Mention.keywords.any([keyword]))
            )
        elif source:
            results = self.mentions.search(Mention.source == source)
        elif keyword:
            results = self.mentions.search(Mention.keywords.any([keyword]))
        else:
            results = self.mentions.all()

        if limit:
            return results[:limit]
        return results

    def get_by_sentiment(self, sentiment: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get mentions by sentiment.

        Args:
            sentiment: Sentiment type (positive, negative, neutral)
            limit: Maximum number of results

        Returns:
            List of mentions with specified sentiment
        """
        Mention = Query()
        results = self.mentions.search(Mention.sentiment.sentiment == sentiment)

        if limit:
            return results[:limit]
        return results

    def save_query(self, keywords: List[str], sources: List[str], results_count: int) -> int:
        """
        Save a query record.

        Args:
            keywords: Keywords used in the query
            sources: Sources queried
            results_count: Number of results found

        Returns:
            Document ID of the saved query
        """
        query_record = {
            "keywords": keywords,
            "sources": sources,
            "results_count": results_count,
            "timestamp": datetime.now().isoformat(),
        }
        return self.queries.insert(query_record)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Dictionary with database statistics
        """
        all_mentions = self.mentions.all()

        sources = {}
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}

        for mention in all_mentions:
            source = mention.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1

            sentiment_data = mention.get("sentiment", {})
            sentiment = sentiment_data.get("sentiment", "neutral")
            if sentiment in sentiments:
                sentiments[sentiment] += 1

        return {
            "total_mentions": len(all_mentions),
            "sources": sources,
            "sentiments": sentiments,
            "total_queries": len(self.queries.all()),
        }

    def clear_mentions(self):
        """Clear all mentions from the database."""
        self.mentions.truncate()

    def clear_all(self):
        """Clear all data from the database."""
        self.mentions.truncate()
        self.queries.truncate()

    def close(self):
        """Close the database connection."""
        self.db.close()

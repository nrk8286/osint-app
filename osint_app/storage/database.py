"""Database storage backend implementation."""

from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String, create_engine, delete, func, select
from sqlalchemy.orm import declarative_base, sessionmaker

from osint_app.core.config import config
from osint_app.models.schemas import Mention, SentimentScore, SourceType
from osint_app.storage.models import Base, MentionDB


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
                sentiment_confidence=mention.sentiment_confidence,
                language=mention.language,
                extra_metadata=mention.metadata,
            )
            session.add(db_mention)
            session.flush()
            return int(db_mention.id)

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
                    sentiment_confidence=m.sentiment_confidence,
                    language=m.language,
                    extra_metadata=m.metadata,
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

            return {
                "total_mentions": total or 0,
                "by_source": {source: count for source, count in by_source},
                "by_sentiment": {},
                "days": days,
            }

    def _db_to_mention(self, db_mention: MentionDB) -> Mention:
        """Convert database model to Mention schema."""
        return Mention(
            id=str(db_mention.id),
            source=SourceType(db_mention.source),
            keyword=db_mention.keyword,
            url=db_mention.url,
            title=db_mention.title,
            content=db_mention.content,
            timestamp=db_mention.timestamp,
            author=db_mention.author,
            sentiment_confidence=db_mention.sentiment_confidence,
            language=db_mention.language,
            metadata=db_mention.extra_metadata or {},
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
            result = session.execute(delete(MentionDB).where(MentionDB.timestamp < cutoff))
            return result.rowcount or 0


# ---------------------------------------------------------------------------
# Backwards-compatible Database API
#
# The test suite (tests/test_database.py) expects a `Database` class with a
# dict-based interface. The main application code uses `DatabaseStorage` with
# Pydantic schemas.
#
# To keep both working, we provide a small adapter implementation here.
# ---------------------------------------------------------------------------

_CompatBase = declarative_base()


class _MentionCompat(_CompatBase):
    __tablename__ = "mentions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String, nullable=False)
    source = Column(String, nullable=False)
    keywords = Column(JSON, nullable=False, default=list)
    sentiment = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class _QueryCompat(_CompatBase):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keywords = Column(JSON, nullable=False, default=list)
    sources = Column(JSON, nullable=False, default=list)
    results_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Database:
    """Compatibility wrapper expected by tests.

    This class is intentionally minimal and only implements what the unit tests
    expect (save/get/clear mentions, save queries, and compute statistics).
    """

    def __init__(self, db_path: str):
        # Tests pass a filesystem path; interpret it as a SQLite file.
        self.db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(self.db_url, echo=False, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, future=True)
        _CompatBase.metadata.create_all(self.engine)

    @contextmanager
    def _session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        self.engine.dispose()

    def save_mention(self, mention: Dict[str, Any]) -> int:
        with self._session() as session:
            row = _MentionCompat(
                text=mention["text"],
                source=mention["source"],
                keywords=mention.get("keywords", []),
                sentiment=mention.get("sentiment"),
            )
            session.add(row)
            session.flush()
            return int(row.id)

    def save_mentions(self, mentions: List[Dict[str, Any]]) -> List[int]:
        ids: List[int] = []
        for m in mentions:
            ids.append(self.save_mention(m))
        return ids

    def get_mentions(
        self,
        source: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        with self._session() as session:
            q = select(_MentionCompat).order_by(_MentionCompat.id.asc())
            if source:
                q = q.where(_MentionCompat.source == source)

            rows = session.execute(q).scalars().all()

            if keyword:
                # Keep this SQLite/JSON portable: filter in Python.
                rows = [r for r in rows if keyword in (r.keywords or [])]

            if limit is not None:
                rows = rows[: int(limit)]

            return [
                {
                    "id": int(r.id),
                    "text": r.text,
                    "source": r.source,
                    "keywords": r.keywords or [],
                    "sentiment": r.sentiment,
                }
                for r in rows
            ]

    def get_by_sentiment(self, sentiment: str) -> List[Dict[str, Any]]:
        mentions = self.get_mentions()
        return [m for m in mentions if (m.get("sentiment") or {}).get("sentiment") == sentiment]

    def save_query(self, keywords: List[str], sources: List[str], results_count: int) -> int:
        with self._session() as session:
            row = _QueryCompat(keywords=keywords, sources=sources, results_count=results_count)
            session.add(row)
            session.flush()
            return int(row.id)

    def get_statistics(self) -> Dict[str, Any]:
        with self._session() as session:
            mentions = session.execute(select(_MentionCompat)).scalars().all()
            queries = session.execute(select(_QueryCompat)).scalars().all()

            sources: Dict[str, int] = {}
            sentiments: Dict[str, int] = {}

            for m in mentions:
                sources[m.source] = sources.get(m.source, 0) + 1
                s = (m.sentiment or {}).get("sentiment")
                if s:
                    sentiments[s] = sentiments.get(s, 0) + 1

            return {
                "total_mentions": len(mentions),
                "sources": sources,
                "sentiments": sentiments,
                "total_queries": len(queries),
            }

    def clear_mentions(self) -> None:
        with self._session() as session:
            session.execute(delete(_MentionCompat))

    def clear_all(self) -> None:
        with self._session() as session:
            session.execute(delete(_MentionCompat))
            session.execute(delete(_QueryCompat))

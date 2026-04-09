"""Database storage backend implementation."""

import json
import sqlite3
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select, func, delete
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
            result = session.execute(
                delete(MentionDB).where(MentionDB.timestamp < cutoff)
            )
            return result.rowcount or 0


class Database:
    """Lightweight SQLite-backed database with a simple dict-based interface.

    This class provides a TinyDB-compatible API used by legacy code and tests.
    Data is stored in a local SQLite file specified at construction time.
    """

    def __init__(self, db_path: str):
        """Initialize database at the given file path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create tables if they don't exist."""
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS mentions (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                text    TEXT,
                source  TEXT,
                keywords TEXT,
                url     TEXT,
                author  TEXT,
                timestamp TEXT,
                sentiment TEXT,
                extra   TEXT
            );
            CREATE TABLE IF NOT EXISTS queries (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                keywords      TEXT,
                sources       TEXT,
                results_count INTEGER,
                timestamp     TEXT
            );
            """
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Mentions
    # ------------------------------------------------------------------

    def save_mention(self, mention: dict) -> int:
        """Save a single mention dict and return its row id."""
        extras = {
            k: v
            for k, v in mention.items()
            if k not in {"text", "source", "keywords", "url", "author", "timestamp", "sentiment"}
        }
        cursor = self._conn.execute(
            """
            INSERT INTO mentions (text, source, keywords, url, author, timestamp, sentiment, extra)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mention.get("text", ""),
                mention.get("source", ""),
                json.dumps(mention.get("keywords", [])),
                mention.get("url", ""),
                mention.get("author", ""),
                mention.get("timestamp", datetime.now().isoformat()),
                json.dumps(mention.get("sentiment")) if mention.get("sentiment") is not None else None,
                json.dumps(extras) if extras else None,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def save_mentions(self, mentions: list) -> list:
        """Save multiple mention dicts and return a list of row ids."""
        return [self.save_mention(m) for m in mentions]

    def get_mentions(
        self,
        source: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list:
        """Retrieve mentions with optional filtering.

        Args:
            source: Filter by source field.
            keyword: Filter by keywords list (substring match).
            limit: Maximum number of rows to return.

        Returns:
            List of mention dicts.
        """
        sql = "SELECT * FROM mentions WHERE 1=1"
        params: list = []
        if source is not None:
            sql += " AND source = ?"
            params.append(source)
        if keyword is not None:
            sql += " AND keywords LIKE ?"
            params.append(f"%{keyword}%")
        sql += " ORDER BY id DESC"
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)

        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_sentiment(self, sentiment: str) -> list:
        """Return mentions whose sentiment field matches the given value.

        Args:
            sentiment: Sentiment label, e.g. 'positive', 'negative', 'neutral'.

        Returns:
            List of matching mention dicts.
        """
        rows = self._conn.execute(
            "SELECT * FROM mentions WHERE sentiment LIKE ?",
            (f'%"sentiment": "{sentiment}"%',),
        ).fetchall()
        result = []
        for row in rows:
            mention = self._row_to_dict(row)
            s = mention.get("sentiment")
            if isinstance(s, dict) and s.get("sentiment") == sentiment:
                result.append(mention)
        return result

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """Convert a SQLite row to a plain dict."""
        d = dict(row)
        d["keywords"] = json.loads(d["keywords"]) if d["keywords"] else []
        if d.get("sentiment"):
            try:
                d["sentiment"] = json.loads(d["sentiment"])
            except (json.JSONDecodeError, TypeError):
                pass
        extra = d.pop("extra", None)
        if extra:
            try:
                d.update(json.loads(extra))
            except (json.JSONDecodeError, TypeError):
                pass
        return d

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def save_query(self, keywords: list, sources: list, results_count: int) -> int:
        """Save a query record and return its row id.

        Args:
            keywords: List of search keywords.
            sources: List of source names.
            results_count: Number of results returned.

        Returns:
            Row id of the saved query.
        """
        cursor = self._conn.execute(
            """
            INSERT INTO queries (keywords, sources, results_count, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                json.dumps(keywords),
                json.dumps(sources),
                results_count,
                datetime.now().isoformat(),
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def get_statistics(self) -> dict:
        """Return aggregate statistics about stored data.

        Returns:
            Dict with keys: total_mentions, sources, sentiments, total_queries.
        """
        total_mentions = self._conn.execute("SELECT COUNT(*) FROM mentions").fetchone()[0]
        total_queries = self._conn.execute("SELECT COUNT(*) FROM queries").fetchone()[0]

        source_rows = self._conn.execute(
            "SELECT source, COUNT(*) AS cnt FROM mentions GROUP BY source"
        ).fetchall()
        sources = {r["source"]: r["cnt"] for r in source_rows}

        sentiment_rows = self._conn.execute(
            "SELECT sentiment FROM mentions WHERE sentiment IS NOT NULL"
        ).fetchall()
        sentiments: dict = {}
        for row in sentiment_rows:
            try:
                s = json.loads(row["sentiment"])
                label = s.get("sentiment") if isinstance(s, dict) else None
            except (json.JSONDecodeError, TypeError):
                label = None
            if label:
                sentiments[label] = sentiments.get(label, 0) + 1

        return {
            "total_mentions": total_mentions,
            "sources": sources,
            "sentiments": sentiments,
            "total_queries": total_queries,
        }

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def clear_mentions(self):
        """Delete all mention records."""
        self._conn.execute("DELETE FROM mentions")
        self._conn.commit()

    def clear_all(self):
        """Delete all records from every table."""
        self._conn.execute("DELETE FROM mentions")
        self._conn.execute("DELETE FROM queries")
        self._conn.commit()

    def close(self):
        """Close the database connection."""
        self._conn.close()

"""Generic RSS/Atom feed reader source integration."""

import asyncio
from datetime import datetime, timezone
from typing import List

try:
    import feedparser

    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

from osint_app.core.config import config
from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.base import BaseSource


class RSSSource(BaseSource):
    """Generic RSS/Atom feed reader that keyword-searches configured feeds."""

    def __init__(self):
        """Initialize RSS source."""
        super().__init__("RSS")
        raw = config.rss_feeds.strip()
        self.feed_urls: List[str] = [u.strip() for u in raw.split(",") if u.strip()] if raw else []
        self.enabled = FEEDPARSER_AVAILABLE and bool(self.feed_urls)

    def is_available(self) -> bool:
        """Check if RSS source is available and has feeds configured."""
        return FEEDPARSER_AVAILABLE and bool(self.feed_urls)

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search all configured RSS/Atom feeds for the keyword.

        Args:
            keyword: Search term
            max_results: Maximum total matching entries to return

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        loop = asyncio.get_event_loop()
        mentions: List[Mention] = []

        for feed_url in self.feed_urls:
            if len(mentions) >= max_results:
                break
            try:
                feed_mentions = await loop.run_in_executor(
                    None, self._parse_feed, feed_url, keyword, max_results - len(mentions)
                )
                mentions.extend(feed_mentions)
            except Exception as e:
                print(f"Error reading RSS feed {feed_url}: {e}")

        return mentions[:max_results]

    def _parse_feed(self, feed_url: str, keyword: str, limit: int) -> List[Mention]:
        """Parse a single feed and return entries matching the keyword.

        Args:
            feed_url: URL of the RSS/Atom feed
            keyword: Search term
            limit: Maximum entries to return from this feed

        Returns:
            List of matching mentions
        """
        kw_lower = keyword.lower()
        feed = feedparser.parse(feed_url)
        mentions: List[Mention] = []

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", "") or entry.get("description", "")
            content_blocks = entry.get("content") or []
            full_content = " ".join(c.get("value", "") for c in content_blocks) if content_blocks else ""
            text_to_search = f"{title} {summary} {full_content}"

            if kw_lower not in text_to_search.lower():
                continue

            link = entry.get("link", feed_url)
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                try:
                    ts = datetime(*published[:6], tzinfo=timezone.utc)
                except Exception:
                    ts = datetime.now(timezone.utc)
            else:
                ts = datetime.now(timezone.utc)

            tags = entry.get("tags") or []
            mention = Mention(
                source=SourceType.RSS,
                keyword=keyword,
                url=link,
                title=title,
                content=summary or full_content,
                timestamp=ts,
                author=entry.get("author"),
                metadata={
                    "feed_url": feed_url,
                    "feed_title": feed.feed.get("title", ""),
                    "tags": [t.get("term") for t in tags if isinstance(t, dict)],
                },
            )
            mentions.append(mention)

            if len(mentions) >= limit:
                break

        return mentions

"""Hacker News source integration via Algolia search API."""

from datetime import datetime, timezone
from typing import List

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.base import BaseSource

_HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"


class HackerNewsSource(BaseSource):
    """Hacker News search via the Algolia HN API (no key required)."""

    def __init__(self):
        """Initialize Hacker News source."""
        super().__init__("HackerNews")
        self.enabled = AIOHTTP_AVAILABLE

    def is_available(self) -> bool:
        """Check if HackerNews source is available."""
        return AIOHTTP_AVAILABLE

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search Hacker News for keyword mentions.

        Args:
            keyword: Search term
            max_results: Maximum number of results

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        mentions: List[Mention] = []

        try:
            params = {
                "query": keyword,
                "hitsPerPage": min(max_results, 50),
                "tags": "story,comment",
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    _HN_SEARCH_URL, params=params, timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status != 200:
                        return []
                    data = await response.json()

            for hit in data.get("hits", []):
                object_id = hit.get("objectID", "")
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
                created_at = hit.get("created_at")
                try:
                    ts = (
                        datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        if created_at
                        else datetime.now(timezone.utc)
                    )
                except (ValueError, AttributeError):
                    ts = datetime.now(timezone.utc)

                mention = Mention(
                    source=SourceType.HACKERNEWS,
                    keyword=keyword,
                    url=url,
                    title=hit.get("title") or hit.get("story_title") or url,
                    content=hit.get("story_text") or hit.get("comment_text") or "",
                    timestamp=ts,
                    author=hit.get("author"),
                    metadata={
                        "object_id": object_id,
                        "points": hit.get("points", 0),
                        "num_comments": hit.get("num_comments", 0),
                        "type": hit.get("_tags", [None])[0],
                    },
                    engagement=(hit.get("points") or 0) + (hit.get("num_comments") or 0),
                )
                mentions.append(mention)

        except Exception as e:
            print(f"Error searching HackerNews: {e}")

        return mentions

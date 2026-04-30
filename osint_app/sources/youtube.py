"""YouTube Data API v3 source integration."""

from datetime import datetime, timezone
from typing import List

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from osint_app.core.config import config
from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.base import BaseSource

_YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


class YouTubeSource(BaseSource):
    """YouTube Data API v3 search integration."""

    def __init__(self):
        """Initialize YouTube source."""
        super().__init__("YouTube")
        self.api_key = config.youtube.api_key
        self.enabled = AIOHTTP_AVAILABLE and config.youtube.is_configured

    def is_available(self) -> bool:
        """Check if YouTube source is available and configured."""
        return AIOHTTP_AVAILABLE and bool(self.api_key)

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search YouTube for videos matching the keyword.

        Args:
            keyword: Search term
            max_results: Maximum number of results (capped at 50)

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        mentions: List[Mention] = []

        try:
            params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "maxResults": min(max_results, 50),
                "key": self.api_key,
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    _YOUTUBE_SEARCH_URL,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as response:
                    if response.status != 200:
                        body = await response.text()
                        print(f"YouTube API error {response.status}: {body[:200]}")
                        return []
                    data = await response.json()

            for item in data.get("items", []):
                video_id = item.get("id", {}).get("videoId", "")
                snippet = item.get("snippet", {})
                published_at = snippet.get("publishedAt")
                try:
                    ts = (
                        datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                        if published_at
                        else datetime.now(timezone.utc)
                    )
                except (ValueError, AttributeError):
                    ts = datetime.now(timezone.utc)

                mention = Mention(
                    source=SourceType.YOUTUBE,
                    keyword=keyword,
                    url=f"https://www.youtube.com/watch?v={video_id}",
                    title=snippet.get("title", ""),
                    content=snippet.get("description", ""),
                    timestamp=ts,
                    author=snippet.get("channelTitle"),
                    metadata={
                        "video_id": video_id,
                        "channel_id": snippet.get("channelId"),
                        "thumbnail": snippet.get("thumbnails", {})
                        .get("default", {})
                        .get("url"),
                    },
                )
                mentions.append(mention)

        except Exception as e:
            print(f"Error searching YouTube: {e}")

        return mentions

"""Pastebin source integration using the public scraping API."""

from datetime import datetime, timezone
from typing import List

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.base import BaseSource

_PASTEBIN_SCRAPE_URL = "https://scrape.pastebin.com/api_scraping.php"
_PASTEBIN_ITEM_URL = "https://scrape.pastebin.com/api_scrape_item.php"


class PastebinSource(BaseSource):
    """Pastebin search using the public scraping endpoint.

    Note: The Pastebin scraping API is only accessible from whitelisted IPs.
    The source degrades gracefully when the API is unavailable or returns errors.
    """

    def __init__(self):
        """Initialize Pastebin source."""
        super().__init__("Pastebin")
        self.enabled = AIOHTTP_AVAILABLE

    def is_available(self) -> bool:
        """Check if Pastebin source is available."""
        return AIOHTTP_AVAILABLE

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Fetch recent pastes and filter those containing the keyword.

        Args:
            keyword: Search term
            max_results: Maximum number of matching pastes to return

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        mentions: List[Mention] = []
        kw_lower = keyword.lower()

        try:
            # Fetch the most recent pastes metadata list
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    _PASTEBIN_SCRAPE_URL,
                    params={"limit": 100},
                    timeout=aiohttp.ClientTimeout(total=20),
                ) as response:
                    if response.status != 200:
                        return []
                    pastes = await response.json(content_type=None)

            # Filter pastes whose titles match; content fetching is rate-limited
            matched = [
                p
                for p in pastes
                if kw_lower in (p.get("title") or "").lower()
                or kw_lower in (p.get("syntax") or "").lower()
            ]

            for paste in matched[:max_results]:
                key = paste.get("key", "")
                paste_url = f"https://pastebin.com/{key}"
                date_val = paste.get("date")
                try:
                    ts = (
                        datetime.fromtimestamp(int(date_val), tz=timezone.utc)
                        if date_val
                        else datetime.now(timezone.utc)
                    )
                except (ValueError, TypeError):
                    ts = datetime.now(timezone.utc)

                mention = Mention(
                    source=SourceType.PASTEBIN,
                    keyword=keyword,
                    url=paste_url,
                    title=paste.get("title") or paste_url,
                    content="",
                    timestamp=ts,
                    metadata={
                        "key": key,
                        "syntax": paste.get("syntax"),
                        "size": paste.get("size"),
                        "expire": paste.get("expire"),
                    },
                )
                mentions.append(mention)

        except Exception as e:
            print(f"Error searching Pastebin: {e}")

        return mentions

"""Telegram public channel monitoring source integration.

Requires the ``telethon`` package and valid Telegram API credentials
(TELEGRAM_API_ID + TELEGRAM_API_HASH from https://my.telegram.org/apps).

The source is disabled gracefully when credentials or the library are absent.
"""

import asyncio
from datetime import datetime, timezone
from typing import List

try:
    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError
    from telethon.tl.functions.contacts import SearchRequest

    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False

from osint_app.core.config import config
from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.base import BaseSource


class TelegramSource(BaseSource):
    """Telegram public channel / global search integration via Telethon."""

    def __init__(self):
        """Initialize Telegram source."""
        super().__init__("Telegram")
        self.api_id = config.telegram.api_id
        self.api_hash = config.telegram.api_hash
        self.enabled = TELETHON_AVAILABLE and config.telegram.is_configured

    def is_available(self) -> bool:
        """Check if Telegram source is available and configured."""
        return TELETHON_AVAILABLE and self.enabled and bool(self.api_id) and bool(self.api_hash)

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search public Telegram channels for the keyword using the global search.

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
            client = TelegramClient(
                "osint_monitor_session",
                int(self.api_id),
                self.api_hash,
            )
            await client.start()

            # Use global search across public channels
            result = await client(SearchRequest(q=keyword, limit=min(max_results, 50)))

            for channel in getattr(result, "chats", [])[:max_results]:
                username = getattr(channel, "username", None)
                if not username:
                    continue
                url = f"https://t.me/{username}"
                title = getattr(channel, "title", username)
                participants = getattr(channel, "participants_count", 0) or 0

                mention = Mention(
                    source=SourceType.TELEGRAM,
                    keyword=keyword,
                    url=url,
                    title=title,
                    content=getattr(channel, "about", "") or "",
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "username": username,
                        "participants": participants,
                        "channel_id": channel.id,
                    },
                    engagement=participants,
                )
                mentions.append(mention)

            await client.disconnect()

        except Exception as e:
            print(f"Error searching Telegram: {e}")

        return mentions

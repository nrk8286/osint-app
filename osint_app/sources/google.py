"""Google search source integration."""

import asyncio
from datetime import datetime
from typing import List

try:
    from googlesearch import search as google_search
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from osint_app.sources.base import BaseSource
from osint_app.models.schemas import Mention, SourceType


class GoogleSource(BaseSource):
    """Google search integration."""

    def __init__(self):
        """Initialize Google source."""
        super().__init__("Google")
        self.enabled = GOOGLE_AVAILABLE

    def is_available(self) -> bool:
        """Check if Google search is available."""
        return GOOGLE_AVAILABLE

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search Google for keyword mentions.

        Args:
            keyword: Search term
            max_results: Number of results to retrieve

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        mentions = []

        try:
            # Run blocking Google search in executor
            loop = asyncio.get_event_loop()
            urls = await loop.run_in_executor(
                None,
                lambda: list(google_search(keyword, num_results=max_results, sleep_interval=2))
            )

            for url in urls:
                mention = Mention(
                    source=SourceType.GOOGLE,
                    keyword=keyword,
                    url=url,
                    title=url,
                    content="",
                    timestamp=datetime.now()
                )
                mentions.append(mention)

                # Rate limiting
                await asyncio.sleep(1)

        except Exception as e:
            print(f"Error searching Google: {e}")

        return mentions

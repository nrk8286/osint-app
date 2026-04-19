"""News API source integration."""

from datetime import datetime
from typing import List
import asyncio

try:
    import aiohttp

    NEWS_HTTP_AVAILABLE = True
except ImportError:
    NEWS_HTTP_AVAILABLE = False

from osint_app.sources.base import BaseSource
from osint_app.models.schemas import Mention, SourceType
from osint_app.core.config import config


class NewsAPISource(BaseSource):
    """News API integration."""

    def __init__(self):
        """Initialize News API source."""
        super().__init__("NewsAPI")
        self.api_key = config.news_api.key
        self.enabled = config.news_api.is_configured and NEWS_HTTP_AVAILABLE
        self.base_url = "https://newsapi.org/v2/everything"

    def is_available(self) -> bool:
        """Check if News API is available and configured."""
        return NEWS_HTTP_AVAILABLE and self.enabled and bool(self.api_key)

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search News API for keyword mentions.

        Args:
            keyword: Search term
            max_results: Maximum number of results

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        mentions = []

        try:
            params = {
                "q": keyword,
                "apiKey": self.api_key,
                "pageSize": min(max_results, 100),
                "sortBy": "publishedAt",
                "language": "en",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        for article in data.get("articles", []):
                            mention = Mention(
                                source=SourceType.NEWS,
                                keyword=keyword,
                                url=article.get("url", ""),
                                title=article.get("title", ""),
                                content=article.get("description", "")
                                + "\n"
                                + article.get("content", ""),
                                timestamp=(
                                    datetime.fromisoformat(
                                        article.get("publishedAt", "").replace("Z", "+00:00")
                                    )
                                    if article.get("publishedAt")
                                    else datetime.now()
                                ),
                                author=article.get("author"),
                                metadata={
                                    "source_name": article.get("source", {}).get("name"),
                                    "image_url": article.get("urlToImage"),
                                },
                            )
                            mentions.append(mention)
                    else:
                        print(f"News API error: HTTP {response.status}")

        except Exception as e:
            print(f"Error searching News API: {e}")

        return mentions

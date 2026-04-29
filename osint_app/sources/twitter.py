"""Twitter source integration."""

import asyncio
from datetime import datetime
from typing import List

try:
    import tweepy

    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

from osint_app.core.config import config
from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.base import BaseSource


class TwitterSource(BaseSource):
    """Twitter API integration."""

    def __init__(self):
        """Initialize Twitter source."""
        super().__init__("Twitter")
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Twitter API client."""
        if not TWITTER_AVAILABLE:
            self.enabled = False
            return

        try:
            if config.twitter.bearer_token:
                self.client = tweepy.Client(bearer_token=config.twitter.bearer_token)
                self.enabled = True
            else:
                self.enabled = False
        except Exception as e:
            print(f"Error initializing Twitter client: {e}")
            self.enabled = False

    def is_available(self) -> bool:
        """Check if Twitter is available and configured."""
        return TWITTER_AVAILABLE and self.enabled and self.client is not None

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search Twitter for keyword mentions.

        Args:
            keyword: Search term
            max_results: Maximum number of tweets

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        mentions = []

        try:
            loop = asyncio.get_running_loop()
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.search_recent_tweets(
                    query=keyword,
                    max_results=min(max_results, 100),
                    tweet_fields=["created_at", "author_id", "public_metrics"],
                ),
            )

            if response.data:
                for tweet in response.data:
                    mention = Mention(
                        source=SourceType.TWITTER,
                        keyword=keyword,
                        url=f"https://twitter.com/user/status/{tweet.id}",
                        title=f"Tweet by user {tweet.author_id}",
                        content=tweet.text,
                        timestamp=(
                            tweet.created_at if hasattr(tweet, "created_at") else datetime.now()
                        ),
                        author=str(tweet.author_id),
                        metadata={
                            "tweet_id": str(tweet.id),
                            "metrics": (
                                tweet.public_metrics if hasattr(tweet, "public_metrics") else {}
                            ),
                        },
                    )
                    mentions.append(mention)

        except Exception as e:
            print(f"Error searching Twitter: {e}")

        return mentions

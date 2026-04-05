"""Reddit source integration."""

from datetime import datetime
from typing import List
import asyncio

try:
    import praw
    REDDIT_AVAILABLE = True
except ImportError:
    REDDIT_AVAILABLE = False

from osint_app.sources.base import BaseSource
from osint_app.models.schemas import Mention, SourceType
from osint_app.core.config import config


class RedditSource(BaseSource):
    """Reddit API integration."""

    def __init__(self):
        """Initialize Reddit source."""
        super().__init__("Reddit")
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Reddit API client."""
        if not REDDIT_AVAILABLE:
            self.enabled = False
            return

        try:
            if config.reddit.is_configured:
                self.client = praw.Reddit(
                    client_id=config.reddit.client_id,
                    client_secret=config.reddit.client_secret,
                    user_agent=config.reddit.user_agent
                )
                self.enabled = True
            else:
                self.enabled = False
        except Exception as e:
            print(f"Error initializing Reddit client: {e}")
            self.enabled = False

    def is_available(self) -> bool:
        """Check if Reddit is available and configured."""
        return REDDIT_AVAILABLE and self.enabled and self.client is not None

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search Reddit for keyword mentions.

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
            # Run Reddit search in executor
            loop = asyncio.get_event_loop()
            submissions = await loop.run_in_executor(
                None,
                lambda: list(self.client.subreddit('all').search(keyword, limit=max_results))
            )

            for submission in submissions:
                mention = Mention(
                    source=SourceType.REDDIT,
                    keyword=keyword,
                    url=f"https://reddit.com{submission.permalink}",
                    title=submission.title,
                    content=submission.selftext[:1000] if submission.selftext else "",
                    timestamp=datetime.fromtimestamp(submission.created_utc),
                    author=str(submission.author) if submission.author else None,
                    metadata={
                        'subreddit': str(submission.subreddit),
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'upvote_ratio': submission.upvote_ratio
                    }
                )
                mentions.append(mention)

        except Exception as e:
            print(f"Error searching Reddit: {e}")

        return mentions

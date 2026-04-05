"""Main OSINT monitoring class with async support."""

import asyncio
from typing import List, Optional
from datetime import datetime
import pandas as pd

from osint_app.models.schemas import Mention, SearchQuery
from osint_app.sources.google import GoogleSource
from osint_app.sources.twitter import TwitterSource
from osint_app.sources.reddit import RedditSource
from osint_app.sources.news import NewsAPISource
from osint_app.storage.database import DatabaseStorage
from osint_app.utils.sentiment import get_sentiment_analyzer
from osint_app.core.config import config


class OSINTMonitor:
    """Main class for OSINT monitoring with async support."""

    def __init__(self, use_database: bool = True, enable_sentiment: bool = True):
        """Initialize the OSINT monitor.

        Args:
            use_database: Whether to use database storage
            enable_sentiment: Whether to enable sentiment analysis
        """
        # Initialize sources
        self.sources = {
            "google": GoogleSource(),
            "twitter": TwitterSource(),
            "reddit": RedditSource(),
            "news": NewsAPISource(),
        }

        # Initialize storage
        self.db = DatabaseStorage() if use_database else None
        self.mentions: List[Mention] = []

        # Initialize sentiment analyzer
        self.sentiment_analyzer = None
        if enable_sentiment:
            self.sentiment_analyzer = get_sentiment_analyzer(
                use_transformers=config.enable_sentiment_analysis
            )

        self._print_status()

    def _print_status(self):
        """Print initialization status."""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║     OSINT Monitoring Platform v2.0 - Production Ready      ║")
        print("╚════════════════════════════════════════════════════════════╝")
        print("\nData Sources:")
        for name, source in self.sources.items():
            status = "✓ Active" if source.is_available() else "✗ Disabled"
            print(f"  {name.capitalize():12} : {status}")

        print(f"\nFeatures:")
        print(f"  Database     : {'✓ Enabled' if self.db else '✗ Disabled'}")
        print(f"  Sentiment    : {'✓ Enabled' if self.sentiment_analyzer else '✗ Disabled'}")
        print()

    async def search_all_sources(
        self,
        keyword: str,
        google_results: int = 10,
        twitter_results: int = 10,
        reddit_results: int = 10,
        news_results: int = 10,
    ) -> List[Mention]:
        """Search all available sources concurrently.

        Args:
            keyword: Search term
            google_results: Number of Google results
            twitter_results: Number of Twitter results
            reddit_results: Number of Reddit results
            news_results: Number of news results

        Returns:
            Combined list of all mentions
        """
        tasks = []

        if self.sources["google"].is_available():
            tasks.append(self.sources["google"].search(keyword, google_results))

        if self.sources["twitter"].is_available():
            tasks.append(self.sources["twitter"].search(keyword, twitter_results))

        if self.sources["reddit"].is_available():
            tasks.append(self.sources["reddit"].search(keyword, reddit_results))

        if self.sources["news"].is_available():
            tasks.append(self.sources["news"].search(keyword, news_results))

        # Execute all searches concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results and filter out errors
        all_mentions = []
        for result in results:
            if isinstance(result, list):
                all_mentions.extend(result)
            elif isinstance(result, Exception):
                print(f"Warning: Source error: {result}")

        return all_mentions

    async def collect_mentions(
        self,
        keyword: str,
        google_results: int = 10,
        twitter_results: int = 10,
        reddit_results: int = 10,
        news_results: int = 10,
        enable_sentiment: bool = True,
    ) -> List[Mention]:
        """Collect mentions from all sources with sentiment analysis.

        Args:
            keyword: Search term
            google_results: Number of Google results
            twitter_results: Number of Twitter results
            reddit_results: Number of Reddit results
            news_results: Number of news results
            enable_sentiment: Whether to analyze sentiment

        Returns:
            List of mentions with sentiment analysis
        """
        print(f"\n{'='*60}")
        print(f"Collecting mentions for: '{keyword}'")
        print(f"{'='*60}\n")

        # Search all sources
        mentions = await self.search_all_sources(
            keyword=keyword,
            google_results=google_results,
            twitter_results=twitter_results,
            reddit_results=reddit_results,
            news_results=news_results,
        )

        print(f"\nCollected {len(mentions)} total mentions")

        # Add sentiment analysis if enabled
        if enable_sentiment and self.sentiment_analyzer:
            print("Analyzing sentiment...")
            for mention in mentions:
                self.sentiment_analyzer.analyze_mention(mention)

        # Store in database if enabled
        if self.db:
            try:
                count = self.db.save_mentions(mentions)
                print(f"Saved {count} mentions to database")
            except Exception as e:
                print(f"Warning: Failed to save to database: {e}")

        self.mentions.extend(mentions)

        # Print summary
        self._print_summary(mentions)

        return mentions

    def _print_summary(self, mentions: List[Mention]):
        """Print collection summary.

        Args:
            mentions: List of collected mentions
        """
        print(f"\n{'='*60}")
        print("Collection Summary")
        print(f"{'='*60}")

        # Count by source
        by_source = {}
        for mention in mentions:
            by_source[mention.source.value] = by_source.get(mention.source.value, 0) + 1

        for source, count in by_source.items():
            print(f"  {source.capitalize():12} : {count} mentions")

        # Count by sentiment if available
        if any(m.sentiment for m in mentions):
            print(f"\nSentiment Distribution:")
            by_sentiment = {}
            for mention in mentions:
                if mention.sentiment:
                    by_sentiment[mention.sentiment.value] = (
                        by_sentiment.get(mention.sentiment.value, 0) + 1
                    )

            for sentiment, count in by_sentiment.items():
                print(f"  {sentiment.capitalize():12} : {count}")

        print(f"{'='*60}\n")

    def save_to_csv(self, filename: Optional[str] = None):
        """Save collected mentions to CSV.

        Args:
            filename: Output filename (auto-generated if None)
        """
        if not self.mentions:
            print("No mentions to save.")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mentions_{timestamp}.csv"

        try:
            # Convert to dict for DataFrame
            data = [
                {
                    "source": m.source.value,
                    "keyword": m.keyword,
                    "url": m.url,
                    "title": m.title,
                    "content": m.content,
                    "timestamp": m.timestamp.isoformat(),
                    "author": m.author,
                    "sentiment": m.sentiment.value if m.sentiment else None,
                    "sentiment_confidence": m.sentiment_confidence,
                    "language": m.language,
                }
                for m in self.mentions
            ]

            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            print(f"\n✓ Mentions saved to: {filename}")
            print(f"  Total records: {len(self.mentions)}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def save_to_json(self, filename: Optional[str] = None):
        """Save collected mentions to JSON.

        Args:
            filename: Output filename (auto-generated if None)
        """
        if not self.mentions:
            print("No mentions to save.")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mentions_{timestamp}.json"

        try:
            import json

            data = [m.model_dump(mode="json") for m in self.mentions]

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"\n✓ Mentions saved to: {filename}")
            print(f"  Total records: {len(self.mentions)}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def get_stats(self, days: int = 7) -> dict:
        """Get statistics from database.

        Args:
            days: Number of days to analyze

        Returns:
            Statistics dictionary
        """
        if not self.db:
            return {"error": "Database not enabled"}

        return self.db.get_stats(days=days)

    def clear_mentions(self):
        """Clear in-memory mentions."""
        self.mentions = []
        print("In-memory mentions cleared")


# Convenience function for sync usage
def collect_mentions_sync(
    keyword: str,
    google_results: int = 10,
    twitter_results: int = 10,
    reddit_results: int = 10,
    news_results: int = 10,
    enable_sentiment: bool = True,
) -> List[Mention]:
    """Synchronous wrapper for collect_mentions.

    Args:
        keyword: Search term
        google_results: Number of Google results
        twitter_results: Number of Twitter results
        reddit_results: Number of Reddit results
        news_results: Number of news results
        enable_sentiment: Whether to analyze sentiment

    Returns:
        List of mentions
    """
    monitor = OSINTMonitor()
    return asyncio.run(
        monitor.collect_mentions(
            keyword=keyword,
            google_results=google_results,
            twitter_results=twitter_results,
            reddit_results=reddit_results,
            news_results=news_results,
            enable_sentiment=enable_sentiment,
        )
    )

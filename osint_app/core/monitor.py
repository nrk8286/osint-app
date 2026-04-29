"""Main OSINT monitoring class with async support."""

import asyncio
import hashlib
import json
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from osint_app.core.config import config
from osint_app.models.schemas import Mention
from osint_app.sources.github import GitHubSource
from osint_app.sources.google import GoogleSource
from osint_app.sources.news import NewsAPISource
from osint_app.sources.reddit import RedditSource
from osint_app.sources.twitter import TwitterSource
from osint_app.storage.database import DatabaseStorage
from osint_app.utils.sentiment import get_sentiment_analyzer


class OSINTMonitor:
    """Main class for OSINT monitoring with async support."""

    def __init__(self, use_database: bool = True, enable_sentiment: bool = True):
        """Initialize the OSINT monitor.

        Args:
            use_database: Whether to use database storage
            enable_sentiment: Whether to enable sentiment analysis
        """
        self.sources = {
            "google": GoogleSource(),
            "twitter": TwitterSource(),
            "reddit": RedditSource(),
            "news": NewsAPISource(),
            "github": GitHubSource(),
        }

        self.db = DatabaseStorage() if use_database else None
        self.mentions: List[Mention] = []
        self.search_history: List[dict] = []

        self.sentiment_analyzer = None
        if enable_sentiment:
            self.sentiment_analyzer = get_sentiment_analyzer(
                use_transformers=config.enable_sentiment_analysis
            )

        self._print_status()

    def _print_status(self):
        """Print initialization status."""
        print("+" + "=" * 60 + "+")
        print("|   OSINT Monitoring Platform v2.0 - Production Ready        |")
        print("+" + "=" * 60 + "+")
        print("\nData Sources:")
        for name, source in self.sources.items():
            status = "Active" if source.is_available() else "Disabled"
            symbol = "+" if source.is_available() else "-"
            print(f"  [{symbol}] {name.capitalize():12} : {status}")

        print("\nFeatures:")
        print(f"  [{'+'if self.db else '-'}] Database     : {'Enabled' if self.db else 'Disabled'}")
        print(
            f"  [{'+'if self.sentiment_analyzer else '-'}] Sentiment    : "
            f"{'Enabled' if self.sentiment_analyzer else 'Disabled'}"
        )
        print("  [+] Recon        : DNS / IP Info / HTTP Headers")
        print("  [+] Dedup        : URL-based deduplication")
        print("  [+] Relevance    : Keyword density scoring")
        print()

    async def search_all_sources(
        self,
        keyword: str,
        google_results: int = 10,
        twitter_results: int = 10,
        reddit_results: int = 10,
        news_results: int = 10,
        github_results: int = 10,
        sources: Optional[List[str]] = None,
    ) -> List[Mention]:
        """Search all available sources concurrently.

        Args:
            keyword: Search term
            google_results: Number of Google results
            twitter_results: Number of Twitter results
            reddit_results: Number of Reddit results
            news_results: Number of news results
            github_results: Number of GitHub results
            sources: Limit to these source names (default: all)

        Returns:
            Combined list of all mentions
        """
        tasks = []
        source_limits = {
            "google": google_results,
            "twitter": twitter_results,
            "reddit": reddit_results,
            "news": news_results,
            "github": github_results,
        }

        for name, source in self.sources.items():
            if sources and name not in sources:
                continue
            if source.is_available() and source_limits.get(name, 0) > 0:
                tasks.append(source.search(keyword, source_limits[name]))

        results = await asyncio.gather(*tasks, return_exceptions=True)

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
        github_results: int = 10,
        sources: Optional[List[str]] = None,
        enable_sentiment: bool = True,
    ) -> List[Mention]:
        """Collect mentions from all sources with sentiment analysis.

        Args:
            keyword: Search term
            google_results: Number of Google results
            twitter_results: Number of Twitter results
            reddit_results: Number of Reddit results
            news_results: Number of news results
            github_results: Number of GitHub results
            sources: Limit to these source names
            enable_sentiment: Whether to analyze sentiment

        Returns:
            List of mentions with sentiment analysis
        """
        print(f"\n{'=' * 60}")
        print(f"Collecting mentions for: '{keyword}'")
        print(f"{'=' * 60}\n")

        mentions = await self.search_all_sources(
            keyword=keyword,
            google_results=google_results,
            twitter_results=twitter_results,
            reddit_results=reddit_results,
            news_results=news_results,
            github_results=github_results,
            sources=sources,
        )

        print(f"Collected {len(mentions)} total mentions")

        # Deduplicate
        before = len(mentions)
        mentions = self._deduplicate(mentions)
        dupes = before - len(mentions)
        if dupes:
            print(f"Removed {dupes} duplicate(s)")

        # Relevance scoring
        for m in mentions:
            m.relevance_score = self._calculate_relevance(keyword, f"{m.title} {m.content}")

        # Sentiment analysis
        if enable_sentiment and self.sentiment_analyzer:
            print("Analyzing sentiment...")
            for mention in mentions:
                self.sentiment_analyzer.analyze_mention(mention)

        # Store in database
        if self.db:
            try:
                count = self.db.save_mentions(mentions)
                print(f"Saved {count} mentions to database")
            except Exception as e:
                print(f"Warning: Failed to save to database: {e}")

        self.mentions.extend(mentions)
        self.search_history.append(
            {
                "keyword": keyword,
                "timestamp": datetime.now().isoformat(),
                "sources": sources or list(self.sources.keys()),
                "total_results": len(mentions),
            }
        )

        self._print_summary(mentions)
        return mentions

    def _print_summary(self, mentions: List[Mention]):
        """Print collection summary."""
        print(f"\n{'=' * 60}")
        print("Collection Summary")
        print(f"{'=' * 60}")

        by_source: Dict[str, int] = {}
        for mention in mentions:
            key = mention.source.value
            by_source[key] = by_source.get(key, 0) + 1

        for source, count in by_source.items():
            print(f"  {source.capitalize():12} : {count} mentions")

        if any(m.sentiment for m in mentions):
            print("\nSentiment Distribution:")
            by_sentiment: Dict[str, int] = {}
            for mention in mentions:
                if mention.sentiment:
                    by_sentiment[mention.sentiment.value] = (
                        by_sentiment.get(mention.sentiment.value, 0) + 1
                    )
            for sentiment, count in by_sentiment.items():
                print(f"  {sentiment.capitalize():12} : {count}")

        print(f"\nTotal: {len(mentions)} unique mention(s)")
        print(f"{'=' * 60}\n")

    def summary_report(self) -> dict:
        """Generate a summary report of all collected mentions."""
        if not self.mentions:
            print("No mentions to summarize.")
            return {}

        sources = Counter(m.source.value for m in self.mentions)
        keywords = Counter(m.keyword for m in self.mentions)

        report = {
            "total_mentions": len(self.mentions),
            "by_source": dict(sources),
            "by_keyword": dict(keywords),
            "searches_performed": len(self.search_history),
        }

        print(f"\n{'=' * 60}")
        print("Summary Report")
        print(f"{'=' * 60}")
        print(f"  Total mentions: {report['total_mentions']}")
        print(f"  Searches run:   {report['searches_performed']}")

        print("\n  By source:")
        for src, count in sources.most_common():
            bar = "|" * min(count, 30)
            print(f"    {src:<15} {count:>4}  {bar}")

        print("\n  By keyword:")
        for kw, count in keywords.most_common(5):
            print(f"    {kw:<25} {count:>4}")

        engaged = [m for m in self.mentions if m.engagement is not None]
        if engaged:
            total_eng = sum(m.engagement or 0 for m in engaged)
            top = sorted(engaged, key=lambda m: m.engagement or 0, reverse=True)[:3]
            print("\n  Top engagement:")
            print(f"    Total score: {total_eng}")
            for m in top:
                print(f"    [{m.source.value}] {m.title[:45]}  (score: {m.engagement})")

        print(f"{'=' * 60}\n")
        return report

    def filter_mentions(
        self,
        source: Optional[str] = None,
        keyword: Optional[str] = None,
        min_relevance: float = 0.0,
    ) -> List[Mention]:
        """Filter stored mentions by source, keyword, or relevance score."""
        results = self.mentions
        if source:
            results = [m for m in results if m.source.value.lower() == source.lower()]
        if keyword:
            results = [m for m in results if m.keyword.lower() == keyword.lower()]
        if min_relevance > 0:
            results = [m for m in results if (m.relevance_score or 0) >= min_relevance]
        return results

    # ── Export ─────────────────────────────────────────────────────────

    def save_to_csv(self, filename: Optional[str] = None):
        """Save collected mentions to CSV."""
        if not self.mentions:
            print("No mentions to save.")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mentions_{timestamp}.csv"

        try:
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
                    "relevance_score": m.relevance_score,
                    "engagement": m.engagement,
                    "language": m.language,
                }
                for m in self.mentions
            ]
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            print(f"\nMentions saved to: {filename}")
            print(f"  Total records: {len(self.mentions)}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def save_to_json(self, filename: Optional[str] = None):
        """Save collected mentions to JSON."""
        if not self.mentions:
            print("No mentions to save.")
            return

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mentions_{timestamp}.json"

        try:
            data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_mentions": len(self.mentions),
                    "search_history": self.search_history,
                },
                "mentions": [m.model_dump(mode="json") for m in self.mentions],
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            print(f"\nMentions saved to: {filename}")
            print(f"  Total records: {len(self.mentions)}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")

    def get_stats(self, days: int = 7) -> dict:
        """Get statistics from database."""
        if not self.db:
            return {"error": "Database not enabled"}
        return self.db.get_stats(days=days)

    def clear_mentions(self):
        """Clear in-memory mentions."""
        self.mentions = []
        self.search_history = []
        print("In-memory mentions cleared")

    # ── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _calculate_relevance(keyword: str, text: str) -> float:
        """Calculate a simple relevance score (0-1) based on keyword density."""
        if not text:
            return 0.0
        text_lower = text.lower()
        kw_lower = keyword.lower()
        occurrences = text_lower.count(kw_lower)
        words = text_lower.split()
        word_count = max(len(words), 1)
        density = occurrences / word_count
        return round(min(density * 10, 1.0), 2)

    @staticmethod
    def _deduplicate(mentions: List[Mention]) -> List[Mention]:
        """Remove duplicate mentions based on URL."""
        seen = set()
        unique = []
        for m in mentions:
            key = (
                m.url
                or hashlib.md5(f"{m.source.value}:{m.title}:{m.content[:100]}".encode()).hexdigest()
            )
            if key not in seen:
                seen.add(key)
                unique.append(m)
        return unique


# Convenience function for sync usage
def collect_mentions_sync(
    keyword: str,
    google_results: int = 10,
    twitter_results: int = 10,
    reddit_results: int = 10,
    news_results: int = 10,
    github_results: int = 10,
    enable_sentiment: bool = True,
) -> List[Mention]:
    """Synchronous wrapper for collect_mentions."""
    monitor = OSINTMonitor()
    return asyncio.run(
        monitor.collect_mentions(
            keyword=keyword,
            google_results=google_results,
            twitter_results=twitter_results,
            reddit_results=reddit_results,
            news_results=news_results,
            github_results=github_results,
            enable_sentiment=enable_sentiment,
        )
    )

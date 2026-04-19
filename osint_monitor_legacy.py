#!/usr/bin/env python3
"""
Backward compatibility wrapper for osint_monitor.py
This allows existing code to continue working while using the new v2.0 platform.
"""

import asyncio
from typing import List, Dict
from datetime import datetime

from osint_app.core.monitor import OSINTMonitor as NewOSINTMonitor
from osint_app.models.schemas import Mention


class OSINTMonitor:
    """Backward compatible OSINT Monitor class that wraps the new implementation."""

    def __init__(self):
        """Initialize the OSINT monitor (v1 compatible interface)."""
        self._new_monitor = NewOSINTMonitor(use_database=True, enable_sentiment=False)
        self.mentions = []
        self.twitter_client = None

        # Compatibility: check if Twitter is available
        if self._new_monitor.sources['twitter'].is_available():
            self.twitter_client = self._new_monitor.sources['twitter'].client
            print("✓ Twitter API initialized successfully")

    def search_google(self, keyword: str, num_results: int = 10) -> List[Dict]:
        """Search Google for keyword mentions (v1 compatible)."""
        async def _search():
            mentions = await self._new_monitor.sources['google'].search(keyword, num_results)
            return self._mentions_to_dicts(mentions)

        return asyncio.run(_search())

    def search_twitter(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """Search Twitter for keyword mentions (v1 compatible)."""
        async def _search():
            mentions = await self._new_monitor.sources['twitter'].search(keyword, max_results)
            return self._mentions_to_dicts(mentions)

        return asyncio.run(_search())

    def scrape_websites(self, keyword: str, urls: List[str]) -> List[Dict]:
        """Scrape websites for keyword mentions (v1 compatible)."""
        # This was not async in the original, keeping it simple
        mentions = []
        print(f"Scraping websites for '{keyword}'...")

        try:
            import requests
            from bs4 import BeautifulSoup
            import time

            for url in urls:
                try:
                    headers = {'User-Agent': 'OSINT-Monitor/2.0 (Educational Purpose)'}
                    response = requests.get(url, headers=headers, timeout=10)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.content, 'html.parser')
                    for script in soup(['script', 'style']):
                        script.decompose()

                    text = soup.get_text()

                    if keyword.lower() in text.lower():
                        lines = text.split('\n')
                        matching_lines = [line.strip() for line in lines
                                        if keyword.lower() in line.lower() and line.strip()]

                        mention = {
                            'source': 'Web Scraping',
                            'keyword': keyword,
                            'url': url,
                            'title': soup.title.string if soup.title else url,
                            'timestamp': datetime.now().isoformat(),
                            'content': ' | '.join(matching_lines[:3])
                        }
                        mentions.append(mention)
                        print(f"  Found mention in: {url}")
                    else:
                        print(f"  No mention found in: {url}")

                    time.sleep(1)

                except Exception as e:
                    print(f"  Error scraping {url}: {e}")

        except ImportError:
            print("Web scraping dependencies not available")

        return mentions

    def collect_mentions(
        self,
        keyword: str,
        google_results: int = 10,
        twitter_results: int = 10,
        scrape_urls: List[str] = None
    ) -> List[Dict]:
        """Collect mentions from all sources (v1 compatible)."""
        all_mentions = []

        print(f"\n{'='*60}")
        print(f"Collecting mentions for keyword: '{keyword}'")
        print(f"{'='*60}\n")

        # Collect from Google
        google_mentions = self.search_google(keyword, google_results)
        all_mentions.extend(google_mentions)
        print(f"\nGoogle: {len(google_mentions)} mentions found\n")

        # Collect from Twitter
        twitter_mentions = self.search_twitter(keyword, twitter_results)
        all_mentions.extend(twitter_mentions)
        print(f"\nTwitter: {len(twitter_mentions)} mentions found\n")

        # Collect from websites
        if scrape_urls:
            web_mentions = self.scrape_websites(keyword, scrape_urls)
            all_mentions.extend(web_mentions)
            print(f"\nWeb Scraping: {len(web_mentions)} mentions found\n")

        self.mentions.extend(all_mentions)

        print(f"{'='*60}")
        print(f"Total mentions collected: {len(all_mentions)}")
        print(f"{'='*60}\n")

        return all_mentions

    def save_to_csv(self, filename: str = None):
        """Save collected mentions to CSV (v1 compatible)."""
        if not self.mentions:
            print("No mentions to save.")
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'mentions_{timestamp}.csv'

        try:
            import pandas as pd
            df = pd.DataFrame(self.mentions)
            df.to_csv(filename, index=False)
            print(f"\n✓ Mentions saved to: {filename}")
            print(f"  Total records: {len(self.mentions)}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def _mentions_to_dicts(self, mentions: List[Mention]) -> List[Dict]:
        """Convert Mention objects to dictionaries for v1 compatibility."""
        return [
            {
                'source': m.source.value.capitalize(),
                'keyword': m.keyword,
                'url': m.url,
                'title': m.title,
                'timestamp': m.timestamp.isoformat(),
                'content': m.content
            }
            for m in mentions
        ]


def main():
    """Main function (v1 compatible)."""
    import sys

    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║          OSINT Social Media Monitoring App                 ║
    ║          (Running on v2.0 Platform)                        ║
    ║                                                            ║
    ║  ETHICAL USAGE NOTICE:                                     ║
    ║  • For legitimate OSINT research only                      ║
    ║  • Respect robots.txt and ToS                              ║
    ║  • Comply with data protection laws                        ║
    ║  • Only collect public information                         ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    # Initialize monitor
    monitor = OSINTMonitor()

    # Get keyword
    if len(sys.argv) > 1:
        keyword = ' '.join(sys.argv[1:])
    else:
        keyword = input("Enter keyword to monitor: ").strip()

    if not keyword:
        print("Error: Keyword is required")
        sys.exit(1)

    # Optional: URLs to scrape
    scrape_urls = []

    # Collect mentions
    mentions = monitor.collect_mentions(
        keyword=keyword,
        google_results=10,
        twitter_results=10,
        scrape_urls=scrape_urls if scrape_urls else None
    )

    # Save to CSV
    if mentions:
        monitor.save_to_csv()

        # Display sample of results
        print("\nSample of collected mentions:")
        print("-" * 60)
        for i, mention in enumerate(mentions[:5], 1):
            print(f"{i}. [{mention['source']}] {mention['title']}")
            print(f"   URL: {mention['url']}")
            if mention['content']:
                content_preview = mention['content'][:100]
                print(f"   Content: {content_preview}...")
            print()
    else:
        print("\nNo mentions found.")


if __name__ == "__main__":
    main()

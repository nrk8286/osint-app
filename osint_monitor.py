#!/usr/bin/env python3
"""
OSINT Social Media Monitoring App
Aggregates keyword mentions from Google searches, Twitter, and websites.

ETHICAL USAGE NOTICE:
- This tool is intended for legitimate OSINT research and monitoring only
- Always respect robots.txt and website terms of service
- Do not use for harassment, stalking, or illegal activities
- Comply with data protection regulations (GDPR, CCPA, etc.)
- Rate-limit your requests to avoid overloading servers
- Only collect publicly available information
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Optional imports with graceful error handling
try:
    from googlesearch import search
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Warning: googlesearch-python not available. Google search disabled.")

try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False
    print("Warning: tweepy not available. Twitter search disabled.")

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False
    print("Warning: requests/beautifulsoup4 not available. Web scraping disabled.")

try:
    from recon_ng_wrapper import ReconNgWrapper
    RECON_NG_AVAILABLE = True
except ImportError:
    RECON_NG_AVAILABLE = False
    print("Warning: recon-ng not available. Recon-ng features disabled.")


class OSINTMonitor:
    """Main class for OSINT monitoring and data collection."""
    
    def __init__(self):
        """Initialize the OSINT monitor with API credentials."""
        self.mentions = []
        self.twitter_client = None
        self.recon_ng = None

        # Initialize Twitter client if credentials are available
        if TWITTER_AVAILABLE:
            self._init_twitter_client()

        # Initialize Recon-ng if available
        if RECON_NG_AVAILABLE:
            self._init_recon_ng()
    
    def _init_twitter_client(self):
        """Initialize Twitter API client with credentials from environment variables."""
        try:
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if bearer_token:
                self.twitter_client = tweepy.Client(bearer_token=bearer_token)
                print("✓ Twitter API initialized successfully")
            else:
                print("⚠ Twitter credentials not found in environment variables")
        except Exception as e:
            print(f"⚠ Error initializing Twitter client: {e}")

    def _init_recon_ng(self):
        """Initialize Recon-ng framework."""
        try:
            self.recon_ng = ReconNgWrapper()
            if self.recon_ng.is_available():
                print("✓ Recon-ng framework initialized successfully")
            else:
                print("⚠ Recon-ng not installed. Install with: pip install recon-ng")
                self.recon_ng = None
        except Exception as e:
            print(f"⚠ Error initializing Recon-ng: {e}")
            self.recon_ng = None
    
    def search_google(self, keyword: str, num_results: int = 10) -> List[Dict]:
        """
        Search Google for keyword mentions.
        
        Args:
            keyword: The search term
            num_results: Number of results to retrieve
            
        Returns:
            List of mention dictionaries
        """
        mentions = []
        
        if not GOOGLE_AVAILABLE:
            print("Google search is not available (googlesearch-python not installed)")
            return mentions
        
        try:
            print(f"Searching Google for '{keyword}'...")
            for idx, url in enumerate(search(keyword, num_results=num_results, sleep_interval=2)):
                mention = {
                    'source': 'Google',
                    'keyword': keyword,
                    'url': url,
                    'title': url,  # Basic implementation - could be enhanced with scraping
                    'timestamp': datetime.now().isoformat(),
                    'content': ''
                }
                mentions.append(mention)
                print(f"  Found: {url}")
                
                # Rate limiting to be respectful
                time.sleep(1)
                
        except Exception as e:
            print(f"Error searching Google: {e}")
        
        return mentions
    
    def search_twitter(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        Search Twitter for keyword mentions.
        
        Args:
            keyword: The search term
            max_results: Maximum number of tweets to retrieve
            
        Returns:
            List of mention dictionaries
        """
        mentions = []
        
        if not TWITTER_AVAILABLE or not self.twitter_client:
            print("Twitter search is not available (check credentials)")
            return mentions
        
        try:
            print(f"Searching Twitter for '{keyword}'...")
            
            # Search recent tweets
            response = self.twitter_client.search_recent_tweets(
                query=keyword,
                max_results=min(max_results, 100),  # API limit is 100
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            )
            
            if response.data:
                for tweet in response.data:
                    mention = {
                        'source': 'Twitter',
                        'keyword': keyword,
                        'url': f'https://twitter.com/user/status/{tweet.id}',
                        'title': f'Tweet by user {tweet.author_id}',
                        'timestamp': tweet.created_at.isoformat() if hasattr(tweet, 'created_at') else datetime.now().isoformat(),
                        'content': tweet.text
                    }
                    mentions.append(mention)
                    print(f"  Found tweet: {tweet.text[:50]}...")
            else:
                print("  No tweets found")
                
        except Exception as e:
            print(f"Error searching Twitter: {e}")
        
        return mentions
    
    def scrape_websites(self, keyword: str, urls: List[str]) -> List[Dict]:
        """
        Scrape websites for keyword mentions.

        Args:
            keyword: The search term
            urls: List of URLs to scrape

        Returns:
            List of mention dictionaries
        """
        mentions = []

        if not WEB_SCRAPING_AVAILABLE:
            print("Web scraping is not available (requests/beautifulsoup4 not installed)")
            return mentions

        print(f"Scraping websites for '{keyword}'...")

        for url in urls:
            try:
                # Set a user agent to be respectful
                headers = {
                    'User-Agent': 'OSINT-Monitor/1.0 (Educational Purpose)'
                }

                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove script and style elements
                for script in soup(['script', 'style']):
                    script.decompose()

                # Get text content
                text = soup.get_text()

                # Check if keyword is present
                if keyword.lower() in text.lower():
                    # Find the context around the keyword
                    lines = text.split('\n')
                    matching_lines = [line.strip() for line in lines if keyword.lower() in line.lower() and line.strip()]

                    mention = {
                        'source': 'Web Scraping',
                        'keyword': keyword,
                        'url': url,
                        'title': soup.title.string if soup.title else url,
                        'timestamp': datetime.now().isoformat(),
                        'content': ' | '.join(matching_lines[:3])  # First 3 matching lines
                    }
                    mentions.append(mention)
                    print(f"  Found mention in: {url}")
                else:
                    print(f"  No mention found in: {url}")

                # Rate limiting
                time.sleep(1)

            except Exception as e:
                print(f"  Error scraping {url}: {e}")

        return mentions

    def recon_domain(self, domain: str) -> List[Dict]:
        """
        Perform domain reconnaissance using Recon-ng.

        Args:
            domain: The domain to analyze

        Returns:
            List of reconnaissance results
        """
        results = []

        if not RECON_NG_AVAILABLE or not self.recon_ng:
            print("Recon-ng is not available")
            return results

        print(f"Performing reconnaissance on domain: {domain}...")

        # Enumerate the domain
        enum_results = self.recon_ng.enumerate_domain(domain)

        for result in enum_results:
            result['keyword'] = domain
            results.append(result)
            print(f"  Found {result['type']} information")

        return results

    def harvest_emails(self, domain: str) -> List[Dict]:
        """
        Harvest email addresses for a domain using Recon-ng.

        Args:
            domain: The domain to harvest emails from

        Returns:
            List of harvested email results
        """
        results = []

        if not RECON_NG_AVAILABLE or not self.recon_ng:
            print("Recon-ng is not available")
            return results

        print(f"Harvesting emails for domain: {domain}...")

        email_results = self.recon_ng.harvest_emails(domain)

        for email in email_results:
            email['keyword'] = domain
            results.append(email)

        if results:
            print(f"  Found {len(results)} email addresses")

        return results
    
    def collect_mentions(self, keyword: str, google_results: int = 10,
                        twitter_results: int = 10, scrape_urls: List[str] = None,
                        use_recon_ng: bool = False) -> List[Dict]:
        """
        Collect mentions from all sources.

        Args:
            keyword: The search term
            google_results: Number of Google results to retrieve
            twitter_results: Number of Twitter results to retrieve
            scrape_urls: List of URLs to scrape
            use_recon_ng: Whether to use Recon-ng for domain reconnaissance

        Returns:
            Combined list of all mentions
        """
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

        # Perform Recon-ng reconnaissance if enabled and keyword looks like a domain
        if use_recon_ng and self.recon_ng and self.recon_ng.is_available():
            # Check if keyword looks like a domain (basic heuristic)
            if '.' in keyword and not ' ' in keyword:
                recon_results = self.recon_domain(keyword)
                all_mentions.extend(recon_results)
                print(f"\nRecon-ng: {len(recon_results)} reconnaissance results found\n")

                # Also try to harvest emails
                email_results = self.harvest_emails(keyword)
                all_mentions.extend(email_results)
                print(f"Email Harvesting: {len(email_results)} emails found\n")

        self.mentions.extend(all_mentions)

        print(f"{'='*60}")
        print(f"Total mentions collected: {len(all_mentions)}")
        print(f"{'='*60}\n")

        return all_mentions
    
    def save_to_csv(self, filename: str = None):
        """
        Save collected mentions to a CSV file.
        
        Args:
            filename: Output filename (default: mentions_TIMESTAMP.csv)
        """
        if not self.mentions:
            print("No mentions to save.")
            return
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'mentions_{timestamp}.csv'
        
        try:
            df = pd.DataFrame(self.mentions)
            df.to_csv(filename, index=False)
            print(f"\n✓ Mentions saved to: {filename}")
            print(f"  Total records: {len(self.mentions)}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")


def main():
    """Main function to run the OSINT monitor."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║          OSINT Social Media Monitoring App                 ║
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
    
    # Example usage - customize as needed
    if len(sys.argv) > 1:
        keyword = ' '.join(sys.argv[1:])
    else:
        keyword = input("Enter keyword to monitor: ").strip()
        
    if not keyword:
        print("Error: Keyword is required")
        sys.exit(1)
    
    # Optional: URLs to scrape (example)
    # You can customize this list or make it configurable
    scrape_urls = [
        # Example URLs - replace with your targets
        # 'https://example.com',
        # 'https://news.ycombinator.com'
    ]
    
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

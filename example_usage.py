#!/usr/bin/env python3
"""
Example usage of the OSINT Monitor
This demonstrates how to use the OSINTMonitor class programmatically.
"""

from osint_monitor import OSINTMonitor

def main():
    """Example of programmatic usage."""
    
    # Initialize the monitor
    monitor = OSINTMonitor()
    
    # Example 1: Search for a single keyword
    print("\n=== Example 1: Single Keyword Search ===")
    keyword = "cybersecurity"
    mentions = monitor.collect_mentions(
        keyword=keyword,
        google_results=5,      # Get 5 Google results
        twitter_results=5,     # Get 5 tweets
        scrape_urls=[
            # Add URLs to scrape (optional)
            # 'https://example.com',
        ]
    )
    
    # Save results
    if mentions:
        monitor.save_to_csv(f"{keyword}_mentions.csv")
    
    # Example 2: Monitor multiple keywords
    print("\n\n=== Example 2: Multiple Keywords ===")
    keywords = ["OSINT", "threat intelligence", "data breach"]
    
    all_mentions = []
    for kw in keywords:
        print(f"\nSearching for: {kw}")
        mentions = monitor.collect_mentions(
            keyword=kw,
            google_results=3,
            twitter_results=3
        )
        all_mentions.extend(mentions)
    
    # Save all mentions to a single file
    if all_mentions:
        monitor.mentions = all_mentions
        monitor.save_to_csv("multi_keyword_mentions.csv")
    
    # Example 3: Custom web scraping
    print("\n\n=== Example 3: Custom Web Scraping ===")
    custom_urls = [
        'https://news.ycombinator.com',
        'https://www.reddit.com/r/programming',
    ]
    
    web_mentions = monitor.scrape_websites(
        keyword="Python",
        urls=custom_urls
    )
    
    if web_mentions:
        print(f"Found {len(web_mentions)} mentions in custom URLs")

if __name__ == "__main__":
    main()

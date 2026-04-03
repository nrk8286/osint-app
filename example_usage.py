#!/usr/bin/env python3
"""
Example usage of the OSINT Monitor v2.0
Demonstrates how to use the OSINTMonitor class programmatically.
"""

from osint_monitor import OSINTMonitor


def main():
    """Example of programmatic usage."""

    monitor = OSINTMonitor()

    # ── Example 1: Search all sources for a keyword ──────────────────────
    print("\n=== Example 1: Full Multi-Source Search ===")
    keyword = "cybersecurity"
    mentions = monitor.collect_mentions(
        keyword=keyword,
        google_results=5,
        twitter_results=5,
        reddit_results=5,
        github_results=5,
    )

    if mentions:
        monitor.save_to_csv(f"{keyword}_mentions.csv")
        monitor.save_to_json(f"{keyword}_mentions.json")

    # ── Example 2: Search specific sources only ──────────────────────────
    print("\n\n=== Example 2: Targeted Source Search ===")
    mentions = monitor.collect_mentions(
        keyword="machine learning",
        sources=["reddit", "github"],
        reddit_results=10,
        github_results=10,
    )

    # ── Example 3: Multiple keywords ─────────────────────────────────────
    print("\n\n=== Example 3: Multiple Keywords ===")
    keywords = ["OSINT", "threat intelligence", "data breach"]

    for kw in keywords:
        monitor.collect_mentions(
            keyword=kw,
            sources=["google", "reddit"],
            google_results=3,
            reddit_results=3,
        )

    # Save all results combined
    if monitor.mentions:
        monitor.save_to_csv("multi_keyword_mentions.csv")
        monitor.save_to_json("multi_keyword_mentions.json")

    # ── Example 4: Custom web scraping ───────────────────────────────────
    print("\n\n=== Example 4: Custom Web Scraping ===")
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

    # ── Example 5: Domain reconnaissance ─────────────────────────────────
    print("\n\n=== Example 5: Domain Reconnaissance ===")
    monitor.dns_lookup("example.com")
    monitor.ip_info("example.com")
    monitor.check_headers("https://example.com")

    # ── Example 6: Summary report and filtering ──────────────────────────
    print("\n\n=== Example 6: Summary & Filtering ===")
    report = monitor.summary_report()

    reddit_only = monitor.filter_mentions(source="Reddit")
    print(f"\nReddit-only results: {len(reddit_only)}")

    high_relevance = monitor.filter_mentions(min_relevance=0.5)
    print(f"High relevance results: {len(high_relevance)}")


if __name__ == "__main__":
    main()

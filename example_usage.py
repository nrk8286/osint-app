#!/usr/bin/env python3
"""
Example usage of the OSINT Monitor v2.0
Demonstrates programmatic usage of OSINTMonitor and NetworkRecon.
"""

import asyncio
from osint_app.core.monitor import OSINTMonitor, collect_mentions_sync
from osint_app.recon.network import NetworkRecon


async def main():
    """Async examples of programmatic usage."""

    monitor = OSINTMonitor(use_database=False, enable_sentiment=False)

    # ── Example 1: Search all sources ────────────────────────────────
    print("\n=== Example 1: Full Multi-Source Search ===")
    mentions = await monitor.collect_mentions(
        keyword="cybersecurity",
        google_results=5,
        twitter_results=5,
        reddit_results=5,
        news_results=5,
        github_results=5,
    )

    if mentions:
        monitor.save_to_csv("cybersecurity_mentions.csv")
        monitor.save_to_json("cybersecurity_mentions.json")

    # ── Example 2: Search specific sources only ──────────────────────
    print("\n=== Example 2: Targeted Source Search ===")
    await monitor.collect_mentions(
        keyword="machine learning",
        sources=["reddit", "github"],
        reddit_results=10,
        github_results=10,
    )

    # ── Example 3: Multiple keywords ─────────────────────────────────
    print("\n=== Example 3: Multiple Keywords ===")
    for kw in ["OSINT", "threat intelligence", "data breach"]:
        await monitor.collect_mentions(
            keyword=kw,
            sources=["google", "reddit"],
            google_results=3,
            reddit_results=3,
        )

    if monitor.mentions:
        monitor.save_to_csv("multi_keyword_mentions.csv")
        monitor.save_to_json("multi_keyword_mentions.json")

    # ── Example 4: Domain reconnaissance ─────────────────────────────
    print("\n=== Example 4: Domain Reconnaissance ===")
    recon = NetworkRecon()

    dns = recon.dns_lookup("example.com")
    print(f"DNS records: {dns.data}")

    ip = recon.ip_info("example.com")
    print(f"IP info: {ip.data}")

    headers = recon.check_headers("https://example.com")
    print(f"Missing security headers: {headers.data.get('missing_security_headers', [])}")

    # ── Example 5: Summary report and filtering ──────────────────────
    print("\n=== Example 5: Summary & Filtering ===")
    monitor.summary_report()

    reddit_only = monitor.filter_mentions(source="reddit")
    print(f"Reddit-only results: {len(reddit_only)}")

    high_relevance = monitor.filter_mentions(min_relevance=0.5)
    print(f"High relevance results: {len(high_relevance)}")


def sync_example():
    """Synchronous usage example."""
    print("\n=== Sync Example ===")
    mentions = collect_mentions_sync(keyword="python", google_results=3, github_results=3)
    print(f"Found {len(mentions)} mentions synchronously")


if __name__ == "__main__":
    asyncio.run(main())

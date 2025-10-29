#!/usr/bin/env python3
"""Example usage of OSINT App."""

from osint_app.app import OSINTApp
from osint_app.models import SearchQuery


def main():
    """Run example OSINT monitoring."""
    
    print("=" * 60)
    print("OSINT App - Example Usage".center(60))
    print("=" * 60)
    print()
    
    # Initialize the app
    app = OSINTApp()
    
    # Example 1: Simple keyword search
    print("Example 1: Searching for 'Python' across all platforms...")
    print("-" * 60)
    
    mentions = app.search(
        keywords=['Python'],
        platforms=['twitter', 'reddit', 'web'],
        max_results=5
    )
    
    print(f"Found {len(mentions)} mentions\n")
    
    for i, mention in enumerate(mentions, 1):
        print(f"[{i}] {mention.platform} - {mention.author}")
        print(f"    {mention.content[:80]}...")
        print(f"    Sentiment: {mention.sentiment}")
        print(f"    Engagement: {mention.engagement.get('total', 0)}")
        print()
    
    # Example 2: Get sentiment summary
    print("\nExample 2: Sentiment Analysis")
    print("-" * 60)
    
    sentiment_summary = app.get_sentiment_summary()
    print(f"Positive: {sentiment_summary['positive']}")
    print(f"Negative: {sentiment_summary['negative']}")
    print(f"Neutral: {sentiment_summary['neutral']}")
    
    # Example 3: Platform distribution
    print("\nExample 3: Platform Distribution")
    print("-" * 60)
    
    platform_summary = app.get_platform_summary()
    for platform, count in platform_summary.items():
        print(f"{platform}: {count}")
    
    # Example 4: Filter by sentiment
    print("\nExample 4: Filtering Positive Mentions")
    print("-" * 60)
    
    positive_mentions = app.filter_by_sentiment('positive')
    print(f"Found {len(positive_mentions)} positive mentions")
    
    for mention in positive_mentions[:3]:
        print(f"  • {mention.author}: {mention.content[:60]}...")
    
    # Example 5: Engagement metrics
    print("\nExample 5: Total Engagement Metrics")
    print("-" * 60)
    
    engagement = app.get_engagement_summary()
    print(f"Total Likes: {engagement['likes']}")
    print(f"Total Shares: {engagement['shares']}")
    print(f"Total Comments: {engagement['comments']}")
    print(f"Total Engagement: {engagement['total']}")
    
    # Example 6: Export results
    print("\nExample 6: Exporting Results")
    print("-" * 60)
    
    exported_data = app.export_results(mentions[:3])
    print(f"Exported {len(exported_data)} mentions to data structure")
    print("\nSample exported data:")
    import json
    print(json.dumps(exported_data[0], indent=2, default=str))
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!".center(60))
    print("=" * 60)


if __name__ == '__main__':
    main()

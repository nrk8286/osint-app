#!/usr/bin/env python3
"""
Example usage of the OSINT App.
This script demonstrates various features of the OSINT monitoring tool.
"""
from osint_app.collectors.web_collector import (
    WebSearchCollector, NewsCollector, SocialMediaCollector
)
from osint_app.analyzers.sentiment import SentimentAnalyzer
from osint_app.storage.database import Database
from osint_app.utils.reporter import ReportGenerator


def main():
    """Run example OSINT monitoring workflow."""
    print("=" * 60)
    print("OSINT App - Example Usage")
    print("=" * 60)
    
    # 1. Initialize components
    print("\n1. Initializing components...")
    db = Database("./data/example_osint.db")
    analyzer = SentimentAnalyzer()
    reporter = ReportGenerator()
    
    # 2. Define keywords to monitor
    keywords = ["Python", "Machine Learning", "AI"]
    print(f"   Keywords: {', '.join(keywords)}")
    
    # 3. Collect data from different sources
    print("\n2. Collecting mentions...")
    all_mentions = []
    
    # Web search
    print("   - Collecting from web search...")
    web_collector = WebSearchCollector(keywords, max_results=5)
    web_mentions = web_collector.collect()
    all_mentions.extend(web_mentions)
    print(f"     Found {len(web_mentions)} mentions")
    
    # News
    print("   - Collecting from news...")
    news_collector = NewsCollector(keywords, max_results=5)
    news_mentions = news_collector.collect()
    all_mentions.extend(news_mentions)
    print(f"     Found {len(news_mentions)} mentions")
    
    # Social media
    print("   - Collecting from social media...")
    social_collector = SocialMediaCollector(keywords, platforms=["twitter", "reddit"])
    social_mentions = social_collector.collect()
    all_mentions.extend(social_mentions)
    print(f"     Found {len(social_mentions)} mentions")
    
    print(f"\n   Total mentions collected: {len(all_mentions)}")
    
    # 4. Analyze sentiment
    print("\n3. Analyzing sentiment...")
    all_mentions = analyzer.analyze_batch(all_mentions)
    stats = analyzer.get_statistics(all_mentions)
    
    print(f"   Positive: {stats['positive']} ({stats['positive_pct']:.1f}%)")
    print(f"   Negative: {stats['negative']} ({stats['negative_pct']:.1f}%)")
    print(f"   Neutral:  {stats['neutral']} ({stats['neutral_pct']:.1f}%)")
    
    # 5. Save to database
    print("\n4. Saving to database...")
    db.save_mentions(all_mentions)
    db.save_query(keywords, ["web", "news", "social"], len(all_mentions))
    print(f"   Saved {len(all_mentions)} mentions")
    
    # 6. Generate report
    print("\n5. Generating report...")
    report_text = reporter.generate_summary(all_mentions, stats)
    
    # Save to file
    output_file = "example_report.txt"
    reporter.save_report(report_text, output_file)
    print(f"   Report saved to {output_file}")
    
    # 7. Display some examples
    print("\n6. Example mentions:")
    for i, mention in enumerate(all_mentions[:3], 1):
        sentiment_data = mention.get('sentiment', {})
        print(f"\n   {i}. [{mention['source']}] {mention['author']}")
        print(f"      Text: {mention['text'][:80]}...")
        print(f"      Sentiment: {sentiment_data.get('sentiment', 'N/A')}")
        print(f"      Keywords: {', '.join(mention['keywords'])}")
    
    # 8. Show database statistics
    print("\n7. Database statistics:")
    db_stats = db.get_statistics()
    print(f"   Total mentions in DB: {db_stats['total_mentions']}")
    print(f"   Total queries: {db_stats['total_queries']}")
    
    # Cleanup
    db.close()
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

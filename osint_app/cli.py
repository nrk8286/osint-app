#!/usr/bin/env python3
"""
OSINT App - Command Line Interface
Social Media Monitoring Tool
"""
import click
from colorama import Fore, Style, init
from typing import List

from osint_app.collectors.web_collector import (
    WebSearchCollector, NewsCollector, SocialMediaCollector
)
from osint_app.analyzers.sentiment import SentimentAnalyzer
from osint_app.storage.database import Database
from osint_app.utils.config import Config
from osint_app.utils.reporter import ReportGenerator

# Initialize colorama for cross-platform colored output
init(autoreset=True)


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """OSINT App - Social Media Monitoring Tool"""
    pass


@cli.command()
@click.option('--keywords', '-k', multiple=True, required=True, 
              help='Keywords to monitor (can specify multiple times)')
@click.option('--sources', '-s', multiple=True, 
              default=['web', 'news', 'social'],
              help='Data sources (web, news, social)')
@click.option('--max-results', '-m', default=10, 
              help='Maximum results per source')
def collect(keywords: tuple, sources: tuple, max_results: int):
    """Collect mentions from various sources."""
    click.echo(f"{Fore.CYAN}OSINT App - Starting Collection{Style.RESET_ALL}")
    click.echo(f"Keywords: {', '.join(keywords)}")
    click.echo(f"Sources: {', '.join(sources)}")
    click.echo("-" * 60)
    
    config = Config()
    db = Database(config.database_path)
    analyzer = SentimentAnalyzer()
    
    all_mentions = []
    keywords_list = list(keywords)
    
    # Collect from different sources
    if 'web' in sources:
        click.echo(f"{Fore.YELLOW}Collecting from web search...{Style.RESET_ALL}")
        collector = WebSearchCollector(keywords_list, max_results)
        mentions = collector.collect()
        all_mentions.extend(mentions)
        click.echo(f"{Fore.GREEN}✓ Collected {len(mentions)} mentions from web{Style.RESET_ALL}")
    
    if 'news' in sources:
        click.echo(f"{Fore.YELLOW}Collecting from news...{Style.RESET_ALL}")
        collector = NewsCollector(keywords_list, max_results)
        mentions = collector.collect()
        all_mentions.extend(mentions)
        click.echo(f"{Fore.GREEN}✓ Collected {len(mentions)} mentions from news{Style.RESET_ALL}")
    
    if 'social' in sources:
        click.echo(f"{Fore.YELLOW}Collecting from social media...{Style.RESET_ALL}")
        platforms = ['twitter', 'reddit']
        collector = SocialMediaCollector(keywords_list, platforms)
        mentions = collector.collect()
        all_mentions.extend(mentions)
        click.echo(f"{Fore.GREEN}✓ Collected {len(mentions)} mentions from social media{Style.RESET_ALL}")
    
    # Analyze sentiment
    click.echo(f"\n{Fore.YELLOW}Analyzing sentiment...{Style.RESET_ALL}")
    all_mentions = analyzer.analyze_batch(all_mentions)
    
    # Save to database
    click.echo(f"{Fore.YELLOW}Saving to database...{Style.RESET_ALL}")
    db.save_mentions(all_mentions)
    db.save_query(keywords_list, list(sources), len(all_mentions))
    
    click.echo(f"\n{Fore.GREEN}✓ Collection complete!{Style.RESET_ALL}")
    click.echo(f"Total mentions collected: {len(all_mentions)}")
    
    # Show sentiment summary
    stats = analyzer.get_statistics(all_mentions)
    click.echo(f"\nSentiment Summary:")
    click.echo(f"  Positive: {stats['positive']} ({stats['positive_pct']:.1f}%)")
    click.echo(f"  Negative: {stats['negative']} ({stats['negative_pct']:.1f}%)")
    click.echo(f"  Neutral:  {stats['neutral']} ({stats['neutral_pct']:.1f}%)")
    
    db.close()


@cli.command()
@click.option('--limit', '-l', default=20, help='Number of mentions to show')
@click.option('--source', '-s', help='Filter by source')
@click.option('--keyword', '-k', help='Filter by keyword')
@click.option('--sentiment', help='Filter by sentiment (positive/negative/neutral)')
def list_mentions(limit: int, source: str, keyword: str, sentiment: str):
    """List collected mentions."""
    config = Config()
    db = Database(config.database_path)
    
    # Get mentions
    if sentiment:
        mentions = db.get_by_sentiment(sentiment, limit)
    else:
        mentions = db.get_mentions(limit, source, keyword)
    
    if not mentions:
        click.echo(f"{Fore.YELLOW}No mentions found.{Style.RESET_ALL}")
        db.close()
        return
    
    click.echo(f"{Fore.CYAN}Found {len(mentions)} mention(s){Style.RESET_ALL}")
    click.echo("=" * 80)
    
    for i, mention in enumerate(mentions, 1):
        source_name = mention.get('source', 'unknown')
        author = mention.get('author', 'unknown')
        text = mention.get('text', '')
        sentiment_data = mention.get('sentiment', {})
        sentiment_label = sentiment_data.get('sentiment', 'N/A')
        polarity = sentiment_data.get('polarity', 0)
        
        # Color code by sentiment
        if sentiment_label == 'positive':
            sentiment_color = Fore.GREEN
        elif sentiment_label == 'negative':
            sentiment_color = Fore.RED
        else:
            sentiment_color = Fore.YELLOW
        
        click.echo(f"\n{i}. [{source_name}] by {author}")
        click.echo(f"   {text[:150]}{'...' if len(text) > 150 else ''}")
        click.echo(f"   Sentiment: {sentiment_color}{sentiment_label}{Style.RESET_ALL} (polarity: {polarity:.2f})")
        click.echo(f"   Keywords: {', '.join(mention.get('keywords', []))}")
    
    click.echo("\n" + "=" * 80)
    db.close()


@cli.command()
def stats():
    """Show database statistics."""
    config = Config()
    db = Database(config.database_path)
    
    stats = db.get_statistics()
    
    click.echo(f"{Fore.CYAN}DATABASE STATISTICS{Style.RESET_ALL}")
    click.echo("=" * 60)
    click.echo(f"Total Mentions: {stats['total_mentions']}")
    click.echo(f"Total Queries: {stats['total_queries']}")
    
    click.echo(f"\n{Fore.YELLOW}Sources:{Style.RESET_ALL}")
    for source, count in stats['sources'].items():
        click.echo(f"  {source}: {count}")
    
    click.echo(f"\n{Fore.YELLOW}Sentiments:{Style.RESET_ALL}")
    sentiments = stats['sentiments']
    total = stats['total_mentions']
    if total > 0:
        click.echo(f"  {Fore.GREEN}Positive:{Style.RESET_ALL} {sentiments['positive']} ({sentiments['positive']/total*100:.1f}%)")
        click.echo(f"  {Fore.RED}Negative:{Style.RESET_ALL} {sentiments['negative']} ({sentiments['negative']/total*100:.1f}%)")
        click.echo(f"  {Fore.YELLOW}Neutral:{Style.RESET_ALL}  {sentiments['neutral']} ({sentiments['neutral']/total*100:.1f}%)")
    
    db.close()


@cli.command()
@click.option('--format', '-f', type=click.Choice(['text', 'json']), 
              default='text', help='Report format')
@click.option('--output', '-o', help='Output file (optional)')
@click.option('--limit', '-l', default=100, help='Number of mentions to include')
def report(format: str, output: str, limit: int):
    """Generate a report from collected data."""
    config = Config()
    db = Database(config.database_path)
    analyzer = SentimentAnalyzer()
    reporter = ReportGenerator()
    
    # Get mentions
    mentions = db.get_mentions(limit)
    
    if not mentions:
        click.echo(f"{Fore.YELLOW}No mentions found to generate report.{Style.RESET_ALL}")
        db.close()
        return
    
    # Get sentiment statistics
    stats = analyzer.get_statistics(mentions)
    
    # Generate report
    if format == 'json':
        report_content = reporter.generate_json(mentions, stats)
    else:
        report_content = reporter.generate_summary(mentions, stats)
    
    # Output report
    if output:
        reporter.save_report(report_content, output)
        click.echo(f"{Fore.GREEN}✓ Report saved to {output}{Style.RESET_ALL}")
    else:
        click.echo(report_content)
    
    db.close()


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear all data?')
def clear():
    """Clear all data from the database."""
    config = Config()
    db = Database(config.database_path)
    db.clear_all()
    click.echo(f"{Fore.GREEN}✓ Database cleared{Style.RESET_ALL}")
    db.close()


@cli.command()
def config_info():
    """Show current configuration."""
    config = Config()
    
    click.echo(f"{Fore.CYAN}CONFIGURATION{Style.RESET_ALL}")
    click.echo("=" * 60)
    
    config_dict = config.to_dict()
    for key, value in config_dict.items():
        click.echo(f"{key}: {value}")


if __name__ == '__main__':
    cli()

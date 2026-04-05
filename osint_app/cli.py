"""Enhanced CLI for OSINT monitoring platform using Rich."""

import asyncio
import sys
from typing import Optional
import argparse

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich import print as rprint

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich library not available. Install with: pip install rich")

from osint_app.core.monitor import OSINTMonitor
from osint_app.models.schemas import Mention


class OSINTCLI:
    """Enhanced CLI interface for OSINT monitoring."""

    def __init__(self):
        """Initialize CLI."""
        self.console = Console() if RICH_AVAILABLE else None
        self.monitor = OSINTMonitor(use_database=True, enable_sentiment=True)

    def print_banner(self):
        """Print application banner."""
        if not RICH_AVAILABLE:
            print("OSINT Monitoring Platform v2.0")
            return

        banner = """
╔═══════════════════════════════════════════════════════════╗
║      OSINT Monitoring Platform v2.0                        ║
║      Production-Ready Intelligence Gathering               ║
╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(Panel(banner, style="bold blue"))

    def print_mentions_table(self, mentions: list[Mention]):
        """Print mentions in a formatted table.

        Args:
            mentions: List of mentions to display
        """
        if not RICH_AVAILABLE:
            for i, m in enumerate(mentions[:10], 1):
                print(f"{i}. [{m.source.value}] {m.title}")
                print(f"   URL: {m.url}")
                if m.sentiment:
                    print(f"   Sentiment: {m.sentiment.value}")
                print()
            return

        table = Table(title="Collected Mentions", show_lines=True)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Source", style="magenta", width=10)
        table.add_column("Title", style="white", width=40)
        table.add_column("Sentiment", style="green", width=10)
        table.add_column("URL", style="blue", width=30)

        for i, mention in enumerate(mentions[:20], 1):
            sentiment = mention.sentiment.value if mention.sentiment else "N/A"
            sentiment_style = {
                "positive": "green",
                "negative": "red",
                "neutral": "yellow",
                "mixed": "blue",
            }.get(sentiment, "white")

            table.add_row(
                str(i),
                mention.source.value,
                mention.title[:40] + "..." if len(mention.title) > 40 else mention.title,
                f"[{sentiment_style}]{sentiment}[/{sentiment_style}]",
                mention.url[:30] + "..." if len(mention.url) > 30 else mention.url,
            )

        self.console.print(table)

        if len(mentions) > 20:
            self.console.print(f"\n[yellow]Showing 20 of {len(mentions)} total mentions[/yellow]")

    def print_stats(self, stats: dict):
        """Print statistics.

        Args:
            stats: Statistics dictionary
        """
        if not RICH_AVAILABLE:
            print(f"\nStatistics (Last {stats.get('days', 7)} days):")
            print(f"Total Mentions: {stats.get('total_mentions', 0)}")
            print("\nBy Source:")
            for source, count in stats.get("by_source", {}).items():
                print(f"  {source}: {count}")
            print("\nBy Sentiment:")
            for sentiment, count in stats.get("by_sentiment", {}).items():
                print(f"  {sentiment}: {count}")
            return

        self.console.print(f"\n[bold]Statistics (Last {stats.get('days', 7)} days)[/bold]")

        # Create stats table
        table = Table(show_header=False, show_edge=False, box=None)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="yellow", width=10)

        table.add_row("Total Mentions", str(stats.get("total_mentions", 0)))

        self.console.print(table)

        # By source
        if stats.get("by_source"):
            self.console.print("\n[bold cyan]By Source:[/bold cyan]")
            for source, count in stats["by_source"].items():
                self.console.print(f"  • {source}: [yellow]{count}[/yellow]")

        # By sentiment
        if stats.get("by_sentiment"):
            self.console.print("\n[bold cyan]By Sentiment:[/bold cyan]")
            for sentiment, count in stats["by_sentiment"].items():
                color = {"positive": "green", "negative": "red", "neutral": "yellow"}.get(
                    sentiment, "white"
                )
                self.console.print(f"  • {sentiment}: [{color}]{count}[/{color}]")

    async def run_search(
        self,
        keyword: str,
        google: int = 10,
        twitter: int = 10,
        reddit: int = 10,
        news: int = 10,
        output: Optional[str] = None,
    ):
        """Run search with progress indication.

        Args:
            keyword: Search keyword
            google: Number of Google results
            twitter: Number of Twitter results
            reddit: Number of Reddit results
            news: Number of News results
            output: Output filename
        """
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task(f"Searching for '{keyword}'...", total=None)

                mentions = await self.monitor.collect_mentions(
                    keyword=keyword,
                    google_results=google,
                    twitter_results=twitter,
                    reddit_results=reddit,
                    news_results=news,
                    enable_sentiment=True,
                )

                progress.update(task, completed=True)
        else:
            print(f"Searching for '{keyword}'...")
            mentions = await self.monitor.collect_mentions(
                keyword=keyword,
                google_results=google,
                twitter_results=twitter,
                reddit_results=reddit,
                news_results=news,
                enable_sentiment=True,
            )

        # Display results
        if mentions:
            self.print_mentions_table(mentions)

            # Save to file
            if output:
                if output.endswith(".json"):
                    self.monitor.save_to_json(output)
                else:
                    self.monitor.save_to_csv(output)
        else:
            if RICH_AVAILABLE:
                self.console.print("[yellow]No mentions found[/yellow]")
            else:
                print("No mentions found")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OSINT Monitoring Platform - Production-Ready Intelligence Gathering"
    )

    parser.add_argument("keyword", nargs="?", help="Keyword to search for")
    parser.add_argument(
        "--google", type=int, default=10, help="Number of Google results (default: 10)"
    )
    parser.add_argument(
        "--twitter", type=int, default=10, help="Number of Twitter results (default: 10)"
    )
    parser.add_argument(
        "--reddit", type=int, default=10, help="Number of Reddit results (default: 10)"
    )
    parser.add_argument("--news", type=int, default=10, help="Number of News results (default: 10)")
    parser.add_argument("--output", "-o", help="Output filename (CSV or JSON)")
    parser.add_argument("--stats", action="store_true", help="Show statistics from database")
    parser.add_argument("--days", type=int, default=7, help="Days for statistics (default: 7)")

    args = parser.parse_args()

    cli = OSINTCLI()
    cli.print_banner()

    # Show stats mode
    if args.stats:
        stats = cli.monitor.get_stats(days=args.days)
        cli.print_stats(stats)
        return

    # Get keyword
    keyword = args.keyword
    if not keyword:
        if RICH_AVAILABLE:
            keyword = cli.console.input("[bold cyan]Enter keyword to monitor: [/bold cyan]")
        else:
            keyword = input("Enter keyword to monitor: ")

    if not keyword:
        print("Error: Keyword is required")
        sys.exit(1)

    # Run search
    asyncio.run(
        cli.run_search(
            keyword=keyword,
            google=args.google,
            twitter=args.twitter,
            reddit=args.reddit,
            news=args.news,
            output=args.output,
        )
    )


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
OSINT App - Command Line Interface
Social Media Monitoring Tool
"""
import click
from colorama import Fore, Style, init
from typing import List

from osint_app.collectors.web_collector import (
    WebSearchCollector,
    NewsCollector,
    SocialMediaCollector,
)
from osint_app.analyzers.sentiment import SentimentAnalyzer
from osint_app.storage.database import Database
from osint_app.utils.config import Config
from osint_app.utils.reporter import ReportGenerator

# Initialize colorama for cross-platform colored output
init(autoreset=True)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """OSINT App - Social Media Monitoring Tool"""
    pass


@cli.command()
@click.option(
    "--keywords",
    "-k",
    multiple=True,
    required=True,
    help="Keywords to monitor (can specify multiple times)",
)
@click.option(
    "--sources",
    "-s",
    multiple=True,
    default=["web", "news", "social"],
    help="Data sources (web, news, social)",
)
@click.option("--max-results", "-m", default=10, help="Maximum results per source")
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
    if "web" in sources:
        click.echo(f"{Fore.YELLOW}Collecting from web search...{Style.RESET_ALL}")
        collector = WebSearchCollector(keywords_list, max_results)
        mentions = collector.collect()
        all_mentions.extend(mentions)
        click.echo(f"{Fore.GREEN}✓ Collected {len(mentions)} mentions from web{Style.RESET_ALL}")

    if "news" in sources:
        click.echo(f"{Fore.YELLOW}Collecting from news...{Style.RESET_ALL}")
        collector = NewsCollector(keywords_list, max_results)
        mentions = collector.collect()
        all_mentions.extend(mentions)
        click.echo(f"{Fore.GREEN}✓ Collected {len(mentions)} mentions from news{Style.RESET_ALL}")

    if "social" in sources:
        click.echo(f"{Fore.YELLOW}Collecting from social media...{Style.RESET_ALL}")
        platforms = ["twitter", "reddit"]
        collector = SocialMediaCollector(keywords_list, platforms)
        mentions = collector.collect()
        all_mentions.extend(mentions)
        click.echo(
            f"{Fore.GREEN}✓ Collected {len(mentions)} mentions from social media{Style.RESET_ALL}"
        )

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
@click.option("--limit", "-l", default=20, help="Number of mentions to show")
@click.option("--source", "-s", help="Filter by source")
@click.option("--keyword", "-k", help="Filter by keyword")
@click.option("--sentiment", help="Filter by sentiment (positive/negative/neutral)")
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
        source_name = mention.get("source", "unknown")
        author = mention.get("author", "unknown")
        text = mention.get("text", "")
        sentiment_data = mention.get("sentiment", {})
        sentiment_label = sentiment_data.get("sentiment", "N/A")
        polarity = sentiment_data.get("polarity", 0)

        # Color code by sentiment
        if sentiment_label == "positive":
            sentiment_color = Fore.GREEN
        elif sentiment_label == "negative":
            sentiment_color = Fore.RED
        else:
            sentiment_color = Fore.YELLOW

        click.echo(f"\n{i}. [{source_name}] by {author}")
        click.echo(f"   {text[:150]}{'...' if len(text) > 150 else ''}")
        click.echo(
            f"   Sentiment: {sentiment_color}{sentiment_label}{Style.RESET_ALL} (polarity: {polarity:.2f})"
        )
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
    for source, count in stats["sources"].items():
        click.echo(f"  {source}: {count}")

    click.echo(f"\n{Fore.YELLOW}Sentiments:{Style.RESET_ALL}")
    sentiments = stats["sentiments"]
    total = stats["total_mentions"]
    if total > 0:
        click.echo(
            f"  {Fore.GREEN}Positive:{Style.RESET_ALL} {sentiments['positive']} ({sentiments['positive']/total*100:.1f}%)"
        )
        click.echo(
            f"  {Fore.RED}Negative:{Style.RESET_ALL} {sentiments['negative']} ({sentiments['negative']/total*100:.1f}%)"
        )
        click.echo(
            f"  {Fore.YELLOW}Neutral:{Style.RESET_ALL}  {sentiments['neutral']} ({sentiments['neutral']/total*100:.1f}%)"
        )

    db.close()


@cli.command()
@click.option(
    "--format", "-f", type=click.Choice(["text", "json"]), default="text", help="Report format"
)
@click.option("--output", "-o", help="Output file (optional)")
@click.option("--limit", "-l", default=100, help="Number of mentions to include")
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
    if format == "json":
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
@click.confirmation_option(prompt="Are you sure you want to clear all data?")
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


if __name__ == "__main__":
    cli()

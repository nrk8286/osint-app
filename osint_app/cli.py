"""Enhanced CLI for OSINT monitoring platform with interactive menu and recon."""

import argparse
import asyncio
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import IntPrompt, Prompt
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: rich library not available. Install with: pip install rich")

from osint_app.core.monitor import OSINTMonitor
from osint_app.models.schemas import Mention
from osint_app.recon.network import NetworkRecon


class OSINTCLI:
    """Enhanced CLI interface for OSINT monitoring."""

    def __init__(self):
        """Initialize CLI."""
        self.console = Console() if RICH_AVAILABLE else None
        self.monitor = OSINTMonitor(use_database=True, enable_sentiment=True)
        self.recon = NetworkRecon()

    # ── Display helpers ────────────────────────────────────────────────

    def _print(self, text: str, style: str = ""):
        if RICH_AVAILABLE:
            self.console.print(text, style=style)
        else:
            print(text)

    def print_banner(self):
        """Print application banner."""
        banner_text = (
            "\n  OSINT Monitoring Platform v2.0\n"
            "  Production-Ready Intelligence Gathering\n\n"
            "  Sources : Google | Twitter | Reddit | News | GitHub\n"
            "  Recon   : DNS Lookup | IP Geolocation | HTTP Headers\n"
            "  Export  : CSV | JSON | Summary Report\n"
        )
        if RICH_AVAILABLE:
            self.console.print(Panel(banner_text, style="bold blue", title="OSINT Platform"))
        else:
            print("=" * 60)
            print(banner_text)
            print("=" * 60)

    def print_mentions_table(self, mentions: list[Mention]):
        """Print mentions in a formatted table."""
        if not mentions:
            self._print("No mentions to display.", "yellow")
            return

        if not RICH_AVAILABLE:
            for i, m in enumerate(mentions[:20], 1):
                print(f"{i}. [{m.source.value}] {m.title}")
                print(f"   URL: {m.url}")
                if m.sentiment:
                    print(f"   Sentiment: {m.sentiment.value}")
                if m.relevance_score:
                    print(f"   Relevance: {m.relevance_score}")
                print()
            return

        table = Table(title="Collected Mentions", show_lines=True)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Source", style="magenta", width=10)
        table.add_column("Title", style="white", width=35)
        table.add_column("Sentiment", style="green", width=10)
        table.add_column("Relevance", width=9)
        table.add_column("URL", style="blue", width=30)

        for i, mention in enumerate(mentions[:20], 1):
            sentiment = mention.sentiment.value if mention.sentiment else "N/A"
            sentiment_style = {
                "positive": "green",
                "negative": "red",
                "neutral": "yellow",
                "mixed": "blue",
            }.get(sentiment, "white")

            relevance = f"{mention.relevance_score:.2f}" if mention.relevance_score else "N/A"

            table.add_row(
                str(i),
                mention.source.value,
                mention.title[:35] + "..." if len(mention.title) > 35 else mention.title,
                f"[{sentiment_style}]{sentiment}[/{sentiment_style}]",
                relevance,
                mention.url[:30] + "..." if len(mention.url) > 30 else mention.url,
            )

        self.console.print(table)

        if len(mentions) > 20:
            self.console.print(f"\n[yellow]Showing 20 of {len(mentions)} total mentions[/yellow]")

    def print_recon_result(self, result):
        """Print a reconnaissance result."""
        data = result.data

        if RICH_AVAILABLE:
            self.console.print(
                f"\n[bold cyan]{result.recon_type.upper()} - {result.target}[/bold cyan]"
            )
            self.console.print(f"[dim]{result.timestamp.isoformat()}[/dim]\n")
        else:
            print(f"\n{result.recon_type.upper()} - {result.target}")
            print(f"{result.timestamp.isoformat()}\n")

        if "error" in data:
            self._print(f"  Error: {data['error']}", "red")
            return

        if result.recon_type == "dns":
            for key in ("hostname", "aliases", "addresses", "reverse_dns"):
                if key in data:
                    val = data[key]
                    if isinstance(val, list):
                        val = ", ".join(val) if val else "(none)"
                    self._print(f"  {key:15} : {val}", "green")

        elif result.recon_type == "ip_info":
            for key in ("country", "regionName", "city", "isp", "org", "as"):
                if key in data:
                    self._print(f"  {key:15} : {data[key]}", "green")

        elif result.recon_type == "headers":
            self._print(f"  Status Code    : {data.get('status_code', 'N/A')}", "green")
            self._print(f"  Server         : {data.get('server', 'N/A')}", "green")

            sec = data.get("security_headers", {})
            missing = data.get("missing_security_headers", [])

            self._print("\n  Security Headers:", "bold")
            for hdr, val in sec.items():
                if val:
                    self._print(f"    [+] {hdr}: {str(val)[:60]}", "green")
                else:
                    self._print(f"    [-] {hdr}: MISSING", "red" if RICH_AVAILABLE else "")

            if missing:
                self._print(f"\n  {len(missing)} security header(s) missing", "yellow")

    def print_stats(self, stats: dict):
        """Print statistics."""
        if not RICH_AVAILABLE:
            print(f"\nStatistics (Last {stats.get('days', 7)} days):")
            print(f"Total Mentions: {stats.get('total_mentions', 0)}")
            for source, count in stats.get("by_source", {}).items():
                print(f"  {source}: {count}")
            return

        self.console.print(f"\n[bold]Statistics (Last {stats.get('days', 7)} days)[/bold]")

        table = Table(show_header=False, show_edge=False, box=None)
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="yellow", width=10)
        table.add_row("Total Mentions", str(stats.get("total_mentions", 0)))
        self.console.print(table)

        if stats.get("by_source"):
            self.console.print("\n[bold cyan]By Source:[/bold cyan]")
            for source, count in stats["by_source"].items():
                self.console.print(f"  * {source}: [yellow]{count}[/yellow]")

        if stats.get("by_sentiment"):
            self.console.print("\n[bold cyan]By Sentiment:[/bold cyan]")
            for sentiment, count in stats["by_sentiment"].items():
                color = {"positive": "green", "negative": "red", "neutral": "yellow"}.get(
                    sentiment, "white"
                )
                self.console.print(f"  * {sentiment}: [{color}]{count}[/{color}]")

    # ── Search ─────────────────────────────────────────────────────────

    async def run_search(
        self,
        keyword: str,
        google: int = 10,
        twitter: int = 10,
        reddit: int = 10,
        news: int = 10,
        github: int = 10,
        sources: Optional[list] = None,
        output: Optional[str] = None,
    ):
        """Run search with progress indication."""
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
                    github_results=github,
                    sources=sources,
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
                github_results=github,
                sources=sources,
                enable_sentiment=True,
            )

        if mentions:
            self.print_mentions_table(mentions)
            if output:
                if output.endswith(".json"):
                    self.monitor.save_to_json(output)
                else:
                    self.monitor.save_to_csv(output)
        else:
            self._print("No mentions found.", "yellow")

    # ── Interactive menu ───────────────────────────────────────────────

    async def interactive_menu(self):
        """Run an interactive CLI session."""
        self.print_banner()

        menu_items = [
            ("1", "Search all sources"),
            ("2", "Search specific source(s)"),
            ("3", "Domain / IP reconnaissance"),
            ("4", "HTTP header analysis"),
            ("5", "View summary report"),
            ("6", "Filter & browse results"),
            ("7", "Export results (CSV / JSON)"),
            ("8", "Database statistics"),
            ("0", "Exit"),
        ]

        while True:
            self._print("\n--- Main Menu ---", "bold cyan")
            for key, label in menu_items:
                if RICH_AVAILABLE:
                    self.console.print(f"  [green]{key}[/green]) {label}")
                else:
                    print(f"  {key}) {label}")

            choice = input("\n  > ").strip()

            if choice == "1":
                kw = input("  Keyword: ").strip()
                if kw:
                    await self.run_search(keyword=kw)

            elif choice == "2":
                kw = input("  Keyword: ").strip()
                if not kw:
                    continue
                print("  Available: google, twitter, reddit, news, github")
                src = input("  Source(s) comma-separated: ").strip().lower()
                sources = [s.strip() for s in src.split(",") if s.strip()]
                if sources:
                    await self.run_search(keyword=kw, sources=sources)

            elif choice == "3":
                target = input("  Domain or IP: ").strip()
                if target:
                    dns = self.recon.dns_lookup(target)
                    self.print_recon_result(dns)
                    ip = self.recon.ip_info(target)
                    self.print_recon_result(ip)

            elif choice == "4":
                url = input("  URL: ").strip()
                if url:
                    result = self.recon.check_headers(url)
                    self.print_recon_result(result)

            elif choice == "5":
                self.monitor.summary_report()

            elif choice == "6":
                if not self.monitor.mentions:
                    self._print("No results yet. Run a search first.", "yellow")
                    continue
                src = input("  Filter by source (blank=all): ").strip() or None
                results = self.monitor.filter_mentions(source=src)
                self._print(f"\n  Filtered: {len(results)} result(s)", "bold")
                self.print_mentions_table(results)

            elif choice == "7":
                if not self.monitor.mentions:
                    self._print("No results to export.", "yellow")
                    continue
                fmt = input("  Format (csv/json/both) [both]: ").strip().lower() or "both"
                if fmt in ("csv", "both"):
                    self.monitor.save_to_csv()
                if fmt in ("json", "both"):
                    self.monitor.save_to_json()

            elif choice == "8":
                stats = self.monitor.get_stats()
                self.print_stats(stats)

            elif choice == "0":
                self._print("Goodbye!", "green")
                break
            else:
                self._print("Invalid option, try again.", "yellow")


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
    parser.add_argument(
        "--github", type=int, default=10, help="Number of GitHub results (default: 10)"
    )
    parser.add_argument("--output", "-o", help="Output filename (CSV or JSON)")
    parser.add_argument("--stats", action="store_true", help="Show statistics from database")
    parser.add_argument("--days", type=int, default=7, help="Days for statistics (default: 7)")
    parser.add_argument("--sources", help="Comma-separated source list (e.g. google,github,reddit)")
    parser.add_argument("--recon", metavar="DOMAIN", help="Run DNS/IP reconnaissance on a domain")
    parser.add_argument("--headers", metavar="URL", help="Analyze HTTP headers of a URL")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive menu")

    args = parser.parse_args()
    cli = OSINTCLI()

    # Interactive mode
    if args.interactive or (
        not args.keyword and not args.stats and not args.recon and not args.headers
    ):
        asyncio.run(cli.interactive_menu())
        return

    cli.print_banner()

    # Recon mode
    if args.recon:
        dns = cli.recon.dns_lookup(args.recon)
        cli.print_recon_result(dns)
        ip = cli.recon.ip_info(args.recon)
        cli.print_recon_result(ip)
        return

    if args.headers:
        result = cli.recon.check_headers(args.headers)
        cli.print_recon_result(result)
        return

    # Stats mode
    if args.stats:
        stats = cli.monitor.get_stats(days=args.days)
        cli.print_stats(stats)
        return

    # Search mode
    sources = [s.strip() for s in args.sources.split(",")] if args.sources else None

    asyncio.run(
        cli.run_search(
            keyword=args.keyword,
            google=args.google,
            twitter=args.twitter,
            reddit=args.reddit,
            news=args.news,
            github=args.github,
            sources=sources,
            output=args.output,
        )
    )


if __name__ == "__main__":
    main()

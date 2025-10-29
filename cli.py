#!/usr/bin/env python3
"""Command-line interface for OSINT App."""

import argparse
import json
import sys
from datetime import datetime
from typing import List
from osint_app.app import OSINTApp
from osint_app.models import Mention

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    
try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False


def print_header(text: str):
    """Print formatted header."""
    if COLORS_AVAILABLE:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{text.center(60)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*60}{Style.RESET_ALL}\n")
    else:
        print(f"\n{'='*60}")
        print(text.center(60))
        print(f"{'='*60}\n")


def print_success(text: str):
    """Print success message."""
    if COLORS_AVAILABLE:
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    else:
        print(f"✓ {text}")


def print_error(text: str):
    """Print error message."""
    if COLORS_AVAILABLE:
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}", file=sys.stderr)
    else:
        print(f"✗ {text}", file=sys.stderr)


def print_info(text: str):
    """Print info message."""
    if COLORS_AVAILABLE:
        print(f"{Fore.YELLOW}ℹ {text}{Style.RESET_ALL}")
    else:
        print(f"ℹ {text}")


def format_mention(mention: Mention, index: int) -> str:
    """Format a single mention for display."""
    sentiment_emoji = {
        'positive': '😊' if sys.platform != 'win32' else '+',
        'negative': '😞' if sys.platform != 'win32' else '-',
        'neutral': '😐' if sys.platform != 'win32' else '='
    }
    
    sentiment = sentiment_emoji.get(mention.sentiment, '?')
    
    output = []
    if COLORS_AVAILABLE:
        output.append(f"{Fore.BLUE}{Style.BRIGHT}[{index}] {mention.platform}{Style.RESET_ALL}")
        output.append(f"  {Fore.WHITE}Author: {mention.author}{Style.RESET_ALL}")
        output.append(f"  {Fore.WHITE}Content: {mention.content[:80]}...{Style.RESET_ALL}")
        output.append(f"  {Fore.YELLOW}Sentiment: {sentiment} {mention.sentiment}{Style.RESET_ALL}")
        output.append(f"  {Fore.GREEN}Engagement: ♥ {mention.engagement.get('likes', 0)} | "
                     f"↻ {mention.engagement.get('shares', 0)} | "
                     f"💬 {mention.engagement.get('comments', 0)}{Style.RESET_ALL}")
        output.append(f"  {Fore.CYAN}URL: {mention.url}{Style.RESET_ALL}")
    else:
        output.append(f"[{index}] {mention.platform}")
        output.append(f"  Author: {mention.author}")
        output.append(f"  Content: {mention.content[:80]}...")
        output.append(f"  Sentiment: {sentiment} {mention.sentiment}")
        output.append(f"  Engagement: Likes {mention.engagement.get('likes', 0)} | "
                     f"Shares {mention.engagement.get('shares', 0)} | "
                     f"Comments {mention.engagement.get('comments', 0)}")
        output.append(f"  URL: {mention.url}")
    
    return "\n".join(output)


def display_mentions(mentions: List[Mention]):
    """Display mentions in a formatted way."""
    print_header("Search Results")
    
    if not mentions:
        print_info("No mentions found.")
        return
    
    print_success(f"Found {len(mentions)} mentions\n")
    
    for i, mention in enumerate(mentions, 1):
        print(format_mention(mention, i))
        print()


def display_summary(app: OSINTApp):
    """Display summary statistics."""
    print_header("Summary Statistics")
    
    sentiment = app.get_sentiment_summary()
    platforms = app.get_platform_summary()
    engagement = app.get_engagement_summary()
    
    # Sentiment Summary
    print_info("Sentiment Distribution:")
    if TABULATE_AVAILABLE:
        sentiment_data = [[k.capitalize(), v] for k, v in sentiment.items()]
        print(tabulate(sentiment_data, headers=['Sentiment', 'Count'], tablefmt='grid'))
    else:
        for key, value in sentiment.items():
            print(f"  {key.capitalize()}: {value}")
    
    print()
    
    # Platform Summary
    print_info("Platform Distribution:")
    if TABULATE_AVAILABLE:
        platform_data = [[k, v] for k, v in platforms.items()]
        print(tabulate(platform_data, headers=['Platform', 'Count'], tablefmt='grid'))
    else:
        for key, value in platforms.items():
            print(f"  {key}: {value}")
    
    print()
    
    # Engagement Summary
    print_info("Total Engagement:")
    if TABULATE_AVAILABLE:
        engagement_data = [[k.capitalize(), v] for k, v in engagement.items()]
        print(tabulate(engagement_data, headers=['Metric', 'Total'], tablefmt='grid'))
    else:
        for key, value in engagement.items():
            print(f"  {key.capitalize()}: {value}")
    
    print()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='OSINT App - Social Media Monitoring Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s --keywords "Python" "AI" --platforms twitter reddit
  %(prog)s -k "OpenAI" -p twitter --max-results 20
  %(prog)s -k "ChatGPT" --export results.json
        '''
    )
    
    parser.add_argument(
        '-k', '--keywords',
        nargs='+',
        required=True,
        help='Keywords to monitor (space-separated)'
    )
    
    parser.add_argument(
        '-p', '--platforms',
        nargs='+',
        default=['twitter', 'reddit', 'web'],
        choices=['twitter', 'reddit', 'web'],
        help='Platforms to monitor (default: all)'
    )
    
    parser.add_argument(
        '-m', '--max-results',
        type=int,
        default=100,
        help='Maximum results per platform (default: 100)'
    )
    
    parser.add_argument(
        '-e', '--export',
        help='Export results to JSON file'
    )
    
    parser.add_argument(
        '--sentiment',
        choices=['positive', 'negative', 'neutral'],
        help='Filter by sentiment'
    )
    
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Skip displaying summary statistics'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only show summary, not individual mentions'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_header("OSINT App - Social Media Monitoring")
    
    # Initialize app
    app = OSINTApp()
    
    # Search for mentions
    print_info(f"Searching for keywords: {', '.join(args.keywords)}")
    print_info(f"Platforms: {', '.join(args.platforms)}")
    print()
    
    try:
        mentions = app.search(
            keywords=args.keywords,
            platforms=args.platforms,
            max_results=args.max_results
        )
        
        # Filter by sentiment if specified
        if args.sentiment:
            mentions = app.filter_by_sentiment(args.sentiment, mentions)
            print_info(f"Filtered to {args.sentiment} sentiment")
        
        # Display results
        if not args.quiet:
            display_mentions(mentions)
        
        # Display summary
        if not args.no_summary:
            display_summary(app)
        
        # Export if requested
        if args.export:
            try:
                results = app.export_results(mentions)
                with open(args.export, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print_success(f"Results exported to {args.export}")
            except (IOError, OSError) as e:
                print_error(f"Failed to export results: {e}")
            except Exception as e:
                print_error(f"Error during export: {e}")
        
    except Exception as e:
        print_error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

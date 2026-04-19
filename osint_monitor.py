#!/usr/bin/env python3
"""
OSINT Social Media Monitoring App
Aggregates keyword mentions from Google searches, Twitter, websites,
Reddit, GitHub, and performs domain/IP reconnaissance.

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
import json
import time
import socket
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Optional
from collections import Counter

import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ── Color helpers ──────────────────────────────────────────────────────────────

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

    @staticmethod
    def supports_color():
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def colored(text: str, color: str) -> str:
    """Return colored text if terminal supports it."""
    if Colors.supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def print_banner():
    """Print the application banner."""
    banner = f"""
{colored('╔══════════════════════════════════════════════════════════════════╗', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('OSINT Social Media Monitoring App', Colors.BOLD + Colors.GREEN)}  {colored('v2.0', Colors.DIM)}                {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}                                                                  {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('Sources:', Colors.BOLD)} Google | Twitter | Reddit | GitHub | Web       {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('Recon:',   Colors.BOLD)}   DNS Lookup | WHOIS | IP Geolocation           {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('Export:',  Colors.BOLD)}  CSV | JSON | Summary Report                    {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}                                                                  {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('ETHICAL USAGE NOTICE:', Colors.YELLOW)}                                        {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('*', Colors.YELLOW)} For legitimate OSINT research only                         {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('*', Colors.YELLOW)} Respect robots.txt and ToS                                 {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('*', Colors.YELLOW)} Comply with data protection laws                           {colored('║', Colors.CYAN)}
{colored('║', Colors.CYAN)}  {colored('*', Colors.YELLOW)} Only collect public information                             {colored('║', Colors.CYAN)}
{colored('╚══════════════════════════════════════════════════════════════════╝', Colors.CYAN)}
"""
    print(banner)


def print_section(title: str):
    """Print a styled section header."""
    width = 60
    print(f"\n{colored('─' * width, Colors.DIM)}")
    print(f"  {colored(title, Colors.BOLD + Colors.CYAN)}")
    print(f"{colored('─' * width, Colors.DIM)}")


def print_status(msg: str, level: str = "info"):
    """Print a colored status message."""
    icons = {"info": "[-]", "ok": "[+]", "warn": "[!]", "err": "[x]", "search": "[~]"}
    colors = {"info": Colors.BLUE, "ok": Colors.GREEN, "warn": Colors.YELLOW, "err": Colors.RED, "search": Colors.CYAN}
    icon = colored(icons.get(level, "[-]"), colors.get(level, Colors.BLUE))
    print(f"  {icon} {msg}")


# ── Optional imports ───────────────────────────────────────────────────────────

try:
    from googlesearch import search
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    WEB_SCRAPING_AVAILABLE = True
except ImportError:
    WEB_SCRAPING_AVAILABLE = False


# ── Main class ─────────────────────────────────────────────────────────────────

class OSINTMonitor:
    """Main class for OSINT monitoring and data collection."""

    def __init__(self):
        """Initialize the OSINT monitor with API credentials."""
        self.mentions = []
        self.search_history = []
        self.twitter_client = None

        if TWITTER_AVAILABLE:
            self._init_twitter_client()

    def _init_twitter_client(self):
        """Initialize Twitter API client with credentials from environment variables."""
        try:
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            if bearer_token:
                self.twitter_client = tweepy.Client(bearer_token=bearer_token)
                print_status("Twitter API initialized", "ok")
            else:
                print_status("Twitter credentials not found in .env", "warn")
        except Exception as e:
            print_status(f"Error initializing Twitter client: {e}", "err")

    # ── Search sources ─────────────────────────────────────────────────────

    def search_google(self, keyword: str, num_results: int = 10) -> List[Dict]:
        """Search Google for keyword mentions."""
        mentions = []
        if not GOOGLE_AVAILABLE:
            print_status("Google search unavailable (install googlesearch-python)", "warn")
            return mentions

        try:
            print_status(f"Searching Google for '{keyword}'...", "search")
            for url in search(keyword, num_results=num_results, sleep_interval=2):
                mention = {
                    'source': 'Google',
                    'keyword': keyword,
                    'url': url,
                    'title': url,
                    'timestamp': datetime.now().isoformat(),
                    'content': '',
                    'relevance_score': self._calculate_relevance(keyword, url),
                }
                mentions.append(mention)
                print_status(f"Found: {url}", "ok")
                time.sleep(1)
        except Exception as e:
            print_status(f"Google search error: {e}", "err")

        return mentions

    def search_twitter(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """Search Twitter for keyword mentions."""
        mentions = []
        if not TWITTER_AVAILABLE or not self.twitter_client:
            print_status("Twitter search unavailable (check credentials)", "warn")
            return mentions

        try:
            print_status(f"Searching Twitter for '{keyword}'...", "search")
            response = self.twitter_client.search_recent_tweets(
                query=keyword,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'author_id', 'public_metrics']
            )

            if response.data:
                for tweet in response.data:
                    metrics = tweet.public_metrics if hasattr(tweet, 'public_metrics') and tweet.public_metrics else {}
                    mention = {
                        'source': 'Twitter',
                        'keyword': keyword,
                        'url': f'https://twitter.com/user/status/{tweet.id}',
                        'title': f'Tweet by user {tweet.author_id}',
                        'timestamp': tweet.created_at.isoformat() if hasattr(tweet, 'created_at') else datetime.now().isoformat(),
                        'content': tweet.text,
                        'relevance_score': self._calculate_relevance(keyword, tweet.text),
                        'engagement': metrics.get('like_count', 0) + metrics.get('retweet_count', 0),
                    }
                    mentions.append(mention)
                    print_status(f"Tweet: {tweet.text[:60]}...", "ok")
            else:
                print_status("No tweets found", "info")
        except Exception as e:
            print_status(f"Twitter search error: {e}", "err")

        return mentions

    def search_reddit(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """Search Reddit for keyword mentions using the public JSON API."""
        mentions = []
        if not WEB_SCRAPING_AVAILABLE:
            print_status("Reddit search unavailable (install requests)", "warn")
            return mentions

        try:
            print_status(f"Searching Reddit for '{keyword}'...", "search")
            headers = {'User-Agent': 'OSINT-Monitor/2.0 (Educational Purpose)'}
            url = "https://www.reddit.com/search.json"
            params = {'q': keyword, 'limit': min(max_results, 25), 'sort': 'relevance'}

            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for post in data.get('data', {}).get('children', []):
                d = post['data']
                mention = {
                    'source': 'Reddit',
                    'keyword': keyword,
                    'url': f"https://reddit.com{d.get('permalink', '')}",
                    'title': d.get('title', ''),
                    'timestamp': datetime.fromtimestamp(d.get('created_utc', 0)).isoformat(),
                    'content': (d.get('selftext', '') or '')[:500],
                    'relevance_score': self._calculate_relevance(keyword, d.get('title', '') + ' ' + d.get('selftext', '')),
                    'engagement': d.get('score', 0) + d.get('num_comments', 0),
                    'subreddit': d.get('subreddit', ''),
                }
                mentions.append(mention)
                print_status(f"r/{d.get('subreddit', '?')}: {d.get('title', '')[:55]}...", "ok")

            if not mentions:
                print_status("No Reddit results found", "info")
            time.sleep(1)
        except Exception as e:
            print_status(f"Reddit search error: {e}", "err")

        return mentions

    def search_github(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """Search GitHub repositories for keyword mentions."""
        mentions = []
        if not WEB_SCRAPING_AVAILABLE:
            print_status("GitHub search unavailable (install requests)", "warn")
            return mentions

        try:
            print_status(f"Searching GitHub for '{keyword}'...", "search")
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'OSINT-Monitor/2.0',
            }
            gh_token = os.getenv('GITHUB_TOKEN')
            if gh_token:
                headers['Authorization'] = f'token {gh_token}'

            url = "https://api.github.com/search/repositories"
            params = {'q': keyword, 'per_page': min(max_results, 30), 'sort': 'stars'}

            resp = requests.get(url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for repo in data.get('items', []):
                mention = {
                    'source': 'GitHub',
                    'keyword': keyword,
                    'url': repo.get('html_url', ''),
                    'title': repo.get('full_name', ''),
                    'timestamp': repo.get('updated_at', datetime.now().isoformat()),
                    'content': repo.get('description', '') or '',
                    'relevance_score': self._calculate_relevance(keyword, (repo.get('full_name', '') + ' ' + (repo.get('description', '') or ''))),
                    'engagement': repo.get('stargazers_count', 0) + repo.get('forks_count', 0),
                    'language': repo.get('language', ''),
                }
                mentions.append(mention)
                stars = repo.get('stargazers_count', 0)
                print_status(f"{repo.get('full_name','')} ({stars} stars)", "ok")

            if not mentions:
                print_status("No GitHub results found", "info")
            time.sleep(1)
        except Exception as e:
            print_status(f"GitHub search error: {e}", "err")

        return mentions

    def scrape_websites(self, keyword: str, urls: List[str]) -> List[Dict]:
        """Scrape websites for keyword mentions."""
        mentions = []
        if not WEB_SCRAPING_AVAILABLE:
            print_status("Web scraping unavailable (install requests/beautifulsoup4)", "warn")
            return mentions

        print_status(f"Scraping {len(urls)} website(s) for '{keyword}'...", "search")

        for url in urls:
            try:
                headers = {'User-Agent': 'OSINT-Monitor/2.0 (Educational Purpose)'}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')
                for script in soup(['script', 'style']):
                    script.decompose()

                text = soup.get_text()
                if keyword.lower() in text.lower():
                    lines = text.split('\n')
                    matching_lines = [line.strip() for line in lines if keyword.lower() in line.lower() and line.strip()]

                    mention = {
                        'source': 'Web Scraping',
                        'keyword': keyword,
                        'url': url,
                        'title': soup.title.string if soup.title else url,
                        'timestamp': datetime.now().isoformat(),
                        'content': ' | '.join(matching_lines[:3]),
                        'relevance_score': self._calculate_relevance(keyword, ' '.join(matching_lines[:5])),
                    }
                    mentions.append(mention)
                    print_status(f"Found mention in: {url}", "ok")
                else:
                    print_status(f"No mention in: {url}", "info")

                time.sleep(1)
            except Exception as e:
                print_status(f"Error scraping {url}: {e}", "err")

        return mentions

    # ── Domain / IP reconnaissance ─────────────────────────────────────────

    def dns_lookup(self, domain: str) -> Dict:
        """Perform DNS lookup on a domain."""
        print_status(f"DNS lookup for '{domain}'...", "search")
        result = {
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'records': {},
        }

        # Strip protocol if present
        domain = re.sub(r'^https?://', '', domain).split('/')[0]

        try:
            ips = socket.gethostbyname_ex(domain)
            result['records']['hostname'] = ips[0]
            result['records']['aliases'] = ips[1]
            result['records']['addresses'] = ips[2]
            for ip in ips[2]:
                print_status(f"A record: {ip}", "ok")
            for alias in ips[1]:
                print_status(f"Alias: {alias}", "ok")
        except socket.gaierror as e:
            print_status(f"DNS lookup failed: {e}", "err")

        try:
            rev = socket.gethostbyaddr(result['records'].get('addresses', [''])[0])
            result['records']['reverse_dns'] = rev[0]
            print_status(f"Reverse DNS: {rev[0]}", "ok")
        except Exception:
            pass

        return result

    def ip_info(self, ip_or_domain: str) -> Dict:
        """Get IP geolocation and information."""
        if not WEB_SCRAPING_AVAILABLE:
            print_status("IP info unavailable (install requests)", "warn")
            return {}

        # Resolve domain to IP if needed
        target = re.sub(r'^https?://', '', ip_or_domain).split('/')[0]
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            ip = target

        print_status(f"Looking up IP info for {ip}...", "search")

        try:
            resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get('status') == 'success':
                print_status(f"Country: {data.get('country', 'N/A')}", "ok")
                print_status(f"Region:  {data.get('regionName', 'N/A')}", "ok")
                print_status(f"City:    {data.get('city', 'N/A')}", "ok")
                print_status(f"ISP:     {data.get('isp', 'N/A')}", "ok")
                print_status(f"Org:     {data.get('org', 'N/A')}", "ok")
                print_status(f"AS:      {data.get('as', 'N/A')}", "ok")
            else:
                print_status(f"Lookup failed: {data.get('message', 'unknown error')}", "err")
            return data
        except Exception as e:
            print_status(f"IP info error: {e}", "err")
            return {}

    def check_headers(self, url: str) -> Dict:
        """Inspect HTTP response headers for security analysis."""
        if not WEB_SCRAPING_AVAILABLE:
            print_status("Header check unavailable (install requests)", "warn")
            return {}

        print_status(f"Checking HTTP headers for {url}...", "search")

        if not url.startswith('http'):
            url = f'https://{url}'

        try:
            headers_to_send = {'User-Agent': 'OSINT-Monitor/2.0 (Educational Purpose)'}
            resp = requests.head(url, headers=headers_to_send, timeout=10, allow_redirects=True)

            result = {
                'url': url,
                'status_code': resp.status_code,
                'headers': dict(resp.headers),
                'timestamp': datetime.now().isoformat(),
                'security_headers': {},
            }

            security_headers = [
                'Strict-Transport-Security', 'Content-Security-Policy',
                'X-Content-Type-Options', 'X-Frame-Options',
                'X-XSS-Protection', 'Referrer-Policy',
                'Permissions-Policy', 'Cross-Origin-Opener-Policy',
            ]

            for sh in security_headers:
                value = resp.headers.get(sh)
                if value:
                    result['security_headers'][sh] = value
                    print_status(f"{sh}: {value[:60]}", "ok")
                else:
                    print_status(f"{sh}: MISSING", "warn")

            print_status(f"Server: {resp.headers.get('Server', 'N/A')}", "info")
            return result
        except Exception as e:
            print_status(f"Header check error: {e}", "err")
            return {}

    # ── Aggregation ────────────────────────────────────────────────────────

    def collect_mentions(self, keyword: str, google_results: int = 10,
                         twitter_results: int = 10, reddit_results: int = 10,
                         github_results: int = 10, scrape_urls: Optional[List[str]] = None,
                         sources: Optional[List[str]] = None) -> List[Dict]:
        """
        Collect mentions from selected sources.

        Args:
            keyword: The search term
            google_results: Number of Google results
            twitter_results: Number of Twitter results
            reddit_results: Number of Reddit results
            github_results: Number of GitHub results
            scrape_urls: URLs to scrape
            sources: List of sources to query (default: all)
        """
        if sources is None:
            sources = ['google', 'twitter', 'reddit', 'github']

        all_mentions = []

        print_section(f"Collecting mentions for: '{keyword}'")

        if 'google' in sources:
            m = self.search_google(keyword, google_results)
            all_mentions.extend(m)
            print_status(f"Google: {len(m)} mention(s)", "info")

        if 'twitter' in sources:
            m = self.search_twitter(keyword, twitter_results)
            all_mentions.extend(m)
            print_status(f"Twitter: {len(m)} mention(s)", "info")

        if 'reddit' in sources:
            m = self.search_reddit(keyword, reddit_results)
            all_mentions.extend(m)
            print_status(f"Reddit: {len(m)} mention(s)", "info")

        if 'github' in sources:
            m = self.search_github(keyword, github_results)
            all_mentions.extend(m)
            print_status(f"GitHub: {len(m)} mention(s)", "info")

        if scrape_urls:
            m = self.scrape_websites(keyword, scrape_urls)
            all_mentions.extend(m)
            print_status(f"Web Scraping: {len(m)} mention(s)", "info")

        # Deduplicate
        before = len(all_mentions)
        all_mentions = self._deduplicate(all_mentions)
        dupes = before - len(all_mentions)
        if dupes:
            print_status(f"Removed {dupes} duplicate(s)", "info")

        self.mentions.extend(all_mentions)
        self.search_history.append({
            'keyword': keyword,
            'timestamp': datetime.now().isoformat(),
            'sources': sources,
            'total_results': len(all_mentions),
        })

        print(f"\n  {colored('Total:', Colors.BOLD)} {colored(str(len(all_mentions)), Colors.GREEN)} unique mention(s) collected\n")

        return all_mentions

    # ── Export ─────────────────────────────────────────────────────────────

    def save_to_csv(self, filename: Optional[str] = None):
        """Save collected mentions to a CSV file."""
        if not self.mentions:
            print_status("No mentions to save.", "warn")
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'mentions_{timestamp}.csv'

        try:
            df = pd.DataFrame(self.mentions)
            df.to_csv(filename, index=False)
            print_status(f"CSV saved: {filename} ({len(self.mentions)} records)", "ok")
        except Exception as e:
            print_status(f"Error saving CSV: {e}", "err")

    def save_to_json(self, filename: Optional[str] = None):
        """Save collected mentions to a JSON file."""
        if not self.mentions:
            print_status("No mentions to save.", "warn")
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'mentions_{timestamp}.json'

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'total_mentions': len(self.mentions),
                        'search_history': self.search_history,
                    },
                    'mentions': self.mentions,
                }, f, indent=2, ensure_ascii=False)
            print_status(f"JSON saved: {filename} ({len(self.mentions)} records)", "ok")
        except Exception as e:
            print_status(f"Error saving JSON: {e}", "err")

    # ── Analysis & reports ─────────────────────────────────────────────────

    def summary_report(self) -> Dict:
        """Generate a summary report of all collected mentions."""
        if not self.mentions:
            print_status("No mentions to summarize.", "warn")
            return {}

        print_section("Summary Report")

        sources = Counter(m['source'] for m in self.mentions)
        keywords = Counter(m['keyword'] for m in self.mentions)
        domains = Counter(
            re.sub(r'^https?://(www\.)?', '', m.get('url', '')).split('/')[0]
            for m in self.mentions if m.get('url')
        )

        report = {
            'total_mentions': len(self.mentions),
            'by_source': dict(sources),
            'by_keyword': dict(keywords),
            'top_domains': dict(domains.most_common(10)),
            'searches_performed': len(self.search_history),
        }

        print(f"  {colored('Total mentions:', Colors.BOLD)} {report['total_mentions']}")
        print(f"  {colored('Searches run:',   Colors.BOLD)} {report['searches_performed']}")
        print()

        print(f"  {colored('By source:', Colors.UNDERLINE)}")
        for src, count in sources.most_common():
            bar = colored('|' * min(count, 30), Colors.GREEN)
            print(f"    {src:<15} {count:>4}  {bar}")

        print(f"\n  {colored('By keyword:', Colors.UNDERLINE)}")
        for kw, count in keywords.most_common(5):
            print(f"    {kw:<25} {count:>4}")

        print(f"\n  {colored('Top domains:', Colors.UNDERLINE)}")
        for dom, count in domains.most_common(10):
            print(f"    {dom:<35} {count:>4}")

        # Engagement stats if available
        engaged = [m for m in self.mentions if m.get('engagement')]
        if engaged:
            total_eng = sum(m['engagement'] for m in engaged)
            top = sorted(engaged, key=lambda m: m['engagement'], reverse=True)[:3]
            print(f"\n  {colored('Engagement:', Colors.UNDERLINE)}")
            print(f"    Total engagement score: {total_eng}")
            for m in top:
                print(f"    [{m['source']}] {m['title'][:45]}  (score: {m['engagement']})")

        print()
        return report

    def filter_mentions(self, source: Optional[str] = None, keyword: Optional[str] = None,
                        min_relevance: float = 0.0) -> List[Dict]:
        """Filter stored mentions by source, keyword, or relevance score."""
        results = self.mentions
        if source:
            results = [m for m in results if m['source'].lower() == source.lower()]
        if keyword:
            results = [m for m in results if m.get('keyword', '').lower() == keyword.lower()]
        if min_relevance > 0:
            results = [m for m in results if m.get('relevance_score', 0) >= min_relevance]
        return results

    # ── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _calculate_relevance(keyword: str, text: str) -> float:
        """Calculate a simple relevance score (0-1) for a text against the keyword."""
        if not text:
            return 0.0
        text_lower = text.lower()
        kw_lower = keyword.lower()
        occurrences = text_lower.count(kw_lower)
        words = text_lower.split()
        word_count = max(len(words), 1)
        density = occurrences / word_count
        # Clamp to 0-1
        return round(min(density * 10, 1.0), 2)

    @staticmethod
    def _deduplicate(mentions: List[Dict]) -> List[Dict]:
        """Remove duplicate mentions based on URL."""
        seen = set()
        unique = []
        for m in mentions:
            key = m.get('url', '') or hashlib.md5(json.dumps(m, sort_keys=True).encode()).hexdigest()
            if key not in seen:
                seen.add(key)
                unique.append(m)
        return unique


# ── Interactive menu ───────────────────────────────────────────────────────────

def interactive_menu(monitor: OSINTMonitor):
    """Run the interactive CLI menu."""
    while True:
        print(f"\n{colored('Main Menu', Colors.BOLD + Colors.CYAN)}")
        print(f"{colored('─' * 40, Colors.DIM)}")
        options = [
            ("1", "Search all sources"),
            ("2", "Search specific source"),
            ("3", "Domain / IP reconnaissance"),
            ("4", "HTTP header analysis"),
            ("5", "View summary report"),
            ("6", "Filter & browse results"),
            ("7", "Export results (CSV / JSON)"),
            ("8", "New keyword search"),
            ("0", "Exit"),
        ]
        for key, label in options:
            print(f"  {colored(key, Colors.GREEN)}) {label}")

        choice = input(f"\n  {colored('>', Colors.CYAN)} ").strip()

        if choice == '1':
            kw = input("  Keyword: ").strip()
            if kw:
                monitor.collect_mentions(keyword=kw)

        elif choice == '2':
            kw = input("  Keyword: ").strip()
            if not kw:
                continue
            print("  Available sources: google, twitter, reddit, github")
            src = input("  Source(s) comma-separated: ").strip().lower()
            sources = [s.strip() for s in src.split(',') if s.strip()]
            if sources:
                monitor.collect_mentions(keyword=kw, sources=sources)

        elif choice == '3':
            domain = input("  Domain or IP: ").strip()
            if domain:
                monitor.dns_lookup(domain)
                monitor.ip_info(domain)

        elif choice == '4':
            url = input("  URL: ").strip()
            if url:
                monitor.check_headers(url)

        elif choice == '5':
            monitor.summary_report()

        elif choice == '6':
            if not monitor.mentions:
                print_status("No results yet. Run a search first.", "warn")
                continue
            src = input("  Filter by source (blank=all): ").strip() or None
            results = monitor.filter_mentions(source=src)
            print_section(f"Results ({len(results)})")
            for i, m in enumerate(results[:20], 1):
                print(f"  {colored(str(i), Colors.BOLD)}. [{colored(m['source'], Colors.CYAN)}] {m.get('title', 'N/A')[:55]}")
                print(f"     {colored(m.get('url', ''), Colors.DIM)}")
                if m.get('content'):
                    print(f"     {m['content'][:80]}")
            if len(results) > 20:
                print_status(f"... and {len(results) - 20} more", "info")

        elif choice == '7':
            if not monitor.mentions:
                print_status("No results to export.", "warn")
                continue
            fmt = input("  Format (csv/json/both) [both]: ").strip().lower() or 'both'
            if fmt in ('csv', 'both'):
                monitor.save_to_csv()
            if fmt in ('json', 'both'):
                monitor.save_to_json()

        elif choice == '8':
            kw = input("  Keyword: ").strip()
            if kw:
                urls_input = input("  URLs to scrape (comma-separated, blank=none): ").strip()
                scrape_urls = [u.strip() for u in urls_input.split(',') if u.strip()] if urls_input else None
                monitor.collect_mentions(keyword=kw, scrape_urls=scrape_urls)

        elif choice == '0':
            print_status("Goodbye!", "ok")
            break
        else:
            print_status("Invalid option, try again.", "warn")


# ── Entrypoint ─────────────────────────────────────────────────────────────────

def main():
    """Main function to run the OSINT monitor."""
    print_banner()

    monitor = OSINTMonitor()

    # Direct keyword mode via CLI argument
    if len(sys.argv) > 1:
        keyword = ' '.join(sys.argv[1:])
        mentions = monitor.collect_mentions(keyword=keyword)

        if mentions:
            monitor.summary_report()
            monitor.save_to_csv()
            monitor.save_to_json()

            print_section("Sample results (top 5)")
            for i, m in enumerate(mentions[:5], 1):
                print(f"  {colored(str(i), Colors.BOLD)}. [{colored(m['source'], Colors.CYAN)}] {m.get('title', 'N/A')}")
                print(f"     URL: {m.get('url', '')}")
                if m.get('content'):
                    print(f"     {m['content'][:100]}")
                print()
        else:
            print_status("No mentions found.", "info")
        return

    # Interactive mode
    interactive_menu(monitor)


if __name__ == "__main__":
    main()

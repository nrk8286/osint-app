"""Twitter monitor for tracking mentions on Twitter/X."""

import os
from datetime import datetime
from typing import List, Optional
from osint_app.models import Mention, SearchQuery
from osint_app.monitors.base import BaseMonitor
from osint_app.utils import analyze_sentiment, format_engagement


class TwitterMonitor(BaseMonitor):
    """Monitor for Twitter/X platform."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        super().__init__("Twitter")
        self.api_key = api_key or os.getenv("TWITTER_API_KEY")
        self.api_secret = api_secret or os.getenv("TWITTER_API_SECRET")
        self._client = None
    
    def _init_client(self):
        """Initialize Twitter API client if credentials are available."""
        if self.api_key and self.api_secret:
            try:
                import tweepy
                # Note: This is a placeholder for actual Twitter API integration
                # In production, you would initialize the Tweepy client here
                self._client = None  # Placeholder
            except ImportError:
                self._client = None
    
    def is_available(self) -> bool:
        """Check if Twitter monitor is available."""
        return self.api_key is not None and self.api_secret is not None
    
    def search(self, query: SearchQuery) -> List[Mention]:
        """
        Search for mentions on Twitter.
        
        Args:
            query: SearchQuery object
            
        Returns:
            List of Mention objects
        """
        if not self.is_available():
            return self._get_demo_data(query.keywords, query.max_results)
        
        # Actual Twitter API implementation would go here
        # For now, return demo data
        return self._get_demo_data(query.keywords, query.max_results)
    
    def monitor_keyword(self, keyword: str, max_results: int = 100) -> List[Mention]:
        """
        Monitor a single keyword on Twitter.
        
        Args:
            keyword: Keyword to monitor
            max_results: Maximum number of results
            
        Returns:
            List of Mention objects
        """
        query = SearchQuery(keywords=[keyword], platforms=["Twitter"], max_results=max_results)
        return self.search(query)
    
    def _get_demo_data(self, keywords: List[str], max_results: int) -> List[Mention]:
        """
        Generate demo data for demonstration purposes.
        
        Args:
            keywords: List of keywords
            max_results: Maximum number of results
            
        Returns:
            List of demo Mention objects
        """
        mentions = []
        keyword = keywords[0] if keywords else "example"
        
        # Generate some demo mentions
        demo_tweets = [
            f"Just tried {keyword} and it's amazing! #tech #innovation",
            f"Not impressed with {keyword}. Expected more.",
            f"Looking for alternatives to {keyword}. Any suggestions?",
            f"Great experience with {keyword} today! Highly recommend.",
            f"{keyword} is trending right now! Check it out.",
        ]
        
        for i, tweet in enumerate(demo_tweets[:min(max_results, 5)]):
            mention = Mention(
                platform="Twitter",
                content=tweet,
                author=f"@user{i+1}",
                url=f"https://twitter.com/user{i+1}/status/{1000000+i}",
                timestamp=datetime.now(),
                engagement=format_engagement(
                    likes=10 * (i + 1),
                    shares=5 * (i + 1),
                    comments=2 * (i + 1)
                ),
                sentiment=analyze_sentiment(tweet),
                metadata={'verified': i % 2 == 0, 'followers': 1000 * (i + 1)}
            )
            mentions.append(mention)
        
        return mentions

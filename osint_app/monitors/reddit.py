"""Reddit monitor for tracking mentions on Reddit."""

from datetime import datetime
from typing import List, Optional
from osint_app.models import Mention, SearchQuery
from osint_app.monitors.base import BaseMonitor
from osint_app.utils import analyze_sentiment, format_engagement


class RedditMonitor(BaseMonitor):
    """Monitor for Reddit platform."""
    
    def __init__(self):
        super().__init__("Reddit")
    
    def search(self, query: SearchQuery) -> List[Mention]:
        """
        Search for mentions on Reddit.
        
        Args:
            query: SearchQuery object
            
        Returns:
            List of Mention objects
        """
        return self._get_demo_data(query.keywords, query.max_results)
    
    def monitor_keyword(self, keyword: str, max_results: int = 100) -> List[Mention]:
        """
        Monitor a single keyword on Reddit.
        
        Args:
            keyword: Keyword to monitor
            max_results: Maximum number of results
            
        Returns:
            List of Mention objects
        """
        query = SearchQuery(keywords=[keyword], platforms=["Reddit"], max_results=max_results)
        return self.search(query)
    
    def _get_demo_data(self, keywords: List[str], max_results: int) -> List[Mention]:
        """Generate demo Reddit data."""
        mentions = []
        keyword = keywords[0] if keywords else "example"
        
        demo_posts = [
            f"Discussion: What do you think about {keyword}?",
            f"PSA: {keyword} has some great new features!",
            f"Looking for feedback on {keyword}",
            f"Has anyone else tried {keyword}? Thoughts?",
        ]
        
        for i, post in enumerate(demo_posts[:min(max_results, 4)]):
            mention = Mention(
                platform="Reddit",
                content=post,
                author=f"u/redditor{i+1}",
                url=f"https://reddit.com/r/technology/comments/{100000+i}",
                timestamp=datetime.now(),
                engagement=format_engagement(
                    likes=50 * (i + 1),
                    shares=0,
                    comments=15 * (i + 1)
                ),
                sentiment=analyze_sentiment(post),
                metadata={'subreddit': 'r/technology', 'awards': i}
            )
            mentions.append(mention)
        
        return mentions

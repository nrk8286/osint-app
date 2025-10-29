"""Web scraping monitor for general web mentions."""

from datetime import datetime
from typing import List
from osint_app.models import Mention, SearchQuery
from osint_app.monitors.base import BaseMonitor
from osint_app.utils import analyze_sentiment, format_engagement


class WebMonitor(BaseMonitor):
    """Monitor for general web scraping."""
    
    def __init__(self):
        super().__init__("Web")
    
    def search(self, query: SearchQuery) -> List[Mention]:
        """
        Search for mentions on the web.
        
        Args:
            query: SearchQuery object
            
        Returns:
            List of Mention objects
        """
        return self._get_demo_data(query.keywords, query.max_results)
    
    def monitor_keyword(self, keyword: str, max_results: int = 100) -> List[Mention]:
        """
        Monitor a single keyword on the web.
        
        Args:
            keyword: Keyword to monitor
            max_results: Maximum number of results
            
        Returns:
            List of Mention objects
        """
        query = SearchQuery(keywords=[keyword], platforms=["Web"], max_results=max_results)
        return self.search(query)
    
    def _get_demo_data(self, keywords: List[str], max_results: int) -> List[Mention]:
        """Generate demo web data."""
        mentions = []
        keyword = keywords[0] if keywords else "example"
        
        demo_articles = [
            f"News: {keyword} Launches New Initiative",
            f"Blog Post: My Experience with {keyword}",
            f"Review: Is {keyword} Worth It?",
        ]
        
        for i, article in enumerate(demo_articles[:min(max_results, 3)]):
            mention = Mention(
                platform="Web",
                content=article,
                author=f"Author {i+1}",
                url=f"https://example.com/article-{i+1}",
                timestamp=datetime.now(),
                engagement=format_engagement(
                    likes=30 * (i + 1),
                    shares=10 * (i + 1),
                    comments=8 * (i + 1)
                ),
                sentiment=analyze_sentiment(article),
                metadata={'domain': 'example.com', 'type': 'article'}
            )
            mentions.append(mention)
        
        return mentions

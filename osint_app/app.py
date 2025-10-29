"""Main OSINT App orchestrator."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from osint_app.models import Mention, SearchQuery
from osint_app.monitors import get_monitor
from osint_app.utils import analyze_sentiment


class OSINTApp:
    """Main OSINT application for monitoring social media mentions."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize OSINT App.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.monitors = {}
        self.results = []
    
    def add_monitor(self, platform: str, **kwargs):
        """
        Add a monitor for a specific platform.
        
        Args:
            platform: Platform name
            **kwargs: Additional arguments for monitor
        """
        monitor = get_monitor(platform, **kwargs)
        self.monitors[platform.lower()] = monitor
    
    def search(self, keywords: List[str], platforms: List[str] = None, 
               max_results: int = 100) -> List[Mention]:
        """
        Search for mentions across platforms.
        
        Args:
            keywords: List of keywords to search
            platforms: List of platforms to search (default: all)
            max_results: Maximum results per platform
            
        Returns:
            List of all mentions found
        """
        if platforms is None:
            platforms = list(self.monitors.keys())
        
        all_mentions = []
        
        for platform in platforms:
            platform_key = platform.lower()
            if platform_key not in self.monitors:
                self.add_monitor(platform_key)
            
            monitor = self.monitors[platform_key]
            query = SearchQuery(
                keywords=keywords,
                platforms=[platform],
                max_results=max_results
            )
            
            try:
                mentions = monitor.search(query)
                all_mentions.extend(mentions)
            except Exception as e:
                print(f"Error searching {platform}: {e}")
        
        self.results = all_mentions
        return all_mentions
    
    def monitor_keywords(self, keywords: List[str], platforms: List[str] = None,
                        max_results: int = 100) -> List[Mention]:
        """
        Monitor multiple keywords across platforms.
        
        Args:
            keywords: List of keywords to monitor
            platforms: List of platforms to monitor
            max_results: Maximum results per keyword per platform
            
        Returns:
            List of all mentions found
        """
        return self.search(keywords, platforms, max_results)
    
    def get_sentiment_summary(self, mentions: List[Mention] = None) -> Dict[str, int]:
        """
        Get sentiment summary of mentions.
        
        Args:
            mentions: List of mentions (uses stored results if None)
            
        Returns:
            Dictionary with sentiment counts
        """
        if mentions is None:
            mentions = self.results
        
        summary = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for mention in mentions:
            if mention.sentiment:
                summary[mention.sentiment] = summary.get(mention.sentiment, 0) + 1
        
        return summary
    
    def get_platform_summary(self, mentions: List[Mention] = None) -> Dict[str, int]:
        """
        Get summary of mentions by platform.
        
        Args:
            mentions: List of mentions (uses stored results if None)
            
        Returns:
            Dictionary with platform counts
        """
        if mentions is None:
            mentions = self.results
        
        summary = {}
        
        for mention in mentions:
            platform = mention.platform
            summary[platform] = summary.get(platform, 0) + 1
        
        return summary
    
    def get_engagement_summary(self, mentions: List[Mention] = None) -> Dict[str, int]:
        """
        Get total engagement summary.
        
        Args:
            mentions: List of mentions (uses stored results if None)
            
        Returns:
            Dictionary with total engagement metrics
        """
        if mentions is None:
            mentions = self.results
        
        total_engagement = {'likes': 0, 'shares': 0, 'comments': 0, 'total': 0}
        
        for mention in mentions:
            if mention.engagement:
                total_engagement['likes'] += mention.engagement.get('likes', 0)
                total_engagement['shares'] += mention.engagement.get('shares', 0)
                total_engagement['comments'] += mention.engagement.get('comments', 0)
                total_engagement['total'] += mention.engagement.get('total', 0)
        
        return total_engagement
    
    def filter_by_sentiment(self, sentiment: str, mentions: List[Mention] = None) -> List[Mention]:
        """
        Filter mentions by sentiment.
        
        Args:
            sentiment: Sentiment to filter ('positive', 'negative', 'neutral')
            mentions: List of mentions (uses stored results if None)
            
        Returns:
            Filtered list of mentions
        """
        if mentions is None:
            mentions = self.results
        
        return [m for m in mentions if m.sentiment == sentiment]
    
    def filter_by_platform(self, platform: str, mentions: List[Mention] = None) -> List[Mention]:
        """
        Filter mentions by platform.
        
        Args:
            platform: Platform to filter
            mentions: List of mentions (uses stored results if None)
            
        Returns:
            Filtered list of mentions
        """
        if mentions is None:
            mentions = self.results
        
        return [m for m in mentions if m.platform.lower() == platform.lower()]
    
    def export_results(self, mentions: List[Mention] = None) -> List[Dict[str, Any]]:
        """
        Export results as list of dictionaries.
        
        Args:
            mentions: List of mentions (uses stored results if None)
            
        Returns:
            List of mention dictionaries
        """
        if mentions is None:
            mentions = self.results
        
        return [mention.to_dict() for mention in mentions]

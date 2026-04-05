"""
Base collector for OSINT data collection.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class BaseCollector(ABC):
    """Base class for all data collectors."""
    
    def __init__(self, keywords: List[str]):
        """
        Initialize the collector.
        
        Args:
            keywords: List of keywords to monitor
        """
        self.keywords = keywords
        self.results = []
    
    @abstractmethod
    def collect(self) -> List[Dict[str, Any]]:
        """
        Collect data from the source.
        
        Returns:
            List of collected mentions
        """
        pass
    
    def _create_mention(self, text: str, source: str, url: str = "", 
                       author: str = "", **kwargs) -> Dict[str, Any]:
        """
        Create a standardized mention object.
        
        Args:
            text: The text content of the mention
            source: The source platform (e.g., 'twitter', 'reddit')
            url: URL to the original post
            author: Author of the post
            **kwargs: Additional metadata
            
        Returns:
            Standardized mention dictionary
        """
        return {
            "text": text,
            "source": source,
            "url": url,
            "author": author,
            "timestamp": datetime.now().isoformat(),
            "keywords": self._extract_keywords(text),
            "metadata": kwargs
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract matched keywords from text.
        
        Args:
            text: Text to search for keywords
            
        Returns:
            List of matched keywords
        """
        text_lower = text.lower()
        return [kw for kw in self.keywords if kw.lower() in text_lower]

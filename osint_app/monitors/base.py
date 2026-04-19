"""Base monitor class for all social media monitors."""

from abc import ABC, abstractmethod
from typing import List, Optional
from osint_app.models import Mention, SearchQuery


class BaseMonitor(ABC):
    """Abstract base class for social media monitors."""
    
    def __init__(self, platform_name: str):
        self.platform_name = platform_name
    
    @abstractmethod
    def search(self, query: SearchQuery) -> List[Mention]:
        """
        Search for mentions based on query.
        
        Args:
            query: SearchQuery object
            
        Returns:
            List of Mention objects
        """
        pass
    
    @abstractmethod
    def monitor_keyword(self, keyword: str, max_results: int = 100) -> List[Mention]:
        """
        Monitor a single keyword.
        
        Args:
            keyword: Keyword to monitor
            max_results: Maximum number of results
            
        Returns:
            List of Mention objects
        """
        pass
    
    def is_available(self) -> bool:
        """
        Check if the monitor is available and properly configured.
        
        Returns:
            True if available, False otherwise
        """
        return True

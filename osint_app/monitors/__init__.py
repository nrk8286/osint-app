"""Monitor initialization and factory."""

from osint_app.monitors.base import BaseMonitor
from osint_app.monitors.twitter import TwitterMonitor
from osint_app.monitors.reddit import RedditMonitor
from osint_app.monitors.web import WebMonitor

__all__ = ['BaseMonitor', 'TwitterMonitor', 'RedditMonitor', 'WebMonitor', 'get_monitor']


def get_monitor(platform: str, **kwargs) -> BaseMonitor:
    """
    Factory function to get appropriate monitor for platform.
    
    Args:
        platform: Platform name (Twitter, Reddit, Web)
        **kwargs: Additional arguments for monitor initialization
        
    Returns:
        Monitor instance
        
    Raises:
        ValueError: If platform is not supported
    """
    platform = platform.lower()
    
    if platform == 'twitter':
        return TwitterMonitor(**kwargs)
    elif platform == 'reddit':
        return RedditMonitor()
    elif platform == 'web':
        return WebMonitor()
    else:
        raise ValueError(f"Unsupported platform: {platform}")

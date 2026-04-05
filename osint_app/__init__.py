"""
OSINT Social Media Monitoring Platform
A production-ready OSINT tool for monitoring keyword mentions across multiple platforms.
"""

__version__ = "2.0.0"
__author__ = "OSINT Team"

from osint_app.core.monitor import OSINTMonitor

__all__ = ["OSINTMonitor"]
OSINT App - Social Media Monitoring Tool
A simple OSINT application for monitoring social media mentions.
"""

__version__ = "0.1.0"
__author__ = "OSINT App Team"

from .collectors.base import BaseCollector
from .analyzers.sentiment import SentimentAnalyzer
from .storage.database import Database

__all__ = ["BaseCollector", "SentimentAnalyzer", "Database"]

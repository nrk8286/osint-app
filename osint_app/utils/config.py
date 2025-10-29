"""
Configuration manager for OSINT App.
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """Configuration manager."""
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to environment file
        """
        load_dotenv(env_file)
        
        # Database
        self.database_path = os.getenv("DATABASE_PATH", "./data/osint.db")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Twitter API (optional)
        self.twitter_api_key = os.getenv("TWITTER_API_KEY")
        self.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
        self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET")
        
        # Reddit API (optional)
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert config to dictionary.
        
        Returns:
            Dictionary of configuration values
        """
        return {
            "database_path": self.database_path,
            "log_level": self.log_level,
            "twitter_configured": bool(self.twitter_api_key),
            "reddit_configured": bool(self.reddit_client_id)
        }

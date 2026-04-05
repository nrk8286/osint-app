"""Configuration management using Pydantic Settings."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class TwitterConfig(BaseSettings):
    """Twitter API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="TWITTER_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    bearer_token: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        """Check if Twitter API is properly configured."""
        return bool(self.bearer_token)


class RedditConfig(BaseSettings):
    """Reddit API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDDIT_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    user_agent: str = "OSINT-Monitor/2.0"

    @property
    def is_configured(self) -> bool:
        """Check if Reddit API is properly configured."""
        return bool(self.client_id and self.client_secret)


class NewsAPIConfig(BaseSettings):
    """News API configuration."""

    model_config = SettingsConfigDict(
        env_prefix="NEWS_API_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    key: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        """Check if News API is properly configured."""
        return bool(self.key)


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(
        env_prefix="DB_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    url: str = "sqlite:///osint_data.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class RedisConfig(BaseSettings):
    """Redis cache configuration."""

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    enabled: bool = False


class AppConfig(BaseSettings):
    """Main application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App settings
    app_name: str = "OSINT Monitoring Platform"
    version: str = "2.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4

    # Feature flags
    enable_sentiment_analysis: bool = True
    enable_caching: bool = False
    enable_web_scraping: bool = True

    # Rate limiting
    rate_limit_delay: float = 1.0
    max_retries: int = 3
    request_timeout: int = 30

    # Sub-configurations
    twitter: TwitterConfig = TwitterConfig()
    reddit: RedditConfig = RedditConfig()
    news_api: NewsAPIConfig = NewsAPIConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()


# Global config instance
config = AppConfig()

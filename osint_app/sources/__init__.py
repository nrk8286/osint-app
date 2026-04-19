"""Data source integrations for various platforms."""

from osint_app.sources.google import GoogleSource
from osint_app.sources.twitter import TwitterSource
from osint_app.sources.reddit import RedditSource
from osint_app.sources.news import NewsAPISource
from osint_app.sources.github import GitHubSource

__all__ = ["GoogleSource", "TwitterSource", "RedditSource", "NewsAPISource", "GitHubSource"]

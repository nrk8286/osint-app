"""Pytest configuration and fixtures."""

import pytest
from osint_app.core.monitor import OSINTMonitor
from osint_app.storage.database import DatabaseStorage
from osint_app.models.schemas import Mention, SourceType, SentimentScore
from datetime import datetime


@pytest.fixture
def monitor():
    """Create a test monitor instance."""
    return OSINTMonitor(use_database=False, enable_sentiment=False)


@pytest.fixture
def db():
    """Create a test database instance."""
    return DatabaseStorage(db_url="sqlite:///:memory:")


@pytest.fixture
def sample_mention():
    """Create a sample mention for testing."""
    return Mention(
        source=SourceType.TWITTER,
        keyword="test",
        url="https://twitter.com/test/123",
        title="Test tweet",
        content="This is a test tweet",
        timestamp=datetime.now(),
        author="testuser",
        sentiment=SentimentScore.POSITIVE,
        sentiment_confidence=0.95
    )


@pytest.fixture
def sample_mentions():
    """Create multiple sample mentions."""
    return [
        Mention(
            source=SourceType.TWITTER,
            keyword="test",
            url=f"https://twitter.com/test/{i}",
            title=f"Test tweet {i}",
            content=f"This is test tweet number {i}",
            timestamp=datetime.now()
        )
        for i in range(5)
    ]

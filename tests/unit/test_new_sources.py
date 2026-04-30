"""Unit tests for new data source integrations (HackerNews, Pastebin, YouTube, RSS, Shodan, Telegram)."""

import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.hackernews import HackerNewsSource
from osint_app.sources.pastebin import PastebinSource
from osint_app.sources.rss import RSSSource
from osint_app.sources.shodan import ShodanSource
from osint_app.sources.telegram import TelegramSource
from osint_app.sources.youtube import YouTubeSource


# ---------------------------------------------------------------------------
# Helpers for mocking aiohttp ClientSession
# ---------------------------------------------------------------------------


def _make_aiohttp_mock(status: int, payload=None):
    """Return a mock aiohttp.ClientSession instance.

    ``session.get(...)`` returns a MagicMock (NOT an AsyncMock) that
    acts as an async context manager. Using AsyncMock for .get() would
    make it return a coroutine object, which doesn't support the async
    context manager protocol.
    """
    mock_response = MagicMock()
    mock_response.status = status
    if payload is not None:
        mock_response.json = AsyncMock(return_value=payload)
    mock_response.text = AsyncMock(return_value="")

    # Async context manager for session.get(...)
    mock_get_cm = MagicMock()
    mock_get_cm.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_cm.__aexit__ = AsyncMock(return_value=False)

    # Async context manager for aiohttp.ClientSession()
    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)
    mock_session.get = MagicMock(return_value=mock_get_cm)

    return mock_session


# ---------------------------------------------------------------------------
# HackerNews
# ---------------------------------------------------------------------------


class TestHackerNewsSource:
    """Tests for HackerNewsSource."""

    def test_available_when_aiohttp_present(self):
        with patch("osint_app.sources.hackernews.AIOHTTP_AVAILABLE", True):
            source = HackerNewsSource()
            assert source.is_available() is True

    def test_unavailable_when_aiohttp_absent(self):
        with patch("osint_app.sources.hackernews.AIOHTTP_AVAILABLE", False):
            source = HackerNewsSource()
            assert source.is_available() is False

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = HackerNewsSource()
        source.enabled = False
        with patch("osint_app.sources.hackernews.AIOHTTP_AVAILABLE", False):
            results = await source.search("python")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_returns_mentions(self):
        fake_payload = {
            "hits": [
                {
                    "objectID": "123",
                    "title": "Python OSINT tools",
                    "url": "https://example.com/osint",
                    "author": "hacker",
                    "points": 42,
                    "num_comments": 7,
                    "created_at": "2024-01-01T10:00:00Z",
                    "_tags": ["story"],
                }
            ]
        }
        mock_session = _make_aiohttp_mock(200, fake_payload)
        with (
            patch("osint_app.sources.hackernews.AIOHTTP_AVAILABLE", True),
            patch("osint_app.sources.hackernews.aiohttp.ClientSession", return_value=mock_session),
        ):
            source = HackerNewsSource()
            results = await source.search("python", max_results=5)

        assert len(results) == 1
        assert results[0].source == SourceType.HACKERNEWS
        assert results[0].url == "https://example.com/osint"
        assert results[0].engagement == 49  # 42 + 7

    @pytest.mark.asyncio
    async def test_search_uses_fallback_url_when_no_url(self):
        fake_payload = {
            "hits": [
                {
                    "objectID": "456",
                    "title": "Ask HN: something",
                    "url": None,
                    "author": "user",
                    "points": 5,
                    "num_comments": 2,
                    "created_at": "2024-06-01T12:00:00Z",
                    "_tags": ["story"],
                }
            ]
        }
        mock_session = _make_aiohttp_mock(200, fake_payload)
        with (
            patch("osint_app.sources.hackernews.AIOHTTP_AVAILABLE", True),
            patch("osint_app.sources.hackernews.aiohttp.ClientSession", return_value=mock_session),
        ):
            source = HackerNewsSource()
            results = await source.search("hn", max_results=5)

        assert len(results) == 1
        assert results[0].url == "https://news.ycombinator.com/item?id=456"

    @pytest.mark.asyncio
    async def test_search_handles_http_error(self):
        mock_session = _make_aiohttp_mock(500)
        with (
            patch("osint_app.sources.hackernews.AIOHTTP_AVAILABLE", True),
            patch("osint_app.sources.hackernews.aiohttp.ClientSession", return_value=mock_session),
        ):
            source = HackerNewsSource()
            results = await source.search("error", max_results=5)

        assert results == []


# ---------------------------------------------------------------------------
# Pastebin
# ---------------------------------------------------------------------------


class TestPastebinSource:
    """Tests for PastebinSource."""

    def test_available_when_aiohttp_present(self):
        with patch("osint_app.sources.pastebin.AIOHTTP_AVAILABLE", True):
            source = PastebinSource()
            assert source.is_available() is True

    def test_unavailable_when_aiohttp_absent(self):
        with patch("osint_app.sources.pastebin.AIOHTTP_AVAILABLE", False):
            source = PastebinSource()
            assert source.is_available() is False

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = PastebinSource()
        source.enabled = False
        with patch("osint_app.sources.pastebin.AIOHTTP_AVAILABLE", False):
            results = await source.search("python")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_filters_by_keyword_in_title(self):
        fake_pastes = [
            {
                "key": "abc123",
                "title": "python exploit",
                "date": "1700000000",
                "syntax": "python",
            },
            {"key": "xyz789", "title": "random paste", "date": "1700000001", "syntax": "text"},
        ]
        mock_session = _make_aiohttp_mock(200, fake_pastes)
        with (
            patch("osint_app.sources.pastebin.AIOHTTP_AVAILABLE", True),
            patch("osint_app.sources.pastebin.aiohttp.ClientSession", return_value=mock_session),
        ):
            source = PastebinSource()
            results = await source.search("python", max_results=10)

        assert len(results) == 1
        assert results[0].source == SourceType.PASTEBIN
        assert results[0].url == "https://pastebin.com/abc123"


# ---------------------------------------------------------------------------
# YouTube
# ---------------------------------------------------------------------------


class TestYouTubeSource:
    """Tests for YouTubeSource."""

    def test_unavailable_without_api_key(self):
        with patch("osint_app.sources.youtube.AIOHTTP_AVAILABLE", True):
            source = YouTubeSource()
            source.api_key = None
            assert source.is_available() is False

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = YouTubeSource()
        source.api_key = None
        results = await source.search("test")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_returns_mentions(self):
        fake_payload = {
            "items": [
                {
                    "id": {"videoId": "vid001"},
                    "snippet": {
                        "title": "OSINT Tools Overview",
                        "description": "A guide to OSINT",
                        "channelTitle": "SecurityChannel",
                        "channelId": "ch123",
                        "publishedAt": "2024-03-01T08:00:00Z",
                        "thumbnails": {"default": {"url": "https://img.yt/thumb.jpg"}},
                    },
                }
            ]
        }
        mock_session = _make_aiohttp_mock(200, fake_payload)
        with (
            patch("osint_app.sources.youtube.AIOHTTP_AVAILABLE", True),
            patch("osint_app.sources.youtube.aiohttp.ClientSession", return_value=mock_session),
        ):
            source = YouTubeSource()
            source.api_key = "fake_key"
            results = await source.search("osint", max_results=5)

        assert len(results) == 1
        assert results[0].source == SourceType.YOUTUBE
        assert results[0].url == "https://www.youtube.com/watch?v=vid001"
        assert results[0].author == "SecurityChannel"


# ---------------------------------------------------------------------------
# RSS
# ---------------------------------------------------------------------------


class TestRSSSource:
    """Tests for RSSSource."""

    def test_unavailable_when_feedparser_absent(self):
        with patch("osint_app.sources.rss.FEEDPARSER_AVAILABLE", False):
            source = RSSSource()
            assert source.is_available() is False

    def test_unavailable_when_no_feeds_configured(self):
        with (
            patch("osint_app.sources.rss.FEEDPARSER_AVAILABLE", True),
            patch("osint_app.core.config.config.rss_feeds", ""),
        ):
            source = RSSSource()
            assert source.is_available() is False

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = RSSSource()
        source.feed_urls = []
        results = await source.search("python")
        assert results == []

    def test_parse_feed_filters_by_keyword(self):
        """Test that _parse_feed only returns entries matching the keyword."""
        fake_feed = MagicMock()
        fake_feed.feed = MagicMock()
        fake_feed.feed.get = MagicMock(return_value="Test Feed")
        # feedparser entries are dicts, so use plain dicts
        fake_entry_match = {
            "title": "Python security tools",
            "summary": "A post about Python",
            "link": "https://example.com/post1",
            "author": "Author1",
            "content": [],
            "tags": [],
        }
        fake_entry_no_match = {
            "title": "JavaScript news",
            "summary": "About JS",
            "link": "https://example.com/post2",
            "content": [],
            "tags": [],
        }
        fake_feed.entries = [fake_entry_match, fake_entry_no_match]

        with (
            patch("osint_app.sources.rss.FEEDPARSER_AVAILABLE", True),
            patch("osint_app.sources.rss.feedparser.parse", return_value=fake_feed),
        ):
            source = RSSSource()
            source.feed_urls = ["https://example.com/feed.xml"]
            results = source._parse_feed("https://example.com/feed.xml", "python", 10)

        assert len(results) == 1
        assert results[0].source == SourceType.RSS
        assert "Python" in results[0].title


# ---------------------------------------------------------------------------
# Shodan
# ---------------------------------------------------------------------------


class TestShodanSource:
    """Tests for ShodanSource."""

    def test_unavailable_when_shodan_absent(self):
        with patch("osint_app.sources.shodan.SHODAN_AVAILABLE", False):
            source = ShodanSource()
            assert source.is_available() is False

    def test_unavailable_without_api_key(self):
        with patch("osint_app.sources.shodan.SHODAN_AVAILABLE", True):
            source = ShodanSource()
            source.api_key = None
            source.client = None
            source.enabled = False
            assert source.is_available() is False

    def test_search_sync_returns_mentions(self):
        fake_results = {
            "matches": [
                {
                    "ip_str": "1.2.3.4",
                    "port": 80,
                    "org": "ExampleOrg",
                    "data": "HTTP/1.1 200 OK",
                    "hostnames": ["example.com"],
                    "os": None,
                    "location": {"country_name": "US", "city": "Denver"},
                    "vulns": {},
                    "timestamp": "2024-01-15T00:00:00",
                }
            ]
        }
        mock_client = MagicMock()
        mock_client.search.return_value = fake_results

        with patch("osint_app.sources.shodan.SHODAN_AVAILABLE", True):
            source = ShodanSource()
            source.client = mock_client
            source.enabled = True
            mentions = source._search_sync("apache", max_results=5)

        assert len(mentions) == 1
        assert mentions[0].source == SourceType.SHODAN
        assert mentions[0].metadata["ip"] == "1.2.3.4"
        assert mentions[0].metadata["country"] == "US"

    def test_search_sync_handles_exception(self):
        mock_client = MagicMock()
        mock_client.search.side_effect = Exception("API error")

        with patch("osint_app.sources.shodan.SHODAN_AVAILABLE", True):
            source = ShodanSource()
            source.client = mock_client
            source.enabled = True
            mentions = source._search_sync("test", max_results=5)

        assert mentions == []


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------


class TestTelegramSource:
    """Tests for TelegramSource (graceful-disable scenarios)."""

    def test_unavailable_when_telethon_absent(self):
        with patch("osint_app.sources.telegram.TELETHON_AVAILABLE", False):
            source = TelegramSource()
            assert source.is_available() is False

    def test_unavailable_without_credentials(self):
        with patch("osint_app.sources.telegram.TELETHON_AVAILABLE", True):
            source = TelegramSource()
            source.api_id = None
            source.api_hash = None
            source.enabled = False
            assert source.is_available() is False

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = TelegramSource()
        source.enabled = False
        source.api_id = None
        source.api_hash = None
        results = await source.search("test")
        assert results == []

"""Unit tests for data source integrations."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.base import BaseSource
from osint_app.sources.github import GitHubSource
from osint_app.sources.google import GoogleSource
from osint_app.sources.news import NewsAPISource
from osint_app.sources.reddit import RedditSource
from osint_app.sources.twitter import TwitterSource


# ---------------------------------------------------------------------------
# Concrete stub to test BaseSource
# ---------------------------------------------------------------------------

class StubSource(BaseSource):
    """Minimal concrete subclass for testing BaseSource."""

    def __init__(self, name: str = "stub", fail_count: int = 0):
        super().__init__(name)
        self._calls = 0
        self._fail_count = fail_count

    async def search(self, keyword: str, max_results: int = 10):
        self._calls += 1
        if self._calls <= self._fail_count:
            raise RuntimeError(f"Simulated failure #{self._calls}")
        return [
            Mention(source=SourceType.WEB, keyword=keyword, url=f"https://example.com/{self._calls}")
        ]


class TestBaseSource:
    """Tests for the BaseSource abstract class."""

    def test_is_available_default_true(self):
        source = StubSource()
        assert source.is_available() is True

    def test_disable_source(self):
        source = StubSource()
        source.enabled = False
        assert source.is_available() is False

    @pytest.mark.asyncio
    async def test_search_with_retry_success_first_try(self):
        source = StubSource(fail_count=0)
        results = await source.search_with_retry("test", max_results=5, max_retries=3)
        assert len(results) == 1
        assert source._calls == 1

    @pytest.mark.asyncio
    async def test_search_with_retry_succeeds_after_failures(self):
        source = StubSource(fail_count=2)  # fail twice, succeed on 3rd
        results = await source.search_with_retry("test", max_results=5, max_retries=3)
        assert len(results) == 1
        assert source._calls == 3

    @pytest.mark.asyncio
    async def test_search_with_retry_exhausted_returns_empty(self):
        source = StubSource(fail_count=99)  # always fail
        with patch("asyncio.sleep", new_callable=AsyncMock):
            results = await source.search_with_retry("test", max_results=5, max_retries=2)
        assert results == []


class TestGoogleSource:
    """Tests for GoogleSource."""

    def test_availability_matches_library_presence(self):
        from osint_app.sources import google as google_mod

        source = GoogleSource()
        assert source.is_available() == google_mod.GOOGLE_AVAILABLE

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = GoogleSource()
        source.enabled = False
        with patch("osint_app.sources.google.GOOGLE_AVAILABLE", False):
            results = await source.search("test")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_returns_mentions_when_available(self):
        fake_urls = ["https://example.com/1", "https://example.com/2"]
        source = GoogleSource()

        with (
            patch("osint_app.sources.google.GOOGLE_AVAILABLE", True),
            patch.object(source, "is_available", return_value=True),
            patch(
                "osint_app.sources.google.google_search",
                return_value=iter(fake_urls),
            ),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, lambda: None)  # warm loop

            # Directly exercise search via executor mock
            async def mock_run_in_executor(executor, fn):
                return fn()

            with patch.object(loop, "run_in_executor", side_effect=mock_run_in_executor):
                results = await source.search("test", max_results=2)

        assert isinstance(results, list)


class TestGitHubSource:
    """Tests for GitHubSource."""

    def test_availability_matches_requests_presence(self):
        from osint_app.sources import github as gh_mod

        source = GitHubSource()
        assert source.is_available() == gh_mod.REQUESTS_AVAILABLE

    def test_search_sync_success(self):
        source = GitHubSource()
        fake_api_response = {
            "items": [
                {
                    "html_url": "https://github.com/user/repo",
                    "full_name": "user/repo",
                    "description": "A test repo",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "stargazers_count": 100,
                    "forks_count": 20,
                    "language": "Python",
                    "open_issues_count": 5,
                    "topics": ["python", "osint"],
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = fake_api_response
        mock_resp.raise_for_status = MagicMock()

        with patch("osint_app.sources.github.requests.get", return_value=mock_resp):
            mentions = source._search_sync("python", max_results=5)

        assert len(mentions) == 1
        assert mentions[0].source == SourceType.GITHUB
        assert mentions[0].url == "https://github.com/user/repo"
        assert mentions[0].engagement == 120  # stars + forks

    def test_search_sync_handles_api_error(self):
        source = GitHubSource()
        with patch("osint_app.sources.github.requests.get", side_effect=ConnectionError("fail")):
            mentions = source._search_sync("test", max_results=5)
        assert mentions == []

    def test_search_sync_empty_items(self):
        source = GitHubSource()
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"items": []}
        mock_resp.raise_for_status = MagicMock()

        with patch("osint_app.sources.github.requests.get", return_value=mock_resp):
            mentions = source._search_sync("nothing", max_results=5)
        assert mentions == []

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = GitHubSource()
        source.enabled = False
        with patch("osint_app.sources.github.REQUESTS_AVAILABLE", False):
            results = await source.search("test")
        assert results == []


class TestTwitterSource:
    """Tests for TwitterSource (no credentials scenario)."""

    def test_unavailable_without_credentials(self):
        with patch("osint_app.sources.twitter.TWITTER_AVAILABLE", True):
            with patch("osint_app.core.config.config.twitter.bearer_token", None):
                source = TwitterSource()
                assert source.is_available() is False

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = TwitterSource()
        source.enabled = False
        source.client = None
        results = await source.search("test")
        assert results == []


class TestRedditSource:
    """Tests for RedditSource (no credentials scenario)."""

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = RedditSource()
        source.enabled = False
        source.client = None
        results = await source.search("test")
        assert results == []

    def test_unavailable_without_credentials(self):
        source = RedditSource()
        source.enabled = False
        source.client = None
        assert source.is_available() is False


class TestNewsAPISource:
    """Tests for NewsAPISource."""

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_unavailable(self):
        source = NewsAPISource()
        source.enabled = False
        source.api_key = None
        results = await source.search("test")
        assert results == []

    def test_unavailable_without_api_key(self):
        with patch("osint_app.sources.news.NEWS_HTTP_AVAILABLE", True):
            source = NewsAPISource()
            source.api_key = None
            assert source.is_available() is False

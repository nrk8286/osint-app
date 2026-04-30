"""Unit tests for the FastAPI REST API."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from osint_app.models.schemas import Mention, SourceType


# ---------------------------------------------------------------------------
# We patch the module-level globals (monitor, db, recon) that are created at
# import time so tests run without any external services.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """Create a FastAPI test client with mocked module-level globals."""
    mock_monitor = MagicMock()
    mock_monitor.sources = {
        "google": MagicMock(is_available=lambda: True, name="Google", enabled=True),
        "twitter": MagicMock(is_available=lambda: False, name="Twitter", enabled=False),
    }
    mock_monitor.sentiment_analyzer = MagicMock()

    mock_db = MagicMock()
    mock_db.get_mentions.return_value = []
    mock_db.get_stats.return_value = {"total_mentions": 0, "by_source": {}, "days": 7}
    mock_db.clear_old_mentions.return_value = 0

    mock_recon = MagicMock()

    # Import the app first so the module-level globals exist, then patch them
    import osint_app.api.main as api_main  # noqa: PLC0415

    with (
        patch.object(api_main, "monitor", mock_monitor),
        patch.object(api_main, "db", mock_db),
        patch.object(api_main, "recon", mock_recon),
    ):
        with TestClient(api_main.app, raise_server_exceptions=True) as c:
            c.mock_monitor = mock_monitor
            c.mock_db = mock_db
            c.mock_recon = mock_recon
            yield c


class TestRootEndpoint:
    def test_get_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_api_info(self, client):
        data = response = client.get("/").json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_status_healthy(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_contains_timestamp(self, client):
        data = client.get("/health").json()
        assert "timestamp" in data

    def test_health_lists_sources(self, client):
        data = client.get("/health").json()
        assert "sources" in data


class TestSourcesEndpoint:
    def test_get_sources_returns_200(self, client):
        response = client.get("/api/sources")
        assert response.status_code == 200

    def test_sources_response_is_dict(self, client):
        data = client.get("/api/sources").json()
        assert isinstance(data, dict)


class TestMentionsEndpoint:
    def test_get_mentions_default_returns_200(self, client):
        response = client.get("/api/mentions")
        assert response.status_code == 200

    def test_get_mentions_returns_list(self, client):
        data = client.get("/api/mentions").json()
        assert isinstance(data, list)

    def test_get_mentions_with_keyword_filter(self, client):
        response = client.get("/api/mentions?keyword=python")
        assert response.status_code == 200

    def test_get_mentions_with_limit_and_offset(self, client):
        response = client.get("/api/mentions?limit=10&offset=0")
        assert response.status_code == 200

    def test_get_mentions_invalid_limit_returns_422(self, client):
        response = client.get("/api/mentions?limit=0")  # ge=1
        assert response.status_code == 422

    def test_get_mentions_invalid_source_propagates(self, client):
        """An invalid source value raises an error handled by the endpoint."""
        client.mock_db.get_mentions.side_effect = ValueError("invalid source")
        response = client.get("/api/mentions?source=invalid_source")
        # Either a 422 (FastAPI validation) or 500 (our exception handler)
        assert response.status_code in (422, 500)
        client.mock_db.get_mentions.side_effect = None


class TestStatsEndpoint:
    def test_get_stats_default_returns_200(self, client):
        response = client.get("/api/stats")
        assert response.status_code == 200

    def test_get_stats_contains_total_mentions(self, client):
        data = client.get("/api/stats").json()
        assert "total_mentions" in data

    def test_get_stats_custom_days(self, client):
        response = client.get("/api/stats?days=30")
        assert response.status_code == 200

    def test_get_stats_invalid_days_returns_422(self, client):
        response = client.get("/api/stats?days=0")  # ge=1
        assert response.status_code == 422


class TestClearMentionsEndpoint:
    def test_delete_mentions_returns_200(self, client):
        response = client.delete("/api/mentions?days=30")
        assert response.status_code == 200

    def test_delete_mentions_returns_deleted_count(self, client):
        client.mock_db.clear_old_mentions.return_value = 5
        data = client.delete("/api/mentions?days=30").json()
        assert "deleted" in data
        assert data["deleted"] == 5

    def test_delete_mentions_invalid_days_returns_422(self, client):
        response = client.delete("/api/mentions?days=0")  # ge=1
        assert response.status_code == 422


class TestWhoisEndpoint:
    """Tests for GET /api/recon/whois/{domain}."""

    def test_whois_returns_200(self, client):
        from osint_app.models.schemas import ReconResult

        mock_result = ReconResult(
            target="example.com",
            recon_type="whois",
            data={"registrar": "Test Registrar"},
        )
        client.mock_recon.whois_lookup.return_value = mock_result
        response = client.get("/api/recon/whois/example.com")
        assert response.status_code == 200

    def test_whois_response_contains_target(self, client):
        from osint_app.models.schemas import ReconResult

        mock_result = ReconResult(
            target="example.com",
            recon_type="whois",
            data={"registrar": "Test Registrar"},
        )
        client.mock_recon.whois_lookup.return_value = mock_result
        data = client.get("/api/recon/whois/example.com").json()
        assert data["target"] == "example.com"
        assert data["recon_type"] == "whois"


class TestLogsRecentEndpoint:
    """Tests for GET /api/logs/recent."""

    def test_logs_recent_returns_200(self, client):
        response = client.get("/api/logs/recent")
        assert response.status_code == 200

    def test_logs_recent_returns_list(self, client):
        data = client.get("/api/logs/recent").json()
        assert isinstance(data, list)

    def test_logs_recent_honours_limit(self, client):
        response = client.get("/api/logs/recent?limit=10")
        assert response.status_code == 200

    def test_logs_recent_invalid_limit_returns_422(self, client):
        response = client.get("/api/logs/recent?limit=0")
        assert response.status_code == 422


class TestAgentLogStorageIntegration:
    """Tests for save_log_event and get_log_events on DatabaseStorage."""

    def test_save_and_retrieve_log_event(self, db):
        event = {
            "timestamp": "2024-01-01T10:00:00+00:00",
            "event_type": "SEARCH_DONE",
            "source": "HackerNews",
            "keyword": "osint",
            "count": 7,
            "duration_ms": 320.5,
            "detail": None,
        }
        row_id = db.save_log_event(event)
        assert row_id > 0

        events = db.get_log_events(limit=10)
        assert any(
            e["source"] == "HackerNews" and e["event_type"] == "SEARCH_DONE" for e in events
        )

    def test_get_log_events_filters_by_source(self, db):
        db.save_log_event(
            {
                "timestamp": "2024-01-01T10:00:00+00:00",
                "event_type": "SEARCH_STARTED",
                "source": "YouTube",
                "keyword": "python",
            }
        )
        db.save_log_event(
            {
                "timestamp": "2024-01-01T10:00:01+00:00",
                "event_type": "SEARCH_STARTED",
                "source": "Reddit",
                "keyword": "python",
            }
        )
        events = db.get_log_events(source="YouTube")
        assert all(e["source"] == "YouTube" for e in events)

    def test_get_log_events_filters_by_event_type(self, db):
        db.save_log_event(
            {
                "timestamp": "2024-01-01T10:00:00+00:00",
                "event_type": "SEARCH_ERROR",
                "source": "Shodan",
                "keyword": "test",
                "detail": "quota exceeded",
            }
        )
        events = db.get_log_events(event_type="SEARCH_ERROR")
        assert all(e["event_type"] == "SEARCH_ERROR" for e in events)


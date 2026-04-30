"""Unit tests for network reconnaissance module."""

import socket
from unittest.mock import MagicMock, patch

import pytest

from osint_app.recon.network import NetworkRecon


class TestDnsLookup:
    """Tests for NetworkRecon.dns_lookup."""

    def test_strips_http_prefix(self):
        with patch("socket.gethostbyname_ex") as mock_dns:
            mock_dns.return_value = ("example.com", [], ["93.184.216.34"])
            with patch("socket.gethostbyaddr", return_value=("example.com", [], ["93.184.216.34"])):
                result = NetworkRecon.dns_lookup("http://example.com/path")
        assert result.target == "example.com"
        assert result.recon_type == "dns"

    def test_strips_https_prefix(self):
        with patch("socket.gethostbyname_ex") as mock_dns:
            mock_dns.return_value = ("example.com", [], ["93.184.216.34"])
            with patch("socket.gethostbyaddr", return_value=("example.com", [], ["93.184.216.34"])):
                result = NetworkRecon.dns_lookup("https://example.com/path?q=1")
        assert result.target == "example.com"

    def test_successful_lookup_returns_addresses(self):
        with patch("socket.gethostbyname_ex") as mock_dns:
            mock_dns.return_value = ("example.com", ["alias.example.com"], ["1.2.3.4"])
            with patch("socket.gethostbyaddr", return_value=("ptr.example.com", [], [])):
                result = NetworkRecon.dns_lookup("example.com")
        assert result.data["hostname"] == "example.com"
        assert "1.2.3.4" in result.data["addresses"]
        assert result.data["reverse_dns"] == "ptr.example.com"

    def test_dns_error_stored_in_data(self):
        with patch("socket.gethostbyname_ex", side_effect=socket.gaierror("No such host")):
            result = NetworkRecon.dns_lookup("nonexistent.invalid")
        assert "error" in result.data

    def test_reverse_dns_failure_is_ignored(self):
        """Reverse DNS failure must not crash the method."""
        with patch("socket.gethostbyname_ex") as mock_dns:
            mock_dns.return_value = ("example.com", [], ["1.2.3.4"])
            with patch("socket.gethostbyaddr", side_effect=socket.herror("fail")):
                result = NetworkRecon.dns_lookup("example.com")
        assert result.data["addresses"] == ["1.2.3.4"]
        assert "reverse_dns" not in result.data


class TestIpInfo:
    """Tests for NetworkRecon.ip_info."""

    def test_returns_error_when_requests_unavailable(self):
        with patch("osint_app.recon.network.REQUESTS_AVAILABLE", False):
            result = NetworkRecon.ip_info("1.2.3.4")
        assert "error" in result.data

    def test_successful_ip_lookup(self):
        fake_geo = {"country": "US", "city": "New York", "isp": "ExampleISP"}
        mock_resp = MagicMock()
        mock_resp.json.return_value = fake_geo
        mock_resp.raise_for_status = MagicMock()

        with (
            patch("osint_app.recon.network.REQUESTS_AVAILABLE", True),
            patch("socket.gethostbyname", return_value="1.2.3.4"),
            patch("osint_app.recon.network.requests.get", return_value=mock_resp),
        ):
            result = NetworkRecon.ip_info("1.2.3.4")
        assert result.recon_type == "ip_info"
        assert result.data["country"] == "US"

    def test_http_error_captured_in_data(self):
        with (
            patch("osint_app.recon.network.REQUESTS_AVAILABLE", True),
            patch("socket.gethostbyname", return_value="1.2.3.4"),
            patch(
                "osint_app.recon.network.requests.get",
                side_effect=ConnectionError("timeout"),
            ),
        ):
            result = NetworkRecon.ip_info("1.2.3.4")
        assert "error" in result.data

    def test_unresolvable_hostname_falls_back_to_raw(self):
        """If DNS resolution fails, the original string is used as IP."""
        with (
            patch("osint_app.recon.network.REQUESTS_AVAILABLE", True),
            patch("socket.gethostbyname", side_effect=socket.gaierror("fail")),
            patch("osint_app.recon.network.requests.get", side_effect=ConnectionError("fail")),
        ):
            result = NetworkRecon.ip_info("not-a-host.invalid")
        assert "error" in result.data


class TestCheckHeaders:
    """Tests for NetworkRecon.check_headers."""

    def test_returns_error_when_requests_unavailable(self):
        with patch("osint_app.recon.network.REQUESTS_AVAILABLE", False):
            result = NetworkRecon.check_headers("https://example.com")
        assert "error" in result.data

    def test_prepends_https_when_scheme_missing(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {
            "Server": "nginx",
            "Strict-Transport-Security": "max-age=31536000",
        }

        with (
            patch("osint_app.recon.network.REQUESTS_AVAILABLE", True),
            patch("osint_app.recon.network.requests.head", return_value=mock_resp) as mock_head,
        ):
            result = NetworkRecon.check_headers("example.com")

        called_url = mock_head.call_args[0][0]
        assert called_url.startswith("https://")

    def test_successful_header_check(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {
            "Server": "Apache",
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
        }

        with (
            patch("osint_app.recon.network.REQUESTS_AVAILABLE", True),
            patch("osint_app.recon.network.requests.head", return_value=mock_resp),
        ):
            result = NetworkRecon.check_headers("https://example.com")

        assert result.recon_type == "headers"
        assert result.data["status_code"] == 200
        assert "security_headers" in result.data
        assert "missing_security_headers" in result.data

    def test_missing_security_headers_listed(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"Server": "nginx"}  # no security headers

        with (
            patch("osint_app.recon.network.REQUESTS_AVAILABLE", True),
            patch("osint_app.recon.network.requests.head", return_value=mock_resp),
        ):
            result = NetworkRecon.check_headers("https://example.com")

        missing = result.data["missing_security_headers"]
        assert "Strict-Transport-Security" in missing
        assert "Content-Security-Policy" in missing

    def test_connection_error_captured_in_data(self):
        with (
            patch("osint_app.recon.network.REQUESTS_AVAILABLE", True),
            patch(
                "osint_app.recon.network.requests.head",
                side_effect=ConnectionError("refused"),
            ),
        ):
            result = NetworkRecon.check_headers("https://down.example.com")
        assert "error" in result.data

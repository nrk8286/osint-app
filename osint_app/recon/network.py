"""Network reconnaissance: DNS lookup, IP geolocation, HTTP header analysis, WHOIS."""

import re
import socket
from datetime import datetime
from typing import Dict, Optional

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import whois as whois_lib

    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

from osint_app.models.schemas import ReconResult


class NetworkRecon:
    """Domain and IP reconnaissance toolkit."""

    # ── DNS ─────────────────────────────────────────────────────────────

    @staticmethod
    def dns_lookup(domain: str) -> ReconResult:
        """Resolve DNS records for *domain*.

        Returns A records, aliases, and reverse-DNS when available.
        """
        domain = re.sub(r"^https?://", "", domain).split("/")[0]
        records: Dict = {}

        try:
            hostname, aliases, addresses = socket.gethostbyname_ex(domain)
            records["hostname"] = hostname
            records["aliases"] = aliases
            records["addresses"] = addresses
        except socket.gaierror as exc:
            records["error"] = str(exc)

        # Reverse DNS for first address
        if records.get("addresses"):
            try:
                rev = socket.gethostbyaddr(records["addresses"][0])
                records["reverse_dns"] = rev[0]
            except Exception:
                pass

        return ReconResult(target=domain, recon_type="dns", data=records)

    # ── IP geolocation ──────────────────────────────────────────────────

    @staticmethod
    def ip_info(ip_or_domain: str) -> ReconResult:
        """Return geolocation and ISP data for an IP or domain."""
        if not REQUESTS_AVAILABLE:
            return ReconResult(
                target=ip_or_domain,
                recon_type="ip_info",
                data={"error": "requests library not installed"},
            )

        target = re.sub(r"^https?://", "", ip_or_domain).split("/")[0]
        try:
            ip = socket.gethostbyname(target)
        except socket.gaierror:
            ip = target

        try:
            resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            data = {"error": str(exc)}

        return ReconResult(target=ip, recon_type="ip_info", data=data)

    # ── HTTP headers ────────────────────────────────────────────────────

    SECURITY_HEADERS = [
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Referrer-Policy",
        "Permissions-Policy",
        "Cross-Origin-Opener-Policy",
    ]

    @staticmethod
    def check_headers(url: str) -> ReconResult:
        """Inspect HTTP response headers, highlighting security headers."""
        if not REQUESTS_AVAILABLE:
            return ReconResult(
                target=url,
                recon_type="headers",
                data={"error": "requests library not installed"},
            )

        if not url.startswith("http"):
            url = f"https://{url}"

        try:
            resp = requests.head(
                url,
                headers={"User-Agent": "OSINT-Monitor/2.0 (Educational Purpose)"},
                timeout=10,
                allow_redirects=True,
            )

            security: Dict[str, Optional[str]] = {}
            for hdr in NetworkRecon.SECURITY_HEADERS:
                security[hdr] = resp.headers.get(hdr)

            data = {
                "status_code": resp.status_code,
                "server": resp.headers.get("Server"),
                "all_headers": dict(resp.headers),
                "security_headers": security,
                "missing_security_headers": [h for h, v in security.items() if v is None],
            }
        except Exception as exc:
            data = {"error": str(exc)}

        return ReconResult(target=url, recon_type="headers", data=data)

    # ── WHOIS ────────────────────────────────────────────────────────────

    @staticmethod
    def whois_lookup(domain: str) -> ReconResult:
        """Perform a WHOIS lookup for *domain*.

        Returns registration details such as registrar, creation/expiry dates,
        name servers, and registrant info when available.

        Args:
            domain: Domain name to query (http/https prefix is stripped)

        Returns:
            ReconResult with recon_type ``"whois"``
        """
        if not WHOIS_AVAILABLE:
            return ReconResult(
                target=domain,
                recon_type="whois",
                data={"error": "python-whois library not installed"},
            )

        domain = re.sub(r"^https?://", "", domain).split("/")[0]

        try:
            w = whois_lib.whois(domain)
            # Convert datetime objects to ISO strings for JSON serialisation
            data: Dict = {}
            for key, val in w.items():
                if val is None:
                    continue
                if isinstance(val, list):
                    data[key] = [
                        v.isoformat() if hasattr(v, "isoformat") else str(v) for v in val
                    ]
                elif hasattr(val, "isoformat"):
                    data[key] = val.isoformat()
                else:
                    data[key] = str(val)
        except Exception as exc:
            data = {"error": str(exc)}

        return ReconResult(target=domain, recon_type="whois", data=data)

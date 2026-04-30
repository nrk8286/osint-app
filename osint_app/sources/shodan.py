"""Shodan IoT search engine source integration."""

import asyncio
from datetime import datetime, timezone
from typing import List

try:
    import shodan as shodan_lib

    SHODAN_AVAILABLE = True
except ImportError:
    SHODAN_AVAILABLE = False

from osint_app.core.config import config
from osint_app.models.schemas import Mention, SourceType
from osint_app.sources.base import BaseSource


class ShodanSource(BaseSource):
    """Shodan internet-of-things search integration."""

    def __init__(self):
        """Initialize Shodan source."""
        super().__init__("Shodan")
        self.api_key = config.shodan.api_key
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initialize Shodan API client."""
        if not SHODAN_AVAILABLE or not self.api_key:
            self.enabled = False
            return
        try:
            self.client = shodan_lib.Shodan(self.api_key)
            self.enabled = True
        except Exception as e:
            print(f"Error initializing Shodan client: {e}")
            self.enabled = False

    def is_available(self) -> bool:
        """Check if Shodan source is available and configured."""
        return SHODAN_AVAILABLE and bool(self.client) and self.enabled

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search Shodan for hosts matching the keyword.

        Args:
            keyword: Search term / Shodan filter query
            max_results: Maximum number of results

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._search_sync, keyword, max_results)

    def _search_sync(self, keyword: str, max_results: int) -> List[Mention]:
        """Synchronous Shodan search implementation."""
        mentions: List[Mention] = []
        try:
            results = self.client.search(keyword, page=1)
            for match in results.get("matches", [])[:max_results]:
                ip_str = match.get("ip_str", "")
                port = match.get("port", "")
                url = f"https://www.shodan.io/host/{ip_str}"
                hostnames = match.get("hostnames", [])
                org = match.get("org") or match.get("isp") or ""
                banner = (match.get("data") or "")[:500]

                ts_raw = match.get("timestamp")
                try:
                    ts = (
                        datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                        if ts_raw
                        else datetime.now(timezone.utc)
                    )
                except (ValueError, AttributeError):
                    ts = datetime.now(timezone.utc)

                mention = Mention(
                    source=SourceType.SHODAN,
                    keyword=keyword,
                    url=url,
                    title=f"{ip_str}:{port} — {org}",
                    content=banner,
                    timestamp=ts,
                    metadata={
                        "ip": ip_str,
                        "port": port,
                        "org": org,
                        "hostnames": hostnames,
                        "os": match.get("os"),
                        "country": match.get("location", {}).get("country_name"),
                        "city": match.get("location", {}).get("city"),
                        "vulns": list(match.get("vulns", {}).keys()),
                    },
                )
                mentions.append(mention)
        except Exception as e:
            print(f"Error searching Shodan: {e}")
        return mentions

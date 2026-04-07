"""GitHub repository search source integration."""

import asyncio
import os
from datetime import datetime
from typing import List

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from osint_app.sources.base import BaseSource
from osint_app.models.schemas import Mention, SourceType


class GitHubSource(BaseSource):
    """GitHub repository search integration."""

    def __init__(self):
        """Initialize GitHub source."""
        super().__init__("GitHub")
        self.token = os.getenv("GITHUB_TOKEN")
        self.enabled = REQUESTS_AVAILABLE

    def is_available(self) -> bool:
        """Check if GitHub search is available."""
        return REQUESTS_AVAILABLE

    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search GitHub repositories for keyword.

        Args:
            keyword: Search term
            max_results: Maximum results (capped at 30)

        Returns:
            List of mentions
        """
        if not self.is_available():
            return []

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._search_sync, keyword, max_results)

    def _search_sync(self, keyword: str, max_results: int) -> List[Mention]:
        """Synchronous GitHub search implementation."""
        mentions = []

        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "OSINT-Monitor/2.0",
            }
            if self.token:
                headers["Authorization"] = f"token {self.token}"

            resp = requests.get(
                "https://api.github.com/search/repositories",
                headers=headers,
                params={"q": keyword, "per_page": min(max_results, 30), "sort": "stars"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            for repo in data.get("items", []):
                mention = Mention(
                    source=SourceType.GITHUB,
                    keyword=keyword,
                    url=repo.get("html_url", ""),
                    title=repo.get("full_name", ""),
                    content=repo.get("description", "") or "",
                    timestamp=datetime.fromisoformat(
                        repo.get("updated_at", datetime.now().isoformat()).replace("Z", "+00:00")
                    ),
                    metadata={
                        "stars": repo.get("stargazers_count", 0),
                        "forks": repo.get("forks_count", 0),
                        "language": repo.get("language"),
                        "open_issues": repo.get("open_issues_count", 0),
                        "topics": repo.get("topics", []),
                    },
                    engagement=repo.get("stargazers_count", 0) + repo.get("forks_count", 0),
                )
                mentions.append(mention)

        except Exception as e:
            print(f"Error searching GitHub: {e}")

        return mentions

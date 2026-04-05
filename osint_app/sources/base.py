"""Base class for data source integrations."""

from abc import ABC, abstractmethod
from typing import List
import asyncio

from osint_app.models.schemas import Mention


class BaseSource(ABC):
    """Abstract base class for data sources."""

    def __init__(self, name: str):
        """Initialize base source.

        Args:
            name: Name of the data source
        """
        self.name = name
        self.enabled = True

    @abstractmethod
    async def search(self, keyword: str, max_results: int = 10) -> List[Mention]:
        """Search for keyword mentions.

        Args:
            keyword: Search term
            max_results: Maximum number of results to return

        Returns:
            List of mentions found
        """
        pass

    def is_available(self) -> bool:
        """Check if source is available and configured.

        Returns:
            True if source can be used
        """
        return self.enabled

    async def search_with_retry(
        self, keyword: str, max_results: int = 10, max_retries: int = 3
    ) -> List[Mention]:
        """Search with retry logic.

        Args:
            keyword: Search term
            max_results: Maximum results
            max_retries: Maximum retry attempts

        Returns:
            List of mentions
        """
        for attempt in range(max_retries):
            try:
                return await self.search(keyword, max_results)
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Error in {self.name} after {max_retries} attempts: {e}")
                    return []
                await asyncio.sleep(2**attempt)  # Exponential backoff
        return []

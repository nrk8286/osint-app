"""Compatibility models for the original demo CLI and its synthetic monitors.

These deliberately remain separate from the v2 collector schemas, whose source,
keyword, and engagement fields have different meanings.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Mention:
    platform: str
    content: str
    author: str
    url: str
    timestamp: datetime
    engagement: Dict[str, int] = field(default_factory=dict)
    sentiment: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


@dataclass
class SearchQuery:
    keywords: List[str]
    platforms: List[str] = field(default_factory=list)
    max_results: int = 100

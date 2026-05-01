"""Provider base types — shared dataclasses + helpers."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)


class ProviderUnavailable(RuntimeError):
    """Raised by a provider when its env vars or network call are unusable."""


@dataclass
class ProviderResult:
    provider: str
    status: str  # ok | no_key | http_error | timeout | empty | unsupported
    data: Any = None
    error: str | None = None
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status,
            "data": self.data,
            "error": self.error,
            "fetched_at": self.fetched_at,
        }


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

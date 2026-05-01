"""
Quota Guard — protects paid APIs from runaway spend.

Tracks daily call counts in-memory + DB-persistable. Each provider has a
per-day cap; calls beyond cap are blocked with a clear error so the chain
can fall through to a free provider or fail safely.

Usage:
    if quota_guard.consume('google_maps_places', cost=1):
        result = await places_api.search(...)
    else:
        # use static fallback or free provider

Limits read from env (override the defaults for prod):
    DEALIX_QUOTA_GOOGLE_SEARCH_DAILY=100   (free tier)
    DEALIX_QUOTA_GOOGLE_MAPS_DAILY=200
    DEALIX_QUOTA_GROQ_DAILY=2000
    DEALIX_QUOTA_FIRECRAWL_DAILY=200
    DEALIX_QUOTA_TAVILY_DAILY=200
    DEALIX_QUOTA_HUNTER_DAILY=50
"""

from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)

DEFAULT_LIMITS = {
    "google_search": 100,
    "google_maps_places": 200,
    "groq": 2000,
    "firecrawl": 200,
    "tavily": 200,
    "hunter": 50,
    "abstract_email": 100,
    "wappalyzer": 50,
    "gmail_send": 50,
    "gmail_drafts": 50,
}


def _env_limit(provider: str) -> int:
    key = f"DEALIX_QUOTA_{provider.upper()}_DAILY"
    try:
        return int(os.getenv(key, str(DEFAULT_LIMITS.get(provider, 100))))
    except ValueError:
        return DEFAULT_LIMITS.get(provider, 100)


class QuotaGuard:
    """Thread-safe in-process daily quota tracker."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._counters: dict[str, int] = {}
        self._date_iso = datetime.now(timezone.utc).date().isoformat()

    def _maybe_reset(self) -> None:
        today = datetime.now(timezone.utc).date().isoformat()
        if today != self._date_iso:
            self._counters.clear()
            self._date_iso = today

    def consume(self, provider: str, *, cost: int = 1) -> bool:
        """Try to spend `cost` units. Returns True if allowed, False if cap hit."""
        with self._lock:
            self._maybe_reset()
            limit = _env_limit(provider)
            current = self._counters.get(provider, 0)
            if current + cost > limit:
                log.info("quota_blocked provider=%s used=%d limit=%d", provider, current, limit)
                return False
            self._counters[provider] = current + cost
            return True

    def remaining(self, provider: str) -> int:
        with self._lock:
            self._maybe_reset()
            return max(0, _env_limit(provider) - self._counters.get(provider, 0))

    def status(self) -> dict[str, Any]:
        with self._lock:
            self._maybe_reset()
            return {
                "date_utc": self._date_iso,
                "providers": {
                    p: {
                        "used": self._counters.get(p, 0),
                        "limit": _env_limit(p),
                        "remaining": _env_limit(p) - self._counters.get(p, 0),
                    }
                    for p in DEFAULT_LIMITS
                },
            }


# Global singleton — one process = one guard
guard = QuotaGuard()

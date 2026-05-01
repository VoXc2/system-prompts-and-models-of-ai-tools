"""
Idempotency store — prevents duplicate processing of webhooks / actions.

Usage:
    store = IdempotencyStore()
    if await store.seen(key="hubspot:evt:12345"):
        return {"status": "duplicate"}
    # ... process ...
    await store.mark(key="hubspot:evt:12345", ttl_seconds=3600*24)
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Any

log = logging.getLogger(__name__)


class IdempotencyStore:
    """Redis-backed idempotency set with TTL."""

    def __init__(self, prefix: str = "idem:", redis_client: Any | None = None):
        self.prefix = prefix
        self._redis = redis_client or self._default_client()

    def _default_client(self) -> Any | None:
        try:
            import redis  # type: ignore

            url = os.getenv("REDIS_URL")
            if not url:
                return None
            return redis.from_url(url, socket_timeout=3, decode_responses=True)
        except Exception:  # pragma: no cover
            return None

    @staticmethod
    def hash_payload(payload: Any) -> str:
        """Stable hash of arbitrary payload — useful for body-based idempotency."""
        if isinstance(payload, dict):
            import json

            data = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
        elif isinstance(payload, bytes):
            data = payload
        else:
            data = str(payload).encode()
        return hashlib.sha256(data).hexdigest()[:32]

    def _key(self, key: str) -> str:
        return f"{self.prefix}{key}"

    def seen(self, key: str) -> bool:
        if not self._redis:
            return False
        try:
            return bool(self._redis.exists(self._key(key)))
        except Exception:  # pragma: no cover
            return False

    def mark(self, key: str, ttl_seconds: int = 86400) -> bool:
        """Mark key as processed. Returns True if newly marked, False if already existed."""
        if not self._redis:
            return True
        try:
            # SET NX EX — atomic check-and-set
            result = self._redis.set(self._key(key), "1", nx=True, ex=ttl_seconds)
            return bool(result)
        except Exception as exc:  # pragma: no cover
            key_fp = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
            log.warning("idem_mark_failed key_fp=%s err_type=%s", key_fp, type(exc).__name__)
            return True

    def claim(self, key: str, ttl_seconds: int = 86400) -> bool:
        """Atomic: returns True if caller owns this key (first to claim).
        False means duplicate — skip processing."""
        return self.mark(key, ttl_seconds=ttl_seconds)

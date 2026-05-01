"""
Redis-backed Dead Letter Queue.
Any webhook / outbound / enrichment call that fails after max_retries lands here.

Storage model (Redis):
  dlq:<queue_name>              — Redis list of JSON items (LPUSH new, RPOP consume)
  dlq:<queue_name>:meta         — Hash of depth, last_error, last_at
  dlq:<queue_name>:retry_count  — Hash of item_id → attempts
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class DLQItem:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    queue: str = ""
    source: str = ""  # e.g. "hubspot.webhook", "calendly.webhook", "outbound.send"
    payload: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    attempts: int = 0
    first_seen_at: float = field(default_factory=time.time)
    last_attempt_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, s: str) -> DLQItem:
        return cls(**json.loads(s))


class DLQ:
    """Minimal DLQ backed by Redis."""

    def __init__(self, queue: str, redis_client: Any | None = None):
        self.queue = queue
        self._key = f"dlq:{queue}"
        self._meta_key = f"dlq:{queue}:meta"
        self._redis = redis_client or self._default_client()

    def _default_client(self) -> Any | None:
        try:
            import redis  # type: ignore

            url = os.getenv("REDIS_URL")
            if not url:
                log.warning("dlq_no_redis_url")
                return None
            return redis.from_url(url, socket_timeout=3, decode_responses=True)
        except Exception as e:
            log.warning("dlq_redis_unavailable %s", e)
            return None

    def push(
        self,
        source: str,
        payload: dict[str, Any],
        error: str,
        attempts: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> str | None:
        """Add a failed item to the DLQ. Returns item id or None on redis failure."""
        if not self._redis:
            return None
        item = DLQItem(
            queue=self.queue,
            source=source,
            payload=payload,
            error=error[:500],
            attempts=attempts,
            metadata=metadata or {},
        )
        try:
            self._redis.lpush(self._key, item.to_json())
            self._redis.hset(
                self._meta_key,
                mapping={
                    "last_error": error[:500],
                    "last_at": str(time.time()),
                    "last_source": source,
                },
            )
            log.warning(
                "dlq_push queue=%s source=%s id=%s err=%s", self.queue, source, item.id, error[:100]
            )
            return item.id
        except Exception as e:  # pragma: no cover
            log.error("dlq_push_failed queue=%s err=%s", self.queue, e)
            return None

    def depth(self) -> int:
        if not self._redis:
            return 0
        try:
            return int(self._redis.llen(self._key) or 0)
        except Exception:  # pragma: no cover
            return 0

    def peek(self, n: int = 10) -> list[DLQItem]:
        if not self._redis:
            return []
        try:
            raws = self._redis.lrange(self._key, 0, n - 1) or []
            return [DLQItem.from_json(r) for r in raws]
        except Exception:  # pragma: no cover
            return []

    def pop(self) -> DLQItem | None:
        if not self._redis:
            return None
        try:
            raw = self._redis.rpop(self._key)
            return DLQItem.from_json(raw) if raw else None
        except Exception:  # pragma: no cover
            return None

    def drain(self, limit: int = 100) -> list[DLQItem]:
        """Remove up to `limit` items from the queue (for replay)."""
        items: list[DLQItem] = []
        for _ in range(limit):
            it = self.pop()
            if not it:
                break
            items.append(it)
        return items

    def stats(self) -> dict[str, Any]:
        if not self._redis:
            return {"queue": self.queue, "depth": 0, "redis": "unavailable"}
        try:
            meta = self._redis.hgetall(self._meta_key) or {}
            return {
                "queue": self.queue,
                "depth": self.depth(),
                "last_error": meta.get("last_error"),
                "last_at": meta.get("last_at"),
                "last_source": meta.get("last_source"),
            }
        except Exception as e:  # pragma: no cover
            return {"queue": self.queue, "error": str(e)}


# Canonical queues for Dealix
WEBHOOKS_DLQ = "webhooks"  # failed inbound webhooks (HubSpot/Calendly/Moyasar/n8n)
OUTBOUND_DLQ = "outbound"  # failed outbound messages (email/WhatsApp/SMS)
ENRICHMENT_DLQ = "enrichment"  # failed lead enrichment calls (Enrich.so, etc.)
CRM_SYNC_DLQ = "crm_sync"  # failed HubSpot/CRM sync operations

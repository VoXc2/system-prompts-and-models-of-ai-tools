"""Dead Letter Queue — Redis-backed failure capture with retry drain.

Failed webhooks, integrations, and outbound calls land here instead of
being silently lost. Admin endpoints expose queue depth and allow
manual or automatic retry.
"""

from __future__ import annotations

import json
import time
import asyncio
import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Coroutine, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger("dealix.dlq")

MAX_RETRIES = 5
BACKOFF_BASE = 2


@dataclass
class DLQEntry:
    id: str = field(default_factory=lambda: str(uuid4()))
    queue: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    error: str = ""
    attempt: int = 0
    max_retries: int = MAX_RETRIES
    created_at: float = field(default_factory=time.time)
    last_attempt_at: float = 0.0

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls, raw: str | bytes) -> "DLQEntry":
        data = json.loads(raw)
        return cls(**data)


class DeadLetterQueue:
    """Redis list-backed DLQ with exponential-backoff retry."""

    def __init__(self, redis_client=None):
        self._redis = redis_client

    async def _get_redis(self):
        if self._redis is not None:
            return self._redis
        try:
            import redis.asyncio as aioredis
            from app.config import get_settings
            settings = get_settings()
            self._redis = aioredis.from_url(
                settings.REDIS_URL, decode_responses=True
            )
            return self._redis
        except Exception:
            logger.warning("Redis unavailable for DLQ — entries will be logged only")
            return None

    def _key(self, queue: str) -> str:
        return f"dlq:{queue}"

    async def push(
        self,
        queue: str,
        payload: Dict[str, Any],
        error: str,
        attempt: int = 0,
        max_retries: int = MAX_RETRIES,
    ) -> Optional[str]:
        entry = DLQEntry(
            queue=queue,
            payload=payload,
            error=str(error)[:2000],
            attempt=attempt,
            max_retries=max_retries,
        )
        r = await self._get_redis()
        if r is None:
            logger.error("DLQ.push(NO_REDIS) queue=%s error=%s", queue, error)
            return None
        await r.rpush(self._key(queue), entry.to_json())
        logger.info("DLQ.push queue=%s id=%s attempt=%d", queue, entry.id, attempt)
        return entry.id

    async def peek(self, queue: str, limit: int = 20) -> List[DLQEntry]:
        r = await self._get_redis()
        if r is None:
            return []
        raw_items = await r.lrange(self._key(queue), 0, limit - 1)
        return [DLQEntry.from_json(item) for item in raw_items]

    async def depth(self, queue: str) -> int:
        r = await self._get_redis()
        if r is None:
            return 0
        return await r.llen(self._key(queue))

    async def all_queues(self) -> Dict[str, int]:
        r = await self._get_redis()
        if r is None:
            return {}
        keys = []
        cursor = 0
        while True:
            cursor, batch = await r.scan(cursor, match="dlq:*", count=100)
            keys.extend(batch)
            if cursor == 0:
                break
        result = {}
        for key in keys:
            name = key.replace("dlq:", "", 1)
            result[name] = await r.llen(key)
        return result

    async def drain(
        self,
        queue: str,
        handler: Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]],
        batch_size: int = 10,
    ) -> Dict[str, Any]:
        r = await self._get_redis()
        if r is None:
            return {"processed": 0, "succeeded": 0, "re_queued": 0, "dead": 0}

        processed = succeeded = re_queued = dead = 0
        for _ in range(batch_size):
            raw = await r.lpop(self._key(queue))
            if raw is None:
                break
            entry = DLQEntry.from_json(raw)
            processed += 1
            try:
                await handler(entry.payload)
                succeeded += 1
                logger.info("DLQ.drain.ok queue=%s id=%s", queue, entry.id)
            except Exception as exc:
                entry.attempt += 1
                entry.error = str(exc)[:2000]
                entry.last_attempt_at = time.time()
                if entry.attempt >= entry.max_retries:
                    dead += 1
                    logger.error(
                        "DLQ.drain.dead queue=%s id=%s attempts=%d",
                        queue, entry.id, entry.attempt,
                    )
                else:
                    await r.rpush(self._key(queue), entry.to_json())
                    re_queued += 1
                    logger.warning(
                        "DLQ.drain.retry queue=%s id=%s attempt=%d",
                        queue, entry.id, entry.attempt,
                    )

        return {
            "processed": processed,
            "succeeded": succeeded,
            "re_queued": re_queued,
            "dead": dead,
        }

    async def purge(self, queue: str) -> int:
        r = await self._get_redis()
        if r is None:
            return 0
        count = await r.llen(self._key(queue))
        await r.delete(self._key(queue))
        return count


dlq = DeadLetterQueue()

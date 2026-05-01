"""
Semantic cache over Redis.

Each cached entry:
    key = f"{namespace}:{fingerprint}"
    value = JSON: {"query": ..., "answer": ..., "embedding": [f32...],
                   "model": ..., "created_at": ...}

Lookups:
    1. Compute embedding of incoming query.
    2. SCAN the namespace and fetch the N most recently used entries (bounded
       to ``max_scan`` to keep latency low).
    3. Pick the first entry with cosine similarity >= threshold.

Savings model:
    Local embedding is free (~50 ms CPU). Any hit skips an LLM call
    that would cost ~$0.001 - $0.15.  Even at a 10% hit rate on a busy
    agent pipeline, the net cost reduction is substantial.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import redis.asyncio as aioredis


@dataclass
class CacheHit:
    query: str
    answer: str
    similarity: float
    model: str
    cached_at: float


@dataclass
class CacheStats:
    hits: int = 0
    misses: int = 0
    writes: int = 0
    errors: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "writes": self.writes,
            "errors": self.errors,
            "hit_rate": round(self.hit_rate, 4),
        }


class SemanticCache:
    """Redis-backed semantic cache with local multilingual embeddings.

    Usage::

        cache = SemanticCache(redis=redis_client, namespace="icp")
        hit = await cache.lookup("ما هي فرص قطاع العقار؟")
        if hit is None:
            answer = await llm.chat(...)
            await cache.store(query, answer.content, model=answer.model)
        else:
            answer = hit.answer
    """

    DEFAULT_THRESHOLD = 0.95
    DEFAULT_TTL = 60 * 60 * 24  # 24h
    DEFAULT_MAX_SCAN = 200

    def __init__(
        self,
        redis: aioredis.Redis,
        *,
        namespace: str = "dealix:cache",
        threshold: float = DEFAULT_THRESHOLD,
        ttl: int = DEFAULT_TTL,
        max_scan: int = DEFAULT_MAX_SCAN,
    ) -> None:
        self.redis = redis
        self.namespace = namespace
        self.threshold = threshold
        self.ttl = ttl
        self.max_scan = max_scan
        self.stats = CacheStats()

    # ─── public API ──────────────────────────────────────────────

    async def lookup(self, query: str) -> CacheHit | None:
        """Return a CacheHit if a semantically similar entry exists."""
        import numpy as np

        from dealix.caching.embeddings import LocalEmbedder

        try:
            q_vec = LocalEmbedder.embed(query)
            keys = await self._scan_keys()
            if not keys:
                self.stats.misses += 1
                return None

            # Pipeline fetch for speed
            pipe = self.redis.pipeline()
            for k in keys:
                pipe.get(k)
            payloads = await pipe.execute()

            best_sim = 0.0
            best_hit: CacheHit | None = None
            for raw in payloads:
                if not raw:
                    continue
                entry = json.loads(raw)
                vec = np.asarray(entry["embedding"], dtype=np.float32)
                sim = LocalEmbedder.similarity(q_vec, vec)
                if sim >= self.threshold and sim > best_sim:
                    best_sim = sim
                    best_hit = CacheHit(
                        query=entry.get("query", ""),
                        answer=entry.get("answer", ""),
                        similarity=sim,
                        model=entry.get("model", "unknown"),
                        cached_at=entry.get("created_at", 0.0),
                    )
            if best_hit is not None:
                self.stats.hits += 1
                return best_hit
            self.stats.misses += 1
            return None
        except Exception:
            self.stats.errors += 1
            return None

    async def store(
        self,
        query: str,
        answer: str,
        *,
        model: str = "unknown",
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Persist a (query, answer) pair under the namespace."""
        from dealix.caching.embeddings import LocalEmbedder

        try:
            vec = LocalEmbedder.embed(query).tolist()
            key = f"{self.namespace}:{LocalEmbedder.fingerprint(query)}"
            payload = {
                "query": query,
                "answer": answer,
                "embedding": vec,
                "model": model,
                "created_at": time.time(),
                **(extra or {}),
            }
            await self.redis.set(key, json.dumps(payload), ex=self.ttl)
            self.stats.writes += 1
        except Exception:
            self.stats.errors += 1

    async def purge(self) -> int:
        """Delete every key in the namespace. Returns count."""
        keys = await self._scan_keys(limit=None)
        if not keys:
            return 0
        await self.redis.delete(*keys)
        return len(keys)

    # ─── internals ───────────────────────────────────────────────

    async def _scan_keys(self, limit: int | None = None) -> list[str]:
        pattern = f"{self.namespace}:*"
        max_items = self.max_scan if limit is None else limit
        keys: list[str] = []
        cursor = 0
        while True:
            cursor, batch = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            keys.extend(
                k.decode("utf-8") if isinstance(k, (bytes, bytearray)) else k for k in batch
            )
            if cursor == 0 or (limit and len(keys) >= max_items):
                break
        return keys[:max_items] if limit is None else keys

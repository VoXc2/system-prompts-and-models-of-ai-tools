"""FastAPI dependencies — shared Redis client, ApprovalGate, PostHog, etc."""

from __future__ import annotations

import os
from functools import lru_cache

import redis.asyncio as aioredis

from dealix.governance import ApprovalGate

_redis: aioredis.Redis | None = None
_gate: ApprovalGate | None = None


def _redis_url() -> str:
    return os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            _redis_url(),
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=3,
            socket_timeout=3,
        )
    return _redis


async def get_approval_gate() -> ApprovalGate:
    global _gate
    if _gate is None:
        r = await get_redis()
        _gate = ApprovalGate(r)
    return _gate


@lru_cache(maxsize=1)
def get_posthog_client():
    """Lazy PostHog client — HTTP-only, no SDK weight."""
    from dealix.analytics.posthog_client import PostHogClient

    return PostHogClient()

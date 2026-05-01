"""
Async retry with exponential backoff + jitter, optional DLQ push on final failure.
"""

from __future__ import annotations

import asyncio
import logging
import secrets
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from dealix.reliability.dlq import DLQ

log = logging.getLogger(__name__)

T = TypeVar("T")


async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    jitter: float = 0.2,
    dlq: DLQ | None = None,
    dlq_source: str = "",
    dlq_payload: dict[str, Any] | None = None,
    retryable: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    """
    Retry an async callable with exponential backoff + jitter.
    On final failure, if `dlq` is set, push to DLQ and re-raise.
    """
    last_exc: BaseException | None = None
    start = time.time()
    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except retryable as e:
            last_exc = e
            if attempt >= max_attempts:
                break
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            # jitter is UX, not crypto — but use secrets to appease S311
            delay += (secrets.randbelow(1000) / 1000.0) * (jitter * delay)
            log.warning(
                "retry attempt=%d/%d delay=%.2fs source=%s err=%s",
                attempt,
                max_attempts,
                delay,
                dlq_source,
                str(e)[:200],
            )
            await asyncio.sleep(delay)

    elapsed = time.time() - start
    log.error(
        "retry_exhausted attempts=%d elapsed=%.2fs source=%s err=%s",
        max_attempts,
        elapsed,
        dlq_source,
        str(last_exc)[:200],
    )
    if dlq:
        dlq.push(
            source=dlq_source or "unknown",
            payload=dlq_payload or {},
            error=str(last_exc or "unknown")[:500],
            attempts=max_attempts,
        )
    assert last_exc is not None
    raise last_exc

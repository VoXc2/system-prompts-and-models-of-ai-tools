"""
Cost tracker for every LLM call.

Each call records:
    provider, model, input_tokens, output_tokens, cached_tokens,
    cost_usd, request_id, agent_name, latency_ms, created_at

Storage:
    - Primary: Postgres table ``llm_calls``  (best: durable + queryable)
    - Fallback: in-memory ring buffer so tests / local dev work DB-less.

Pricing (USD / million tokens, last updated 2026-04):
    Claude Sonnet        : $3.00 in  | $15.00 out | $0.30 cached
    Gemini 2.5 Flash     : $0.075 in | $0.30 out
    DeepSeek V3          : $0.14 in  | $0.28 out
    GLM-4                : $0.14 in  | $0.28 out
    Groq Llama-3.3 70B   : $0 (free tier ~30 req/min)
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections import deque
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import asyncpg  # type: ignore

logger = logging.getLogger("dealix.costs")


# ─── Pricing (USD per 1M tokens) ──────────────────────────────────────────────

MODEL_PRICES: dict[str, dict[str, float]] = {
    # Anthropic
    "claude-sonnet-4-5": {"in": 3.00, "out": 15.00, "cached": 0.30},
    "claude-sonnet-4-5-20250929": {"in": 3.00, "out": 15.00, "cached": 0.30},
    "claude-opus-4": {"in": 15.00, "out": 75.00, "cached": 1.50},
    "claude-haiku-4": {"in": 0.25, "out": 1.25, "cached": 0.03},
    # Google
    "gemini-2.5-flash": {"in": 0.075, "out": 0.30, "cached": 0.019},
    "gemini-2.5-pro": {"in": 1.25, "out": 5.00, "cached": 0.31},
    # DeepSeek
    "deepseek-chat": {"in": 0.14, "out": 0.28, "cached": 0.014},
    "deepseek-reasoner": {"in": 0.55, "out": 2.19, "cached": 0.14},
    # Zhipu GLM
    "glm-4": {"in": 0.14, "out": 0.28, "cached": 0.014},
    "glm-4-plus": {"in": 0.70, "out": 2.10, "cached": 0.07},
    # Groq (free tier)
    "llama-3.3-70b-versatile": {"in": 0.0, "out": 0.0, "cached": 0.0},
    "llama-3.1-8b-instant": {"in": 0.0, "out": 0.0, "cached": 0.0},
}


def estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0,
) -> float:
    """Return the estimated USD cost of a completion.

    Falls back to ``claude-sonnet-4-5`` pricing for unknown models — conservative
    (high) so we never *under* report spend.
    """
    price = MODEL_PRICES.get(model, MODEL_PRICES["claude-sonnet-4-5"])
    billable_in = max(input_tokens - cached_tokens, 0)
    cost = (
        (billable_in * price["in"])
        + (cached_tokens * price["cached"])
        + (output_tokens * price["out"])
    ) / 1_000_000
    return round(cost, 6)


# ─── Entry + Tracker ──────────────────────────────────────────────────────────


@dataclass
class CostEntry:
    request_id: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost_usd: float
    agent_name: str | None = None
    latency_ms: float | None = None
    status: str = "ok"  # ok | error
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d


class CostTracker:
    """Records every LLM call.

    Use as an async-context-style wrapper::

        tracker = CostTracker(dsn=settings.postgres_dsn)
        await tracker.record(
            provider="anthropic",
            model="claude-sonnet-4-5",
            input_tokens=1200,
            output_tokens=400,
            cached_tokens=800,
            agent_name="icp_matcher",
            latency_ms=1234.5,
        )
    """

    SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS llm_calls (
        id              BIGSERIAL PRIMARY KEY,
        request_id      TEXT NOT NULL,
        provider        TEXT NOT NULL,
        model           TEXT NOT NULL,
        input_tokens    INT  NOT NULL,
        output_tokens   INT  NOT NULL,
        cached_tokens   INT  NOT NULL DEFAULT 0,
        cost_usd        NUMERIC(12, 6) NOT NULL,
        agent_name      TEXT,
        latency_ms      NUMERIC(10, 2),
        status          TEXT NOT NULL DEFAULT 'ok',
        error           TEXT,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS llm_calls_created_at_idx ON llm_calls (created_at DESC);
    CREATE INDEX IF NOT EXISTS llm_calls_agent_idx       ON llm_calls (agent_name);
    """

    def __init__(
        self,
        dsn: str | None = None,
        *,
        buffer_size: int = 1000,
    ) -> None:
        self.dsn = dsn
        self._pool: asyncpg.Pool | None = None
        self._buffer: deque[CostEntry] = deque(maxlen=buffer_size)
        self._schema_ready = False
        self._lock = asyncio.Lock()

    # ── lifecycle ─────────────────────────────────────────────

    async def _ensure_pool(self) -> None:
        if self.dsn is None or self._pool is not None:
            return
        import asyncpg  # type: ignore

        self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=4)
        async with self._pool.acquire() as conn:
            await conn.execute(self.SCHEMA_SQL)
        self._schema_ready = True

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    # ── core API ──────────────────────────────────────────────

    async def record(
        self,
        *,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        agent_name: str | None = None,
        latency_ms: float | None = None,
        status: str = "ok",
        error: str | None = None,
        request_id: str | None = None,
    ) -> CostEntry:
        entry = CostEntry(
            request_id=request_id or uuid.uuid4().hex,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cost_usd=estimate_cost_usd(model, input_tokens, output_tokens, cached_tokens),
            agent_name=agent_name,
            latency_ms=latency_ms,
            status=status,
            error=error,
        )
        # in-memory always
        self._buffer.append(entry)
        # best-effort persistence
        try:
            await self._ensure_pool()
            if self._pool is not None:
                async with self._pool.acquire() as conn:
                    await conn.execute(
                        """INSERT INTO llm_calls (request_id, provider, model,
                             input_tokens, output_tokens, cached_tokens, cost_usd,
                             agent_name, latency_ms, status, error, created_at)
                           VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)""",
                        entry.request_id,
                        entry.provider,
                        entry.model,
                        entry.input_tokens,
                        entry.output_tokens,
                        entry.cached_tokens,
                        entry.cost_usd,
                        entry.agent_name,
                        entry.latency_ms,
                        entry.status,
                        entry.error,
                        entry.created_at,
                    )
        except Exception as exc:  # pragma: no cover — degrade gracefully
            logger.warning("cost_tracker: persistence failed: %s", exc)
        return entry

    # ── reporting ─────────────────────────────────────────────

    def recent(self, limit: int = 50) -> list[CostEntry]:
        return list(self._buffer)[-limit:]

    def totals(self) -> dict[str, float]:
        """In-memory summary — O(n) over the ring buffer."""
        total = 0.0
        per_provider: dict[str, float] = {}
        per_model: dict[str, float] = {}
        for e in self._buffer:
            total += e.cost_usd
            per_provider[e.provider] = per_provider.get(e.provider, 0.0) + e.cost_usd
            per_model[e.model] = per_model.get(e.model, 0.0) + e.cost_usd
        return {
            "total_usd": round(total, 4),
            "per_provider": {k: round(v, 4) for k, v in per_provider.items()},
            "per_model": {k: round(v, 4) for k, v in per_model.items()},
            "count": len(self._buffer),
        }

    async def query_window(
        self,
        *,
        since: datetime,
        until: datetime | None = None,
    ) -> list[dict[str, Any]]:  # pragma: no cover — requires DB
        """Return raw rows between two timestamps (UTC)."""
        await self._ensure_pool()
        if self._pool is None:
            return []
        until = until or datetime.now(tz=UTC)
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT * FROM llm_calls
                    WHERE created_at >= $1 AND created_at <= $2
                    ORDER BY created_at DESC""",
                since,
                until,
            )
        return [dict(r) for r in rows]

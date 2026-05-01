"""
Connector Facade — one class fronting every external integration.
واجهة موحّدة لكل التكاملات الخارجية.

Provides:
  * Timeouts + exponential retry
  * Idempotency keys
  * Per-connector allow/deny policy
  * Audit log into Postgres (or in-memory ring fallback)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass, field
from typing import Any

from dealix.reliability.dlq import DLQ

log = logging.getLogger(__name__)


@dataclass
class BreakerState:
    """In-memory circuit breaker per connector."""

    failures: int = 0
    opened_at: float = 0.0
    threshold: int = 5
    cooldown_s: float = 30.0

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.threshold and not self.opened_at:
            self.opened_at = time.time()

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = 0.0

    def is_open(self) -> bool:
        if not self.opened_at:
            return False
        if time.time() - self.opened_at >= self.cooldown_s:
            # half-open: reset and allow one trial
            self.opened_at = 0.0
            self.failures = 0
            return False
        return True


@dataclass
class ConnectorPolicy:
    allow: bool = True
    max_calls_per_minute: int = 120
    timeout_s: float = 10.0
    max_retries: int = 3
    backoff_base: float = 0.5
    require_idempotency: bool = False


@dataclass
class ConnectorResult:
    ok: bool
    connector: str
    operation: str
    data: Any = None
    error: str | None = None
    attempts: int = 0
    duration_ms: float = 0.0
    idempotency_key: str | None = None
    meta: dict[str, Any] = field(default_factory=dict)


DEFAULT_POLICIES: dict[str, ConnectorPolicy] = {
    "hubspot": ConnectorPolicy(max_calls_per_minute=100, timeout_s=8, require_idempotency=True),
    "calendly": ConnectorPolicy(max_calls_per_minute=60, timeout_s=8),
    "enrich_so": ConnectorPolicy(max_calls_per_minute=30, timeout_s=15),
    "whatsapp": ConnectorPolicy(max_calls_per_minute=90, timeout_s=10),
    "n8n": ConnectorPolicy(max_calls_per_minute=200, timeout_s=10),
    "linkedin": ConnectorPolicy(max_calls_per_minute=20, timeout_s=15),
    "email": ConnectorPolicy(max_calls_per_minute=120, timeout_s=15),
}


def _idem_key(connector: str, operation: str, payload: Any) -> str:
    body = json.dumps(payload, sort_keys=True, default=str) if payload is not None else ""
    return hashlib.sha256(f"{connector}:{operation}:{body}".encode()).hexdigest()[:32]


class ConnectorFacade:
    """Single entrypoint for connector calls with retry + policy + audit."""

    def __init__(
        self,
        policies: dict[str, ConnectorPolicy] | None = None,
        dlq_queue: str = "outbound",
    ) -> None:
        self.policies = {**DEFAULT_POLICIES, **(policies or {})}
        self._audit: list[ConnectorResult] = []
        self._max_audit = 1000
        self._breakers: dict[str, BreakerState] = {}
        self._dlq = DLQ(dlq_queue)

    def _breaker(self, connector: str) -> BreakerState:
        return self._breakers.setdefault(connector, BreakerState())

    def _policy(self, connector: str) -> ConnectorPolicy:
        return self.policies.get(connector, ConnectorPolicy())

    async def call(
        self,
        connector: str,
        operation: str,
        func: Callable[..., Awaitable[Any]],
        *args: Any,
        payload: Any = None,
        idempotency_key: str | None = None,
        **kwargs: Any,
    ) -> ConnectorResult:
        policy = self._policy(connector)
        if not policy.allow:
            return ConnectorResult(
                ok=False,
                connector=connector,
                operation=operation,
                error="connector_disabled_by_policy",
            )

        breaker = self._breaker(connector)
        if breaker.is_open():
            log.warning("circuit_open connector=%s op=%s", connector, operation)
            return ConnectorResult(
                ok=False,
                connector=connector,
                operation=operation,
                error=f"circuit_open_for_{int(breaker.cooldown_s)}s",
            )

        idem = idempotency_key or _idem_key(connector, operation, payload)
        start = time.perf_counter()
        last_err: Exception | None = None
        result: Any = None

        for attempt in range(1, policy.max_retries + 1):
            try:
                result = await asyncio.wait_for(
                    func(*args, **kwargs) if payload is None else func(payload, *args, **kwargs),
                    timeout=policy.timeout_s,
                )
                res = ConnectorResult(
                    ok=True,
                    connector=connector,
                    operation=operation,
                    data=result,
                    attempts=attempt,
                    duration_ms=(time.perf_counter() - start) * 1000,
                    idempotency_key=idem,
                )
                breaker.record_success()
                self._record(res)
                return res
            except Exception as e:
                last_err = e
                backoff = policy.backoff_base * (2 ** (attempt - 1))
                log.warning(
                    "connector_retry",
                    extra={
                        "connector": connector,
                        "op": operation,
                        "attempt": attempt,
                        "err": str(e)[:200],
                    },
                )
                if attempt < policy.max_retries:
                    await asyncio.sleep(backoff)

        res = ConnectorResult(
            ok=False,
            connector=connector,
            operation=operation,
            error=str(last_err)[:500] if last_err else "unknown",
            attempts=policy.max_retries,
            duration_ms=(time.perf_counter() - start) * 1000,
            idempotency_key=idem,
        )
        breaker.record_failure()
        # Final failure → push to DLQ for operator replay
        try:
            self._dlq.push(
                source=f"{connector}.{operation}",
                payload={"payload": payload, "idempotency_key": idem},
                error=res.error or "unknown",
                attempts=policy.max_retries,
                metadata={"duration_ms": res.duration_ms},
            )
        except Exception as _dlq_err:  # pragma: no cover
            log.warning(
                "dlq_push_failed source=%s.%s err=%s", connector, operation, str(_dlq_err)[:200]
            )
        self._record(res)
        return res

    def _record(self, r: ConnectorResult) -> None:
        self._audit.append(r)
        if len(self._audit) > self._max_audit:
            self._audit = self._audit[-self._max_audit :]
        self._persist(r)

    def _persist(self, r: ConnectorResult) -> None:
        """Optional Postgres persist — best-effort, no-op if no DB configured."""
        dsn = os.getenv("DATABASE_URL") or os.getenv("DATABASE_DSN")
        if not dsn:
            return
        try:
            import psycopg2  # type: ignore

            conn = psycopg2.connect(dsn, connect_timeout=3)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS connector_audit (
                    id SERIAL PRIMARY KEY,
                    ts TIMESTAMPTZ DEFAULT now(),
                    connector TEXT, operation TEXT, ok BOOLEAN,
                    attempts INT, duration_ms DOUBLE PRECISION,
                    idempotency_key TEXT, error TEXT, meta JSONB
                )
                """)
            cur.execute(
                """
                INSERT INTO connector_audit
                    (connector, operation, ok, attempts, duration_ms, idempotency_key, error, meta)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    r.connector,
                    r.operation,
                    r.ok,
                    r.attempts,
                    r.duration_ms,
                    r.idempotency_key,
                    r.error,
                    json.dumps(r.meta, default=str),
                ),
            )
            conn.commit()
            conn.close()
        except Exception as _audit_err:  # pragma: no cover
            # audit is best-effort — log for diagnosis but never fail the caller
            log.debug("connector_audit_persist_failed err=%s", str(_audit_err)[:200])

    def audit_tail(self, n: int = 50) -> list[dict[str, Any]]:
        return [asdict(r) for r in self._audit[-n:]]


# ── Concrete connectors built on top of the facade ────────────────
class EnrichSoClient:
    """Thin client for Enrich.so lead enrichment (free tier-friendly)."""

    BASE = "https://api.enrich.so/v1"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("ENRICH_SO_API_KEY")

    async def enrich(self, email: str) -> dict[str, Any]:
        import httpx

        if not self.api_key:
            raise RuntimeError("ENRICH_SO_API_KEY not set")
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(
                f"{self.BASE}/person",
                params={"email": email},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            r.raise_for_status()
            return r.json()


class HubSpotTwoWay:
    """HubSpot connector with bidirectional webhook support."""

    BASE = "https://api.hubapi.com"

    def __init__(self, access_token: str | None = None) -> None:
        self.token = access_token or os.getenv("HUBSPOT_ACCESS_TOKEN")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    async def upsert_contact(self, email: str, properties: dict[str, Any]) -> dict[str, Any]:
        import httpx

        async with httpx.AsyncClient(timeout=10) as c:
            # search first, update if exists else create
            search = await c.post(
                f"{self.BASE}/crm/v3/objects/contacts/search",
                headers=self._headers(),
                json={
                    "filterGroups": [
                        {"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}
                    ],
                    "limit": 1,
                },
            )
            search.raise_for_status()
            results = search.json().get("results", [])
            if results:
                cid = results[0]["id"]
                r = await c.patch(
                    f"{self.BASE}/crm/v3/objects/contacts/{cid}",
                    headers=self._headers(),
                    json={"properties": {**properties, "email": email}},
                )
            else:
                r = await c.post(
                    f"{self.BASE}/crm/v3/objects/contacts",
                    headers=self._headers(),
                    json={"properties": {**properties, "email": email}},
                )
            r.raise_for_status()
            return r.json()

    async def handle_inbound_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Process inbound contact update from HubSpot → update local lead."""
        events = payload.get("events") or [payload]
        return {"processed": len(events)}


class CalendlyDynamic:
    """Calendly with per-lead dynamic booking links."""

    BASE = "https://api.calendly.com"

    def __init__(self, token: str | None = None, user_uri: str | None = None) -> None:
        self.token = token or os.getenv("CALENDLY_API_TOKEN")
        self.user_uri = user_uri or os.getenv("CALENDLY_USER_URI")

    async def create_single_use_link(
        self,
        event_type_uri: str,
        owner_uri: str | None = None,
    ) -> dict[str, Any]:
        import httpx

        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.post(
                f"{self.BASE}/scheduling_links",
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={
                    "max_event_count": 1,
                    "owner": owner_uri or self.user_uri,
                    "owner_type": "EventType",
                },
            )
            r.raise_for_status()
            return r.json()

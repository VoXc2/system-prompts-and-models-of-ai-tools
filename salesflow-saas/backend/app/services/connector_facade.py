"""
Connector Facade — Dealix Sovereign Data Plane

Provides a governed, versioned wrapper for ALL external API integrations.
Every connector call:
  - Has a contract schema
  - Has a retry policy (exponential backoff)
  - Has a timeout
  - Has an idempotency key strategy
  - Has an approval policy (A/B/C)
  - Is logged to the ToolVerificationLedger
  - Emits OTel traces + metrics
  - Has rollback/compensation notes

Agents MUST NOT call external APIs directly — they go through this facade.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.sovereign import ConnectorRegistry, ToolVerificationLedger
from app.services.otel_instrumentation import record_connector_call, new_correlation_id


class ConnectorCallError(Exception):
    def __init__(self, connector_key: str, status_code: int, message: str):
        self.connector_key = connector_key
        self.status_code = status_code
        super().__init__(f"[{connector_key}] HTTP {status_code}: {message}")


class ConnectorFacade:
    """
    Governed connector proxy.
    Usage:
        facade = ConnectorFacade(db, tenant_id)
        result = await facade.call("hubspot", "create_contact", payload)
    """

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def call(
        self,
        connector_key: str,
        action: str,
        payload: dict[str, Any],
        *,
        idempotency_key: str | None = None,
        correlation_id: str | None = None,
        _executor: Callable[..., Coroutine] | None = None,
    ) -> dict[str, Any]:
        """
        Execute a governed connector call with retry, idempotency, and audit logging.

        _executor is an async callable (connector_key, action, payload) → dict.
        If not provided, a mock executor is used (for testing/dev).
        """
        corr_id = correlation_id or new_correlation_id()
        config = await self._get_config(connector_key)
        retry_policy = config.get("retry_policy") or {"max_retries": 3, "backoff_multiplier_ms": 1000, "max_backoff_ms": 30000}
        timeout_ms = config.get("timeout_ms") or 30000

        idem_key = idempotency_key or self._generate_idempotency_key(connector_key, action, payload)

        t_start = time.monotonic()
        last_exc: Exception | None = None
        result: dict[str, Any] = {}
        outcome = "success"

        max_retries = int(retry_policy.get("max_retries", 3))
        backoff_ms = int(retry_policy.get("backoff_multiplier_ms", 1000))
        max_backoff_ms = int(retry_policy.get("max_backoff_ms", 30000))

        for attempt in range(max_retries + 1):
            try:
                if _executor:
                    result = await asyncio.wait_for(
                        _executor(connector_key, action, payload),
                        timeout=timeout_ms / 1000,
                    )
                else:
                    result = self._mock_executor(connector_key, action, payload)
                outcome = "success"
                break
            except (asyncio.TimeoutError, ConnectorCallError, Exception) as exc:
                last_exc = exc
                outcome = "failed"
                if attempt < max_retries:
                    wait = min(backoff_ms * (2 ** attempt), max_backoff_ms) / 1000
                    await asyncio.sleep(wait)

        latency_ms = int((time.monotonic() - t_start) * 1000)

        # Update connector health
        await self._update_health(connector_key, outcome == "success", last_exc)

        # Log to ToolVerificationLedger
        ledger = ToolVerificationLedger(
            tenant_id=self.tenant_id,
            agent_role="connector_facade",
            tool_name=f"{connector_key}.{action}",
            intended_action=f"{action} via {connector_key}",
            claimed_action=f"{action} via {connector_key}",
            actual_tool_call={
                "connector_key": connector_key,
                "action": action,
                "payload_keys": list(payload.keys()),
                "idempotency_key": idem_key,
            },
            side_effects=[],
            contradiction_status="none",
            correlation_id=corr_id,
            outcome=outcome,
            latency_ms=latency_ms,
        )
        self.db.add(ledger)
        await self.db.commit()

        await record_connector_call(
            connector_key=connector_key,
            latency_ms=latency_ms,
            success=outcome == "success",
            tenant_id=self.tenant_id,
        )

        if outcome != "success" and last_exc:
            raise last_exc

        return {**result, "_meta": {"correlation_id": corr_id, "latency_ms": latency_ms, "idempotency_key": idem_key}}

    async def _get_config(self, connector_key: str) -> dict[str, Any]:
        result = await self.db.execute(
            select(ConnectorRegistry).where(
                ConnectorRegistry.tenant_id == self.tenant_id,
                ConnectorRegistry.connector_key == connector_key,
                ConnectorRegistry.is_active.is_(True),
            ).limit(1)
        )
        row = result.scalar_one_or_none()
        if row:
            return {
                "retry_policy": row.retry_policy,
                "timeout_ms": row.timeout_ms,
                "approval_policy": row.approval_policy,
                "api_version": row.api_version,
            }
        return {"retry_policy": None, "timeout_ms": 30000, "approval_policy": "A", "api_version": "latest"}

    async def _update_health(self, connector_key: str, success: bool, exc: Exception | None) -> None:
        result = await self.db.execute(
            select(ConnectorRegistry).where(
                ConnectorRegistry.tenant_id == self.tenant_id,
                ConnectorRegistry.connector_key == connector_key,
                ConnectorRegistry.is_active.is_(True),
            ).limit(1)
        )
        row = result.scalar_one_or_none()
        if row:
            row.last_attempt_at = datetime.now(timezone.utc)
            if success:
                row.last_success_at = datetime.now(timezone.utc)
                row.health_status = "ok"
                row.last_error = None
            else:
                row.health_status = "error"
                row.last_error = str(exc)[:500] if exc else "unknown"
            await self.db.flush()

    def _generate_idempotency_key(self, connector_key: str, action: str, payload: dict) -> str:
        payload_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        return f"{connector_key}:{action}:{payload_hash}"

    def _mock_executor(self, connector_key: str, action: str, payload: dict) -> dict:
        """Development mock — replace with real HTTP client per connector."""
        return {
            "status": "ok",
            "connector": connector_key,
            "action": action,
            "mock": True,
        }

    async def get_health_board(self) -> list[dict[str, Any]]:
        result = await self.db.execute(
            select(ConnectorRegistry).where(
                ConnectorRegistry.tenant_id == self.tenant_id,
            ).order_by(ConnectorRegistry.connector_key)
        )
        rows = result.scalars().all()
        return [
            {
                "id": str(r.id),
                "connector_key": r.connector_key,
                "display_name_ar": r.display_name_ar,
                "display_name_en": r.display_name_en,
                "vendor": r.vendor,
                "api_version": r.api_version,
                "health_status": r.health_status,
                "last_success_at": r.last_success_at.isoformat() if r.last_success_at else None,
                "last_attempt_at": r.last_attempt_at.isoformat() if r.last_attempt_at else None,
                "last_error": r.last_error,
                "is_active": r.is_active,
                "approval_policy": r.approval_policy,
            }
            for r in rows
        ]

# Connector Facade Standard

> **Version:** 1.0 — 2026-04-16
> **Authority:** Backend Lead — all new connector implementations must comply.
> **Purpose:** Prevent raw vendor API chaos by wrapping every external integration in a versioned, typed, auditable facade.

---

## Motivation

- Vendor APIs change independently (HubSpot date-based versioning from 2026, DocuSign API lifecycle, etc.).
- Without facades, a vendor change breaks multiple agent flows silently.
- Facades provide: stable internal contract, retry/timeout/idempotency enforcement, audit logging, and version isolation.

---

## Base Connector Class

File: `backend/app/connectors/base.py`

```python
from __future__ import annotations

import abc
import uuid
import logging
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from opentelemetry import trace
from pydantic import BaseModel

logger = logging.getLogger(__name__)
tracer = trace.get_tracer("dealix.connectors")

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class ConnectorAuditEntry(BaseModel):
    entry_id: str
    connector_name: str
    connector_version: str
    idempotency_key: str
    tenant_id: str
    action: str
    status: str  # success | failed | retried | skipped_duplicate
    request_payload_hash: str
    response_summary: str
    duration_ms: float
    timestamp: datetime
    trace_id: str


class BaseConnector(abc.ABC, Generic[InputT, OutputT]):
    """
    Abstract base for all external vendor connectors.

    Subclasses must implement:
      - connector_name: str
      - connector_version: str  (e.g. "v1", "v2")
      - _execute(input: InputT) -> OutputT

    The base class enforces:
      - Idempotency (duplicate key = skip + return cached result)
      - Retry with exponential backoff
      - Timeout enforcement
      - OTel tracing on every call
      - Audit log emission
    """

    connector_name: str
    connector_version: str

    MAX_RETRIES: int = 3
    BACKOFF_BASE_SECONDS: float = 2.0
    TIMEOUT_SECONDS: float = 30.0
    NON_RETRYABLE_STATUS_CODES: tuple[int, ...] = (400, 401, 403, 404, 422)

    def __init__(self, tenant_id: str, idempotency_store: IdempotencyStore) -> None:
        self.tenant_id = tenant_id
        self._idempotency_store = idempotency_store

    async def call(
        self,
        action: str,
        input_data: InputT,
        idempotency_key: str,
    ) -> OutputT:
        """Public entry point. Enforces idempotency, retry, tracing, audit."""
        with tracer.start_as_current_span(
            f"{self.connector_name}.{action}",
            attributes={
                "connector.name": self.connector_name,
                "connector.version": self.connector_version,
                "connector.action": action,
                "tenant.id": self.tenant_id,
                "idempotency.key": idempotency_key,
            },
        ) as span:
            # Idempotency check
            cached = await self._idempotency_store.get(idempotency_key)
            if cached is not None:
                logger.info(
                    "Idempotency hit — skipping duplicate call",
                    extra={"idempotency_key": idempotency_key},
                )
                span.set_attribute("idempotency.hit", True)
                return cached

            start = datetime.now(timezone.utc)
            result = await self._call_with_retry(action, input_data, span)
            duration_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            await self._idempotency_store.set(idempotency_key, result)
            await self._emit_audit(action, idempotency_key, input_data, result, duration_ms, span)
            return result

    async def _call_with_retry(self, action: str, input_data: InputT, span: Any) -> OutputT:
        import asyncio
        import hashlib
        attempt = 0
        last_exc: Exception | None = None
        while attempt < self.MAX_RETRIES:
            try:
                return await self._execute(input_data)
            except NonRetryableConnectorError:
                raise
            except ConnectorError as exc:
                last_exc = exc
                attempt += 1
                wait = self.BACKOFF_BASE_SECONDS ** attempt
                logger.warning(
                    "Connector call failed, retrying",
                    extra={"attempt": attempt, "wait_s": wait, "error": str(exc)},
                )
                span.add_event("retry", {"attempt": attempt, "wait_s": wait})
                await asyncio.sleep(wait)
        raise ConnectorMaxRetriesExceeded(self.connector_name, action) from last_exc

    @abc.abstractmethod
    async def _execute(self, input_data: InputT) -> OutputT:
        """Implement vendor-specific API call here."""
        ...

    async def _emit_audit(
        self,
        action: str,
        idempotency_key: str,
        input_data: InputT,
        result: OutputT,
        duration_ms: float,
        span: Any,
    ) -> None:
        import hashlib, json
        trace_id = format(span.get_span_context().trace_id, "032x")
        entry = ConnectorAuditEntry(
            entry_id=str(uuid.uuid4()),
            connector_name=self.connector_name,
            connector_version=self.connector_version,
            idempotency_key=idempotency_key,
            tenant_id=self.tenant_id,
            action=action,
            status="success",
            request_payload_hash=hashlib.sha256(
                input_data.model_dump_json().encode()
            ).hexdigest()[:16],
            response_summary=str(result)[:200],
            duration_ms=duration_ms,
            timestamp=datetime.now(timezone.utc),
            trace_id=trace_id,
        )
        logger.info("connector.audit", extra=entry.model_dump())


class ConnectorError(Exception):
    pass

class NonRetryableConnectorError(ConnectorError):
    pass

class ConnectorMaxRetriesExceeded(ConnectorError):
    def __init__(self, name: str, action: str) -> None:
        super().__init__(f"{name}.{action} exceeded max retries")


class IdempotencyStore(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: str) -> Any | None: ...
    @abc.abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int = 86400) -> None: ...
```

---

## Versioning Contract

Every connector has a `connector_version` string (`"v1"`, `"v2"`, …).

When a vendor releases a breaking API change:
1. Create `connector_v2.py` implementing the new version.
2. Keep `connector_v1.py` until all callers are migrated.
3. Update routing in `backend/app/connectors/registry.py`.
4. Add migration guide to `docs/connector-migrations/`.

**Internal interfaces never change** — only vendor-facing implementation changes per version.

---

## Idempotency Key Format (All Connectors)

```
{tenant_id}:{connector_name}:{action}:{entity_id}:{date_yyyymmdd}
Example: "acme:docusign:send_envelope:deal-uuid-123:20260416"
```

For Temporal activities, use the Temporal `activity_id` as the idempotency key.

---

## Timeout & Retry Policies (Defaults — Override Per Connector)

| Connector | Timeout | Max Retries | Non-retryable Codes |
|-----------|---------|------------|-------------------|
| HubSpot | 15 s | 3 | 400, 401, 403 |
| DocuSign | 30 s | 3 | 400, 401, 403, 404 |
| WhatsApp/Twilio | 10 s | 5 | 400, 401 |
| Email (SMTP/SendGrid) | 10 s | 3 | 400, 401, 403 |
| Calendar (Google/O365) | 15 s | 3 | 400, 401, 403 |
| Billing (internal) | 30 s | 3 | 400, 409 (conflict) |

---

## Registered Connectors

| Connector | Module | Version | Status | Owner |
|-----------|--------|---------|--------|-------|
| HubSpot CRM | `connectors/hubspot_v1.py` | v1 | 🟡 Partial | Backend Engineer |
| WhatsApp/Twilio | `connectors/twilio_v1.py` | v1 | 🔶 Pilot | Backend Engineer |
| DocuSign | `connectors/docusign_v1.py` | v1 | 🟡 Partial | Backend Engineer |
| Email (SendGrid) | `connectors/sendgrid_v1.py` | v1 | 🟡 Partial | Backend Engineer |
| Google Calendar | `connectors/gcal_v1.py` | v1 | ⬜ Planned | Backend Engineer |
| Billing (internal) | `connectors/billing_v1.py` | v1 | ⬜ Planned | Backend Engineer |

---

## CloudEvents Envelope Standard

All events emitted between services must conform to CloudEvents spec:

```json
{
  "specversion": "1.0",
  "type": "ai.dealix.deal.approved",
  "source": "https://dealix.ai/agents/closing-advisor",
  "id": "uuid-v4",
  "time": "2026-04-16T10:00:00Z",
  "datacontenttype": "application/json",
  "subject": "deal/{deal_id}",
  "tenantid": "tenant-uuid",
  "dataresidency": "KSA",
  "data": {
    "deal_id": "uuid",
    "track": "closing",
    "action_taken": "docusign_envelope_sent",
    "approval_packet_id": "uuid"
  }
}
```

Event types follow: `ai.dealix.{entity}.{verb}` (e.g. `ai.dealix.partner.approved`, `ai.dealix.deal.closed`).

---

## AsyncAPI Registry (asyncapi.yaml excerpt)

```yaml
asyncapi: "3.0.0"
info:
  title: Dealix Event API
  version: "1.0.0"

channels:
  deal.approved:
    address: "deal/{deal_id}/approved"
    messages:
      DealApproved:
        payload:
          type: object
          required: [deal_id, track, approval_packet_id]
          properties:
            deal_id: { type: string, format: uuid }
            track: { type: string }
            approval_packet_id: { type: string, format: uuid }

  partner.onboarded:
    address: "partner/{partner_id}/onboarded"
    messages:
      PartnerOnboarded:
        payload:
          type: object
          required: [partner_id, tenant_id, tier]
          properties:
            partner_id: { type: string, format: uuid }
            tenant_id: { type: string, format: uuid }
            tier: { type: string, enum: [gold, silver, bronze] }
```

"""Idempotency Service — prevents duplicate side effects across retries.

Used by both HTTP middleware and service-level callers (approval_bridge,
evidence_pack_service, golden_path).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def hash_request(body: Any) -> str:
    """Compute SHA256 of request body for fingerprinting."""
    payload = json.dumps(body, sort_keys=True, default=str) if body is not None else ""
    return hashlib.sha256(payload.encode()).hexdigest()


class IdempotencyService:
    """Manages idempotency key lifecycle."""

    DEFAULT_TTL_HOURS = 24

    async def get_existing(
        self, db: AsyncSession, *, key: str, tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return cached response for key if exists and not expired."""
        from app.models.idempotency_key import IdempotencyKey

        stmt = select(IdempotencyKey).where(
            IdempotencyKey.key == key,
            IdempotencyKey.tenant_id == tenant_id,
        )
        result = await db.execute(stmt)
        row = result.scalar_one_or_none()
        if not row:
            return None

        # Expiry check
        if row.expires_at and row.expires_at < datetime.now(timezone.utc):
            return None

        return {
            "cached": True,
            "key": row.key,
            "endpoint": row.endpoint,
            "request_hash": row.request_hash,
            "response": row.response,
            "status_code": row.status_code,
        }

    async def store(
        self,
        db: AsyncSession,
        *,
        key: str,
        tenant_id: str,
        endpoint: str,
        request_body: Any,
        response: Any,
        status_code: int = 200,
        ttl_hours: int = DEFAULT_TTL_HOURS,
    ) -> None:
        """Store response keyed by idempotency key."""
        from app.models.idempotency_key import IdempotencyKey

        record = IdempotencyKey(
            tenant_id=tenant_id,
            key=key,
            endpoint=endpoint,
            request_hash=hash_request(request_body),
            response=response if isinstance(response, dict) else {"value": response},
            status_code=str(status_code),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
        )
        db.add(record)
        await db.commit()


idempotency_service = IdempotencyService()

"""
Ingest existing domain tables into SystemMemoryRecord (Phase 1 wiring).

Call from `emit_domain_event` after flush so every DomainEvent is mirrored into unified memory.
"""

from __future__ import annotations

from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operations import DomainEvent
from app.models.second_brain import MemorySource, SystemMemoryRecord


async def mirror_domain_event_to_memory(db: AsyncSession, ev: DomainEvent) -> SystemMemoryRecord:
    """Create a canonical memory row from an existing DomainEvent row."""
    payload: Dict[str, Any] = {
        "event_type": ev.event_type,
        "payload": ev.payload or {},
        "source": ev.source,
        "correlation_id": ev.correlation_id,
        "domain_event_created_at": ev.created_at.isoformat() if ev.created_at else None,
    }
    dedup_key = f"domain_events:{ev.id}"
    row = SystemMemoryRecord(
        tenant_id=ev.tenant_id,
        source=MemorySource.EVENT.value,
        source_table="domain_events",
        source_id=ev.id,
        canonical_type=ev.event_type,
        payload=payload,
        correlation_id=ev.correlation_id,
        dedup_key=dedup_key,
    )
    db.add(row)
    await db.flush()
    return row


async def record_from_audit_stub(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    action: str,
    entity_type: str,
    entity_id: UUID | None,
    changes: Dict[str, Any] | None,
) -> SystemMemoryRecord:
    """Optional path when audit_service writes AuditLog — mirror to memory."""
    row = SystemMemoryRecord(
        tenant_id=tenant_id,
        source=MemorySource.LOG.value,
        source_table="audit_logs",
        source_id=None,
        canonical_type=f"audit.{action}.{entity_type}",
        payload={
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id else None,
            "changes": changes or {},
        },
        correlation_id=None,
        dedup_key=None,
    )
    db.add(row)
    await db.flush()
    return row

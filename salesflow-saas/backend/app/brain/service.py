"""Central Brain Service — ingest events, memory, route agents, decisions, insights."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.brain.decision_engine import (
    load_enabled_rules,
    rule_actions_for_scores,
    score_event_payload,
    suggest_agents_for_event,
)
from app.brain.profiles import AGENT_PROFILES
from app.brain.safety import brain_safety
from app.brain.types import MemoryTier
from app.models.operations import DomainEvent
from app.models.second_brain import SystemMemoryRecord
from . import observability as brain_metrics
from app.services.operations_hub import emit_domain_event

logger = logging.getLogger("dealix.brain")

EventListener = Callable[[DomainEvent, Dict[str, Any]], None]

_listeners: List[EventListener] = []


def register_brain_listener(fn: EventListener) -> None:
    _listeners.append(fn)


def _notify_listeners(ev: DomainEvent, envelope: Dict[str, Any]) -> None:
    for fn in _listeners:
        try:
            fn(ev, envelope)
        except Exception:
            logger.exception("brain_listener_failed")


async def ingest_event(
    db: AsyncSession,
    *,
    tenant_id: UUID,
    event_type: str,
    payload: Dict[str, Any],
    source: str = "brain",
    correlation_id: Optional[str] = None,
    memory_tier: MemoryTier = MemoryTier.SYSTEM,
    user_id: Optional[UUID] = None,
) -> Dict[str, Any]:
    """
    Primary entry: persists DomainEvent (→ unified memory via mirror), scores, rules, routing.
    Does not auto-run LLM unless caller dispatches Celery separately.
    """
    if not brain_safety.allow(tenant_id):
        brain_metrics.record_rate_limited()
        return {"status": "rate_limited", "detail": "tenant_event_budget_exceeded"}

    ev = await emit_domain_event(
        db,
        tenant_id=tenant_id,
        event_type=event_type,
        payload=payload,
        source=source,
        correlation_id=correlation_id,
    )

    scores = score_event_payload(event_type, payload)
    rules = await load_enabled_rules(db, tenant_id)
    actions = rule_actions_for_scores(scores, rules)
    agents = suggest_agents_for_event(event_type, scores)
    agents_sorted = sorted(agents, key=lambda k: AGENT_PROFILES[k].priority)

    envelope = {
        "domain_event_id": str(ev.id),
        "event_type": event_type,
        "scores": asdict(scores),
        "rule_actions": actions,
        "suggested_agents": agents_sorted,
        "memory_tier": memory_tier.value,
    }
    brain_metrics.record_event_ingested()
    _notify_listeners(ev, envelope)

    # Optional user-scoped memory row (tier tag in payload via extra ingest — second write)
    if user_id and memory_tier == MemoryTier.USER:
        await _tag_user_memory(db, tenant_id, ev, user_id, payload)

    return {"status": "ok", **envelope}


async def _tag_user_memory(
    db: AsyncSession,
    tenant_id: UUID,
    ev: DomainEvent,
    user_id: UUID,
    payload: Dict[str, Any],
) -> None:
    row = SystemMemoryRecord(
        tenant_id=tenant_id,
        source="user_action",
        source_table="domain_events",
        source_id=ev.id,
        canonical_type=f"user_memory.{ev.event_type}",
        payload={**payload, "_memory_tier": MemoryTier.USER.value, "_user_id": str(user_id)},
        correlation_id=ev.correlation_id,
        dedup_key=f"user_mem:{user_id}:{ev.id}",
    )
    db.add(row)
    await db.flush()


def brain_health_snapshot() -> Dict[str, Any]:
    from app.services.agent_framework_report import build_agent_framework_report

    try:
        fw = build_agent_framework_report()
    except Exception as exc:  # noqa: BLE001
        fw = {"error": str(exc)}
    return {
        "component": "central_brain",
        "agent_framework": fw,
        "listeners_registered": len(_listeners),
    }

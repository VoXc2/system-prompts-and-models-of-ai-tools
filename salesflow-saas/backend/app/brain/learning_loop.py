"""Daily learning loop — aggregates + self-improvement suggestions (extends existing flow)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.second_brain import LearningMetricSnapshot, SelfImprovementSuggestion


async def run_daily_learning_snapshot(db: AsyncSession, tenant_id: UUID) -> Dict[str, Any]:
    """Persist coarse metrics for Phase 8 — replace with real SQL aggregates later."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=1)
    key = "brain.daily.health"
    row = LearningMetricSnapshot(
        tenant_id=tenant_id,
        period_start=start,
        period_end=now,
        metric_key=key,
        dimensions={"source": "brain_learning_loop"},
        value={"status": "placeholder", "note": "wire to dashboard SQL"},
    )
    db.add(row)

    sug = SelfImprovementSuggestion(
        tenant_id=tenant_id,
        category="optimization",
        title="Brain learning loop executed",
        detail={"period": "24h", "generated_at": now.isoformat()},
        severity=1,
        status="pending",
    )
    db.add(sug)
    await db.flush()
    return {"status": "ok", "metric_key": key, "suggestion_id": str(sug.id)}


async def connect_self_improvement_signals(tenant_id: str, bottlenecks: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Bridge to existing DurableTaskFlow — called from Celery beat."""
    from app.flows.self_improvement_flow import self_improvement_flow
    from app.ai.evolution.signals import evolution_signals_for_flow

    payload = {
        "signals": evolution_signals_for_flow(),
        "bottlenecks": bottlenecks,
    }
    return self_improvement_flow.run(tenant_id, payload)

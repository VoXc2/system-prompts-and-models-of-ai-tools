"""Record upgrade cycles; optional mirror to SystemMemoryRecord when platform tenant is configured."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.second_brain import MemorySource, SystemMemoryRecord
from app.models.upgrade_director import UpgradeCandidateRecord, UpgradeDirectorCycle


async def start_cycle(
    db: AsyncSession,
    *,
    source: str = "manual",
    local_scan: Optional[Dict[str, Any]] = None,
) -> UpgradeDirectorCycle:
    now = datetime.now(timezone.utc)
    row = UpgradeDirectorCycle(
        status="draft",
        source=source,
        cycle_started_at=now,
        phases={"1_scan": "started", "12_summary": "pending"},
        local_scan_snapshot=local_scan,
    )
    db.add(row)
    await db.flush()
    return row


async def complete_cycle(
    db: AsyncSession,
    *,
    cycle_id: UUID,
    machine_summary: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    executive_text: str,
    next_focus: List[str],
    platform_tenant_id: Optional[UUID] = None,
) -> UpgradeDirectorCycle:
    q = await db.execute(select(UpgradeDirectorCycle).where(UpgradeDirectorCycle.id == cycle_id))
    cycle = q.scalar_one_or_none()
    if not cycle:
        raise ValueError("cycle_not_found")

    now = datetime.now(timezone.utc)
    cycle.status = "completed"
    cycle.cycle_completed_at = now
    cycle.machine_summary = machine_summary
    cycle.executive_summary = executive_text
    cycle.next_cycle_focus = next_focus
    cycle.phases = {
        **(cycle.phases or {}),
        "9_decision": "recorded",
        "10_merge": "recorded",
        "11_memory": "recorded" if platform_tenant_id else "skipped_no_platform_tenant",
        "12_summary": "completed",
    }

    for c in candidates:
        rec = UpgradeCandidateRecord(
            cycle_id=cycle.id,
            name=str(c.get("name", "unknown"))[:200],
            category=c.get("category"),
            version=c.get("version"),
            release_date=c.get("release_date"),
            official_source=c.get("official_source"),
            payload=c,
            recommended_action=str(c.get("recommended_action", "watchlist"))[:32],
            weighted_score=str(c.get("weighted_total", c.get("weighted_score", "")))[:32]
            if c.get("weighted_total") is not None or c.get("weighted_score") is not None
            else None,
            confidence=str(c.get("confidence", ""))[:32] if c.get("confidence") is not None else None,
            decision_reason=c.get("decision_reason"),
        )
        db.add(rec)

    if platform_tenant_id:
        mem = SystemMemoryRecord(
            tenant_id=platform_tenant_id,
            source=MemorySource.REPORT.value,
            source_table="upgrade_director_cycles",
            source_id=cycle.id,
            canonical_type="upgrade_director.cycle_completed",
            payload={
                "cycle_id": str(cycle.id),
                "completed_at": now.isoformat(),
                "candidate_count": len(candidates),
                "machine_summary": machine_summary,
            },
            correlation_id=None,
            dedup_key=f"upgrade_cycle:{cycle.id}",
        )
        db.add(mem)

    await db.flush()
    return cycle


async def list_recent_cycles(db: AsyncSession, *, limit: int = 24) -> List[UpgradeDirectorCycle]:
    q = await db.execute(
        select(UpgradeDirectorCycle).order_by(desc(UpgradeDirectorCycle.created_at)).limit(limit)
    )
    return list(q.scalars().all())


async def record_automated_hourly_scan(
    db: AsyncSession,
    *,
    local_scan: Dict[str, Any],
    platform_tenant_id: Optional[UUID] = None,
) -> UpgradeDirectorCycle:
    """Completed cycle with phase-1 only (local deps). No external network."""
    now = datetime.now(timezone.utc)
    machine_summary = {
        "cycle_timestamp": now.isoformat(),
        "top_opportunities": [],
        "adopted_today": [],
        "rejected_today": [],
        "watchlist": [],
        "system_memory_updates": [
            {"type": "local_dependency_snapshot", "keys": list(local_scan.keys())},
        ],
        "next_cycle_focus": [
            "Attach official release notes for pinned majors (FastAPI, Next, Celery).",
            "Run human Phases 3–8 before any staging integration.",
        ],
        "note": "Automated: local filesystem snapshot only. No hype, no network.",
    }
    cycle = UpgradeDirectorCycle(
        status="completed",
        source="hourly_celery",
        cycle_started_at=now,
        cycle_completed_at=now,
        phases={
            "1_scan": {"completed": True, "evidence": "requirements.txt + package.json"},
            "2_filter": "deferred_manual",
            "3_research": "deferred_manual",
            "12_summary": "completed_automated_minimal",
        },
        local_scan_snapshot=local_scan,
        executive_summary="Hourly automated local dependency snapshot. Research phases require human/CI.",
        machine_summary=machine_summary,
        next_cycle_focus=machine_summary["next_cycle_focus"],
    )
    db.add(cycle)
    await db.flush()
    if platform_tenant_id:
        db.add(
            SystemMemoryRecord(
                tenant_id=platform_tenant_id,
                source=MemorySource.REPORT.value,
                source_table="upgrade_director_cycles",
                source_id=cycle.id,
                canonical_type="upgrade_director.hourly_scan",
                payload={
                    "cycle_id": str(cycle.id),
                    "local_scan_snapshot": local_scan,
                    "machine_summary": machine_summary,
                },
                dedup_key=f"upgrade_hourly:{now.date().isoformat()}:{now.hour}",
            )
        )
        await db.flush()
    return cycle

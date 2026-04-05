"""
Autonomous Upgrade Director — admin API to record research cycles (no live web scan in-process).

Human or CI posts candidates + machine summary after Phases 3–9 offline.
"""

from __future__ import annotations

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.services.upgrade_director import (
    collect_local_dependency_snapshot,
    complete_cycle,
    list_recent_cycles,
    start_cycle,
)

router = APIRouter(prefix="/upgrade-director")


class CompleteCycleBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    machine_summary: dict[str, Any]
    candidates: List[dict[str, Any]] = Field(
        default_factory=list,
        description="Full objects matching docs/schemas/upgrade-candidate.schema.json",
    )
    executive_summary: str = ""
    next_cycle_focus: List[str] = Field(default_factory=list)


@router.get("/local-snapshot")
async def get_local_snapshot(
    _: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    return collect_local_dependency_snapshot()


@router.post("/cycles/start")
async def post_start_cycle(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    snap = collect_local_dependency_snapshot()
    c = await start_cycle(db, source="manual", local_scan=snap)
    return {"cycle_id": str(c.id), "status": c.status}


@router.post("/cycles/{cycle_id}/complete")
async def post_complete_cycle(
    cycle_id: UUID,
    body: CompleteCycleBody,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    settings = get_settings()
    pt = (settings.DEALIX_PLATFORM_TENANT_ID or "").strip()
    platform_uuid = UUID(pt) if pt else None
    try:
        await complete_cycle(
            db,
            cycle_id=cycle_id,
            machine_summary=body.machine_summary,
            candidates=body.candidates,
            executive_text=body.executive_summary,
            next_focus=body.next_cycle_focus,
            platform_tenant_id=platform_uuid,
        )
        await db.commit()
    except ValueError:
        raise HTTPException(404, detail="cycle_not_found") from None
    return {"status": "completed", "cycle_id": str(cycle_id)}


@router.get("/cycles")
async def get_cycles(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
    limit: int = 24,
) -> dict[str, Any]:
    rows = await list_recent_cycles(db, limit=min(limit, 100))
    return {
        "cycles": [
            {
                "id": str(r.id),
                "status": r.status,
                "source": r.source,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "cycle_completed_at": r.cycle_completed_at.isoformat() if r.cycle_completed_at else None,
                "has_machine_summary": r.machine_summary is not None,
            }
            for r in rows
        ]
    }


@router.get("/cycles/{cycle_id}")
async def get_cycle_detail(
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
) -> dict[str, Any]:
    from sqlalchemy import select
    from app.models.upgrade_director import UpgradeCandidateRecord, UpgradeDirectorCycle

    q = await db.execute(select(UpgradeDirectorCycle).where(UpgradeDirectorCycle.id == cycle_id))
    c = q.scalar_one_or_none()
    if not c:
        raise HTTPException(404, detail="not_found")
    q2 = await db.execute(select(UpgradeCandidateRecord).where(UpgradeCandidateRecord.cycle_id == cycle_id))
    cands = q2.scalars().all()
    return {
        "id": str(c.id),
        "status": c.status,
        "source": c.source,
        "phases": c.phases,
        "local_scan_snapshot": c.local_scan_snapshot,
        "executive_summary": c.executive_summary,
        "machine_summary": c.machine_summary,
        "next_cycle_focus": c.next_cycle_focus,
        "candidates": [{"name": x.name, "payload": x.payload, "action": x.recommended_action} for x in cands],
    }

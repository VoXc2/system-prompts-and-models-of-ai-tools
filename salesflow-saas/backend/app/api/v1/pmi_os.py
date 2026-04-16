"""PMI / Strategic PMO OS — API routes for post-merger integration."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database import get_db
from app.models.pmi import PMIProgram, PMIWorkstream, PMIMilestone, PMIRisk
from app.schemas.sovereign import PMIProgramCreate, PMIProgramResponse

router = APIRouter(prefix="/pmi", tags=["PMI OS — تكامل ما بعد الاستحواذ"])


@router.get("/programs", response_model=list[PMIProgramResponse])
async def list_programs(
    status: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List PMI programs."""
    q = select(PMIProgram)
    if status:
        q = q.where(PMIProgram.status == status)
    q = q.order_by(PMIProgram.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/programs", response_model=PMIProgramResponse, status_code=201)
async def create_program(
    data: PMIProgramCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new PMI program."""
    program = PMIProgram(**data.model_dump())
    program.tenant_id = "00000000-0000-0000-0000-000000000001"
    db.add(program)
    await db.flush()
    await db.refresh(program)
    return program


@router.get("/programs/{program_id}", response_model=PMIProgramResponse)
async def get_program(program_id: str, db: AsyncSession = Depends(get_db)):
    """Get PMI program details."""
    result = await db.execute(select(PMIProgram).where(PMIProgram.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="PMI Program not found")
    return program


@router.get("/programs/{program_id}/workstreams")
async def list_workstreams(program_id: str, db: AsyncSession = Depends(get_db)):
    """List workstreams in a PMI program."""
    q = select(PMIWorkstream).where(PMIWorkstream.program_id == program_id)
    result = await db.execute(q)
    streams = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "name_ar": s.name_ar,
            "status": s.status,
            "progress_pct": s.progress_pct,
            "owner_id": str(s.owner_id) if s.owner_id else None,
        }
        for s in streams
    ]


@router.get("/programs/{program_id}/milestones")
async def list_milestones(program_id: str, db: AsyncSession = Depends(get_db)):
    """List milestones (30/60/90) for a PMI program."""
    q = select(PMIMilestone).where(
        PMIMilestone.program_id == program_id
    ).order_by(PMIMilestone.target_date)
    result = await db.execute(q)
    milestones = result.scalars().all()
    return [
        {
            "id": str(m.id),
            "name": m.name,
            "name_ar": m.name_ar,
            "milestone_type": m.milestone_type,
            "status": m.status,
            "target_date": m.target_date.isoformat() if m.target_date else None,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None,
        }
        for m in milestones
    ]


@router.get("/programs/{program_id}/risks")
async def list_risks(program_id: str, db: AsyncSession = Depends(get_db)):
    """List risk register for a PMI program."""
    q = select(PMIRisk).where(PMIRisk.program_id == program_id)
    result = await db.execute(q)
    risks = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "title_ar": r.title_ar,
            "severity": r.severity,
            "probability": r.probability,
            "status": r.status,
        }
        for r in risks
    ]


@router.get("/dashboard")
async def pmi_dashboard(db: AsyncSession = Depends(get_db)):
    """PMI OS dashboard summary."""
    total = await db.execute(select(func.count(PMIProgram.id)))
    active = await db.execute(
        select(func.count(PMIProgram.id)).where(PMIProgram.status.in_(["day1_active", "integration"]))
    )
    return {
        "total_programs": total.scalar() or 0,
        "active": active.scalar() or 0,
        "module": "pmi_strategic_pmo",
        "module_ar": "نظام إدارة التكامل الاستراتيجي",
    }

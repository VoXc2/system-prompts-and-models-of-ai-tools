"""PMI/PMO OS API — Day-1 readiness, 30/60/90 plans, risk register, synergy tracking."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.sovereign import PMIProgram, PMITask

router = APIRouter(prefix="/pmi-os", tags=["PMI/PMO OS — نظام التكامل بعد الاستحواذ"])


class PMIProgramCreate(BaseModel):
    name_ar: str
    name_en: str | None = None
    ma_target_id: str | None = None
    synergy_target_sar: float | None = None
    day1_checklist: list[dict] | None = None
    plan_30: list[dict] | None = None
    plan_60: list[dict] | None = None
    plan_90: list[dict] | None = None
    risk_register: list[dict] | None = None


class PMITaskCreate(BaseModel):
    phase: str
    title_ar: str
    title_en: str | None = None
    owner_id: str | None = None
    due_date: datetime | None = None
    dependency_ids: list[str] | None = None


class PMITaskUpdate(BaseModel):
    status: str
    escalated: bool | None = None


@router.post("/programs", status_code=status.HTTP_201_CREATED)
async def create_program(
    tenant_id: str,
    payload: PMIProgramCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    program = PMIProgram(
        tenant_id=tenant_id,
        name_ar=payload.name_ar,
        name_en=payload.name_en,
        ma_target_id=payload.ma_target_id,
        synergy_target_sar=payload.synergy_target_sar,
        day1_checklist=payload.day1_checklist or [],
        plan_30=payload.plan_30 or [],
        plan_60=payload.plan_60 or [],
        plan_90=payload.plan_90 or [],
        risk_register=payload.risk_register or [],
    )
    db.add(program)
    await db.commit()
    await db.refresh(program)
    return {"id": str(program.id), "name_ar": program.name_ar, "status": program.status}


@router.get("/programs")
async def list_programs(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(PMIProgram).where(PMIProgram.tenant_id == tenant_id)
        .order_by(PMIProgram.created_at.desc())
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "name_ar": r.name_ar,
            "name_en": r.name_en,
            "status": r.status,
            "synergy_realized_sar": float(r.synergy_realized_sar) if r.synergy_realized_sar else None,
            "synergy_target_sar": float(r.synergy_target_sar) if r.synergy_target_sar else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/programs/{program_id}")
async def get_program(
    program_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(PMIProgram).where(
            PMIProgram.id == program_id,
            PMIProgram.tenant_id == tenant_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="PMI program not found")

    tasks_result = await db.execute(
        select(PMITask).where(PMITask.program_id == program_id, PMITask.tenant_id == tenant_id)
        .order_by(PMITask.due_date.asc().nullslast())
    )
    tasks = tasks_result.scalars().all()

    return {
        "id": str(p.id),
        "name_ar": p.name_ar,
        "name_en": p.name_en,
        "status": p.status,
        "day1_checklist": p.day1_checklist,
        "plan_30": p.plan_30,
        "plan_60": p.plan_60,
        "plan_90": p.plan_90,
        "risk_register": p.risk_register,
        "synergy_realized_sar": float(p.synergy_realized_sar) if p.synergy_realized_sar else None,
        "synergy_target_sar": float(p.synergy_target_sar) if p.synergy_target_sar else None,
        "tasks": [
            {
                "id": str(t.id),
                "phase": t.phase,
                "title_ar": t.title_ar,
                "status": t.status,
                "escalated": t.escalated,
                "due_date": t.due_date.isoformat() if t.due_date else None,
            }
            for t in tasks
        ],
    }


@router.post("/programs/{program_id}/tasks", status_code=status.HTTP_201_CREATED)
async def add_task(
    program_id: str,
    tenant_id: str,
    payload: PMITaskCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    task = PMITask(
        tenant_id=tenant_id,
        program_id=program_id,
        phase=payload.phase,
        title_ar=payload.title_ar,
        title_en=payload.title_en,
        owner_id=payload.owner_id,
        due_date=payload.due_date,
        dependency_ids=payload.dependency_ids or [],
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {"id": str(task.id), "status": task.status}


@router.patch("/tasks/{task_id}")
async def update_task(
    task_id: str,
    tenant_id: str,
    payload: PMITaskUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(PMITask).where(PMITask.id == task_id, PMITask.tenant_id == tenant_id)
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    t.status = payload.status
    if payload.escalated is not None:
        t.escalated = payload.escalated
    await db.commit()
    return {"id": task_id, "status": t.status, "escalated": t.escalated}

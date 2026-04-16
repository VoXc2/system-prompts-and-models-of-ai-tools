"""Sovereign PMI/PMO OS: post-merger integration programs and tasks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_pmi import PMIProgram, PMITask
from app.schemas.sovereign import (
    PMIProgramCreate,
    PMIProgramResponse,
    PMITaskCreate,
    PMITaskResponse,
)

router = APIRouter(prefix="/sovereign/pmi", tags=["Sovereign PMI/PMO OS"])


class TaskStatusUpdate(BaseModel):
    status: str


@router.post("/programs", response_model=PMIProgramResponse, status_code=201)
async def create_program(
    data: PMIProgramCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    program = PMIProgram(
        tenant_id=current_user.tenant_id,
        owner_id=current_user.id,
        **data.model_dump(exclude_none=True),
    )
    db.add(program)
    await db.flush()
    await db.refresh(program)
    return PMIProgramResponse.model_validate(program)


@router.get("/programs", response_model=List[PMIProgramResponse])
async def list_programs(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(PMIProgram).where(PMIProgram.tenant_id == current_user.tenant_id)
    if status:
        q = q.where(PMIProgram.status == status)
    q = q.order_by(PMIProgram.created_at.desc())
    result = await db.execute(q)
    return [PMIProgramResponse.model_validate(p) for p in result.scalars().all()]


@router.get("/programs/{id}", response_model=PMIProgramResponse)
async def get_program(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PMIProgram).where(
            PMIProgram.id == id,
            PMIProgram.tenant_id == current_user.tenant_id,
        )
    )
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    tasks_q = await db.execute(
        select(PMITask)
        .where(PMITask.program_id == id)
        .order_by(PMITask.created_at)
    )
    tasks = [PMITaskResponse.model_validate(t) for t in tasks_q.scalars().all()]

    resp = PMIProgramResponse.model_validate(program).model_dump()
    resp["tasks"] = [t.model_dump() for t in tasks]
    return resp


@router.post("/tasks", response_model=PMITaskResponse, status_code=201)
async def create_task(
    data: PMITaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    prog_q = await db.execute(
        select(PMIProgram).where(
            PMIProgram.id == data.program_id,
            PMIProgram.tenant_id == current_user.tenant_id,
        )
    )
    if not prog_q.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Program not found")

    task = PMITask(
        tenant_id=current_user.tenant_id,
        **data.model_dump(exclude_none=True),
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return PMITaskResponse.model_validate(task)


@router.patch("/tasks/{id}/status", response_model=PMITaskResponse)
async def update_task_status(
    id: UUID,
    data: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(PMITask).where(PMITask.id == id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = data.status
    if data.status == "completed":
        task.completed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(task)
    return PMITaskResponse.model_validate(task)


@router.get("/engine")
async def pmi_engine(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """PMI 30/60/90 engine: programs with task breakdown by phase."""
    tid = current_user.tenant_id
    programs_q = await db.execute(
        select(PMIProgram).where(PMIProgram.tenant_id == tid)
    )
    programs = programs_q.scalars().all()

    engine_data = []
    for prog in programs:
        tasks_q = await db.execute(
            select(PMITask).where(PMITask.program_id == prog.id)
        )
        tasks = tasks_q.scalars().all()
        by_phase: dict = {}
        for t in tasks:
            phase_entry = by_phase.setdefault(t.phase, {"total": 0, "completed": 0, "pending": 0})
            phase_entry["total"] += 1
            if t.status == "completed":
                phase_entry["completed"] += 1
            else:
                phase_entry["pending"] += 1

        engine_data.append({
            "program": PMIProgramResponse.model_validate(prog).model_dump(),
            "phases": by_phase,
            "total_tasks": len(tasks),
            "completed_tasks": sum(1 for t in tasks if t.status == "completed"),
        })

    return {"programs": engine_data}

"""Sovereign Execution Plane: durable workflows and steps."""

from __future__ import annotations

import uuid as _uuid
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_execution import DurableWorkflow, WorkflowStep
from app.schemas.sovereign import (
    DurableWorkflowCreate,
    DurableWorkflowResponse,
    DurableWorkflowUpdate,
    WorkflowStepCreate,
    WorkflowStepResponse,
    WorkflowStepUpdate,
)

router = APIRouter(prefix="/sovereign/execution", tags=["Sovereign Execution Plane"])


@router.post("/workflows", response_model=DurableWorkflowResponse, status_code=201)
async def create_workflow(
    data: DurableWorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    wf = DurableWorkflow(
        tenant_id=current_user.tenant_id,
        initiator_id=current_user.id,
        idempotency_key=str(_uuid.uuid4()),
        **data.model_dump(exclude_none=True),
    )
    db.add(wf)
    await db.flush()
    await db.refresh(wf)
    return DurableWorkflowResponse.model_validate(wf)


@router.get("/workflows", response_model=List[DurableWorkflowResponse])
async def list_workflows(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(DurableWorkflow).where(DurableWorkflow.tenant_id == current_user.tenant_id)
    if status:
        q = q.where(DurableWorkflow.status == status)
    q = q.order_by(DurableWorkflow.created_at.desc())
    result = await db.execute(q)
    return [DurableWorkflowResponse.model_validate(w) for w in result.scalars().all()]


@router.get("/workflows/{id}", response_model=DurableWorkflowResponse)
async def get_workflow(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DurableWorkflow).where(
            DurableWorkflow.id == id,
            DurableWorkflow.tenant_id == current_user.tenant_id,
        )
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    steps_q = await db.execute(
        select(WorkflowStep)
        .where(WorkflowStep.workflow_id == id)
        .order_by(WorkflowStep.step_order)
    )
    steps = [WorkflowStepResponse.model_validate(s) for s in steps_q.scalars().all()]

    resp = DurableWorkflowResponse.model_validate(wf).model_dump()
    resp["steps"] = [s.model_dump() for s in steps]
    return resp


@router.patch("/workflows/{id}/status", response_model=DurableWorkflowResponse)
async def update_workflow_status(
    id: UUID,
    data: DurableWorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DurableWorkflow).where(
            DurableWorkflow.id == id,
            DurableWorkflow.tenant_id == current_user.tenant_id,
        )
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(wf, field, value)
    if data.status == "completed":
        wf.completed_at = datetime.now(timezone.utc)
    elif data.status == "failed":
        wf.failed_at = datetime.now(timezone.utc)
    elif data.status == "running" and not wf.started_at:
        wf.started_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(wf)
    return DurableWorkflowResponse.model_validate(wf)


@router.post("/workflows/{id}/steps", response_model=WorkflowStepResponse, status_code=201)
async def add_workflow_step(
    id: UUID,
    data: WorkflowStepCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DurableWorkflow).where(
            DurableWorkflow.id == id,
            DurableWorkflow.tenant_id == current_user.tenant_id,
        )
    )
    wf = result.scalar_one_or_none()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    max_order_q = await db.execute(
        select(func.coalesce(func.max(WorkflowStep.step_order), 0))
        .where(WorkflowStep.workflow_id == id)
    )
    next_order = (max_order_q.scalar() or 0) + 1

    step = WorkflowStep(
        tenant_id=current_user.tenant_id,
        workflow_id=id,
        step_order=next_order,
        **data.model_dump(exclude_none=True),
    )
    db.add(step)
    wf.total_steps = next_order
    await db.flush()
    await db.refresh(step)
    return WorkflowStepResponse.model_validate(step)


@router.patch("/steps/{id}/status", response_model=WorkflowStepResponse)
async def update_step_status(
    id: UUID,
    data: WorkflowStepUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WorkflowStep).where(WorkflowStep.id == id)
    )
    step = result.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(step, field, value)
    if data.status == "completed":
        step.completed_at = datetime.now(timezone.utc)
    elif data.status == "running" and not step.started_at:
        step.started_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(step)
    return WorkflowStepResponse.model_validate(step)

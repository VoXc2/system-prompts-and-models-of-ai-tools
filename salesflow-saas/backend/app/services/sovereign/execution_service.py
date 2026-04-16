"""Sovereign Execution Plane — Durable workflows and workflow steps."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class ExecutionService:
    """Manages durable workflows and their execution steps."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Workflows ──────────────────────────────────

    async def create_workflow(
        self,
        tenant_id: str,
        data: dict,
        initiator_id: str,
    ) -> "DurableWorkflow":
        from app.models.sovereign_execution import DurableWorkflow

        workflow = DurableWorkflow(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            workflow_type=data["workflow_type"],
            title=data["title"],
            title_ar=data.get("title_ar"),
            status=data.get("status", "pending"),
            current_step=data.get("current_step"),
            total_steps=data.get("total_steps", 0),
            completed_steps=0,
            idempotency_key=data.get("idempotency_key", str(uuid.uuid4())),
            is_resumable=data.get("is_resumable", True),
            is_compensatable=data.get("is_compensatable", True),
            compensation_plan=data.get("compensation_plan"),
            checkpoint_data=data.get("checkpoint_data"),
            initiator_id=uuid.UUID(initiator_id),
            target_entity_type=data.get("target_entity_type"),
            target_entity_id=uuid.UUID(data["target_entity_id"]) if data.get("target_entity_id") else None,
            timeout_seconds=data.get("timeout_seconds"),
            retry_count=0,
            max_retries=data.get("max_retries", 3),
            correlation_id=data.get("correlation_id", str(uuid.uuid4())),
        )
        self.db.add(workflow)
        await self.db.flush()
        return workflow

    async def list_workflows(
        self,
        tenant_id: str,
        status_filter: Optional[str] = None,
    ) -> list:
        from app.models.sovereign_execution import DurableWorkflow

        query = select(DurableWorkflow).where(
            DurableWorkflow.tenant_id == uuid.UUID(tenant_id),
        )
        if status_filter:
            query = query.where(DurableWorkflow.status == status_filter)

        query = query.order_by(DurableWorkflow.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_workflow(
        self, tenant_id: str, workflow_id: str,
    ) -> Optional["DurableWorkflow"]:
        from app.models.sovereign_execution import DurableWorkflow

        result = await self.db.execute(
            select(DurableWorkflow)
            .options(selectinload(DurableWorkflow.steps))
            .where(
                DurableWorkflow.id == uuid.UUID(workflow_id),
                DurableWorkflow.tenant_id == uuid.UUID(tenant_id),
            )
        )
        return result.scalar_one_or_none()

    async def update_workflow_status(
        self,
        tenant_id: str,
        workflow_id: str,
        status: str,
    ) -> Optional["DurableWorkflow"]:
        from app.models.sovereign_execution import DurableWorkflow

        result = await self.db.execute(
            select(DurableWorkflow).where(
                DurableWorkflow.id == uuid.UUID(workflow_id),
                DurableWorkflow.tenant_id == uuid.UUID(tenant_id),
            )
        )
        workflow = result.scalar_one_or_none()
        if not workflow:
            return None

        workflow.status = status
        workflow.updated_at = datetime.now(timezone.utc)

        if status == "running" and not workflow.started_at:
            workflow.started_at = datetime.now(timezone.utc)
        elif status == "completed":
            workflow.completed_at = datetime.now(timezone.utc)
        elif status == "failed":
            workflow.failed_at = datetime.now(timezone.utc)

        await self.db.flush()
        return workflow

    # ── Steps ──────────────────────────────────────

    async def add_workflow_step(
        self,
        tenant_id: str,
        workflow_id: str,
        step_data: dict,
    ) -> "WorkflowStep":
        from app.models.sovereign_execution import DurableWorkflow, WorkflowStep

        wf_result = await self.db.execute(
            select(DurableWorkflow).where(
                DurableWorkflow.id == uuid.UUID(workflow_id),
                DurableWorkflow.tenant_id == uuid.UUID(tenant_id),
            )
        )
        workflow = wf_result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found for tenant {tenant_id}")

        step = WorkflowStep(
            id=uuid.uuid4(),
            tenant_id=uuid.UUID(tenant_id),
            workflow_id=uuid.UUID(workflow_id),
            step_order=step_data.get("step_order", workflow.total_steps + 1),
            step_name=step_data["step_name"],
            step_type=step_data["step_type"],
            status=step_data.get("status", "pending"),
            input_data=step_data.get("input_data"),
            assigned_to_id=uuid.UUID(step_data["assigned_to_id"]) if step_data.get("assigned_to_id") else None,
        )
        self.db.add(step)

        workflow.total_steps = workflow.total_steps + 1
        workflow.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        return step

    async def update_step_status(
        self,
        tenant_id: str,
        step_id: str,
        status: str,
        output_data: Optional[dict] = None,
    ) -> Optional["WorkflowStep"]:
        from app.models.sovereign_execution import WorkflowStep, DurableWorkflow

        result = await self.db.execute(
            select(WorkflowStep).where(
                WorkflowStep.id == uuid.UUID(step_id),
                WorkflowStep.tenant_id == uuid.UUID(tenant_id),
            )
        )
        step = result.scalar_one_or_none()
        if not step:
            return None

        step.status = status
        if output_data is not None:
            step.output_data = output_data

        now = datetime.now(timezone.utc)
        if status == "running" and not step.started_at:
            step.started_at = now
        elif status in ("completed", "failed"):
            step.completed_at = now

        if status == "completed":
            wf_result = await self.db.execute(
                select(DurableWorkflow).where(
                    DurableWorkflow.id == step.workflow_id,
                    DurableWorkflow.tenant_id == uuid.UUID(tenant_id),
                )
            )
            workflow = wf_result.scalar_one_or_none()
            if workflow:
                workflow.completed_steps = workflow.completed_steps + 1
                workflow.updated_at = now

        await self.db.flush()
        return step

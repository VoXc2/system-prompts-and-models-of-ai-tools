"""Execution Plane — durable workflows and business commitments."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger("dealix.sovereign.execution_plane")


class WorkflowState(StrEnum):
    """Lifecycle states for durable workflows."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED_FOR_APPROVAL = "PAUSED_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"


class DurableWorkflowStatus(BaseModel):
    """Observable status of a sovereign durable workflow."""

    workflow_id: str
    state: WorkflowState
    started_at: datetime
    last_checkpoint_at: datetime | None = None
    idempotency_key: str | None = None
    is_resumable: bool = True
    is_compensatable: bool = True
    observable_url: str | None = Field(
        default=None,
        description="URL or deep link to workflow observability UI",
    )


class WorkflowRegistrationResult(BaseModel):
    """Outcome of registering a Temporal workflow type."""

    workflow_name: str
    registered: bool
    message_en: str
    message_ar: str


class CompensationResult(BaseModel):
    """Result of a compensation saga step."""

    workflow_id: str
    success: bool
    detail_en: str
    detail_ar: str


class PauseForApprovalResult(BaseModel):
    """Result when a workflow pauses for human approval."""

    workflow_id: str
    state: WorkflowState = WorkflowState.PAUSED_FOR_APPROVAL
    message_en: str
    message_ar: str


class ExecutionPlaneEngine:
    """Async stubs for durable execution (Temporal-oriented)."""

    def __init__(self) -> None:
        self._workflows: dict[str, DurableWorkflowStatus] = {}
        self._idempotency: dict[tuple[str, str], str] = {}

    async def start_workflow(
        self,
        tenant_id: str,
        workflow_type: str,
        payload: dict[str, Any],
        approval_class: str,
    ) -> str:
        logger.info(
            "execution_plane.start_workflow tenant_id=%s type=%s approval_class=%s",
            tenant_id,
            workflow_type,
            approval_class,
        )
        _ = payload
        workflow_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        self._workflows[workflow_id] = DurableWorkflowStatus(
            workflow_id=workflow_id,
            state=WorkflowState.RUNNING,
            started_at=now,
            last_checkpoint_at=now,
            idempotency_key=None,
            is_resumable=True,
            is_compensatable=True,
            observable_url=f"/sovereign/workflows/{tenant_id}/{workflow_id}",
        )
        return workflow_id

    async def resume_workflow(self, tenant_id: str, workflow_id: str) -> WorkflowState:
        logger.info(
            "execution_plane.resume_workflow tenant_id=%s workflow_id=%s",
            tenant_id,
            workflow_id,
        )
        wf = self._workflows.get(workflow_id)
        if not wf:
            return WorkflowState.FAILED
        if wf.state == WorkflowState.PAUSED_FOR_APPROVAL:
            wf.state = WorkflowState.RUNNING
            wf.last_checkpoint_at = datetime.now(UTC)
        return wf.state

    async def compensate(
        self,
        tenant_id: str,
        workflow_id: str,
        reason: str,
    ) -> CompensationResult:
        logger.info(
            "execution_plane.compensate tenant_id=%s workflow_id=%s reason=%s",
            tenant_id,
            workflow_id,
            reason,
        )
        wf = self._workflows.get(workflow_id)
        if wf:
            wf.state = WorkflowState.COMPENSATING
            wf.last_checkpoint_at = datetime.now(UTC)
            wf.state = WorkflowState.COMPENSATED
        return CompensationResult(
            workflow_id=workflow_id,
            success=True,
            detail_en="Stub compensation completed.",
            detail_ar="اكتمل التعويض التجريبي.",
        )

    async def get_workflow_status(
        self,
        tenant_id: str,
        workflow_id: str,
    ) -> DurableWorkflowStatus:
        logger.info(
            "execution_plane.get_workflow_status tenant_id=%s workflow_id=%s",
            tenant_id,
            workflow_id,
        )
        wf = self._workflows.get(workflow_id)
        if wf:
            return wf
        now = datetime.now(UTC)
        return DurableWorkflowStatus(
            workflow_id=workflow_id,
            state=WorkflowState.PENDING,
            started_at=now,
            last_checkpoint_at=None,
            idempotency_key=None,
            is_resumable=False,
            is_compensatable=False,
            observable_url=f"/sovereign/workflows/{tenant_id}/{workflow_id}",
        )

    async def register_temporal_workflow(
        self,
        workflow_name: str,
        activity_definitions: list[dict[str, Any]],
    ) -> WorkflowRegistrationResult:
        logger.info(
            "execution_plane.register_temporal_workflow name=%s activities=%s",
            workflow_name,
            len(activity_definitions),
        )
        return WorkflowRegistrationResult(
            workflow_name=workflow_name,
            registered=True,
            message_en="Stub registration — wire to Temporal worker.",
            message_ar="تسجيل تجريبي — يُربط بعامل Temporal لاحقًا.",
        )

    async def pause_for_approval(
        self,
        tenant_id: str,
        workflow_id: str,
        approval_class: str,
        reason: str,
    ) -> PauseForApprovalResult:
        logger.info(
            "execution_plane.pause_for_approval tenant_id=%s workflow_id=%s class=%s",
            tenant_id,
            workflow_id,
            approval_class,
        )
        wf = self._workflows.get(workflow_id)
        if wf:
            wf.state = WorkflowState.PAUSED_FOR_APPROVAL
            wf.last_checkpoint_at = datetime.now(UTC)
        return PauseForApprovalResult(
            workflow_id=workflow_id,
            message_en=f"Paused for {approval_class}: {reason}",
            message_ar=f"توقف مؤقت لانتظار الموافقة ({approval_class}): {reason}",
        )

    async def mark_idempotent(
        self,
        tenant_id: str,
        workflow_id: str,
        idempotency_key: str,
    ) -> None:
        logger.info(
            "execution_plane.mark_idempotent tenant_id=%s workflow_id=%s key=%s",
            tenant_id,
            workflow_id,
            idempotency_key,
        )
        self._idempotency[(tenant_id, idempotency_key)] = workflow_id
        wf = self._workflows.get(workflow_id)
        if wf:
            wf.idempotency_key = idempotency_key
            wf.last_checkpoint_at = datetime.now(UTC)


class ExecutionPlane(ExecutionPlaneEngine):
    """Sovereign Execution Plane — public entry type."""

    pass

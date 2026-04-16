from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED_HITL = "paused_hitl"
    PAUSED_APPROVAL = "paused_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    step_type: str  # "auto", "hitl", "approval_gate", "external_call"
    status: StepStatus = StepStatus.PENDING
    approval_class: str = "R0_AUTO"
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    approved_by: str | None = None
    evidence_pack_id: str | None = None


class WorkflowDefinition(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    name_ar: str = ""
    description: str = ""
    description_ar: str = ""
    version: str = "1.0.0"
    os_module: str  # "sales", "partnership", "ma", "expansion", "pmi", "executive"
    steps: list[WorkflowStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowInstance(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    instance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    tenant_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step_index: int = 0
    steps: list[WorkflowStep] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class DurableWorkflowEngine:
    """Manages workflow lifecycle with HITL checkpoints and approval gates."""

    def __init__(self):
        self._definitions: dict[str, WorkflowDefinition] = {}
        self._instances: dict[str, WorkflowInstance] = {}

    def register_workflow(self, definition: WorkflowDefinition) -> str:
        self._definitions[definition.workflow_id] = definition
        return definition.workflow_id

    def start_workflow(
        self, workflow_id: str, tenant_id: str, context: dict | None = None
    ) -> WorkflowInstance:
        defn = self._definitions.get(workflow_id)
        if not defn:
            raise ValueError(f"Workflow {workflow_id} not registered")

        instance = WorkflowInstance(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            status=WorkflowStatus.RUNNING,
            steps=[step.model_copy() for step in defn.steps],
            context=context or {},
        )
        self._instances[instance.instance_id] = instance
        self._advance(instance)
        return instance

    def _advance(self, instance: WorkflowInstance) -> None:
        while instance.current_step_index < len(instance.steps):
            step = instance.steps[instance.current_step_index]

            if step.step_type in ("hitl", "approval_gate") and step.status == StepStatus.PENDING:
                step.status = StepStatus.WAITING_APPROVAL
                instance.status = (
                    WorkflowStatus.PAUSED_HITL
                    if step.step_type == "hitl"
                    else WorkflowStatus.PAUSED_APPROVAL
                )
                instance.updated_at = datetime.now(timezone.utc)
                return

            if step.status == StepStatus.PENDING:
                step.status = StepStatus.RUNNING
                step.started_at = datetime.now(timezone.utc)
                step.status = StepStatus.COMPLETED
                step.completed_at = datetime.now(timezone.utc)
                instance.current_step_index += 1
                continue

            if step.status in (StepStatus.COMPLETED, StepStatus.APPROVED, StepStatus.SKIPPED):
                instance.current_step_index += 1
                continue

            break

        if instance.current_step_index >= len(instance.steps):
            instance.status = WorkflowStatus.COMPLETED
            instance.completed_at = datetime.now(timezone.utc)
        instance.updated_at = datetime.now(timezone.utc)

    def approve_step(
        self,
        instance_id: str,
        step_id: str,
        approved_by: str,
        evidence_pack_id: str | None = None,
    ) -> WorkflowInstance:
        instance = self._instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        for step in instance.steps:
            if step.step_id == step_id and step.status == StepStatus.WAITING_APPROVAL:
                step.status = StepStatus.APPROVED
                step.approved_by = approved_by
                step.evidence_pack_id = evidence_pack_id
                step.completed_at = datetime.now(timezone.utc)
                instance.current_step_index += 1
                instance.status = WorkflowStatus.RUNNING
                self._advance(instance)
                return instance

        raise ValueError(f"Step {step_id} not awaiting approval")

    def reject_step(
        self,
        instance_id: str,
        step_id: str,
        rejected_by: str,
        reason: str = "",
    ) -> WorkflowInstance:
        instance = self._instances.get(instance_id)
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")

        for step in instance.steps:
            if step.step_id == step_id and step.status == StepStatus.WAITING_APPROVAL:
                step.status = StepStatus.REJECTED
                step.error = reason
                step.completed_at = datetime.now(timezone.utc)
                instance.status = WorkflowStatus.FAILED
                instance.updated_at = datetime.now(timezone.utc)
                return instance

        raise ValueError(f"Step {step_id} not awaiting approval")

    def get_instance(self, instance_id: str) -> WorkflowInstance | None:
        return self._instances.get(instance_id)

    def list_pending_approvals(self, tenant_id: str | None = None) -> list[dict]:
        results = []
        for inst in self._instances.values():
            if tenant_id and inst.tenant_id != tenant_id:
                continue
            if inst.status in (WorkflowStatus.PAUSED_HITL, WorkflowStatus.PAUSED_APPROVAL):
                for step in inst.steps:
                    if step.status == StepStatus.WAITING_APPROVAL:
                        results.append({
                            "instance_id": inst.instance_id,
                            "workflow_id": inst.workflow_id,
                            "step_id": step.step_id,
                            "step_name": step.name,
                            "approval_class": step.approval_class,
                            "tenant_id": inst.tenant_id,
                        })
        return results


workflow_engine = DurableWorkflowEngine()

"""Sovereign Execution Plane: durable workflows and workflow steps."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class DurableWorkflow(TenantModel):
    __tablename__ = "durable_workflows"

    workflow_type = Column(String(80), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    status = Column(String(30), nullable=False, default="pending", index=True)
    current_step = Column(String(120), nullable=True)
    total_steps = Column(Integer, default=0)
    completed_steps = Column(Integer, default=0)
    idempotency_key = Column(String(120), nullable=False, unique=True, index=True)
    is_resumable = Column(Boolean, default=True)
    is_compensatable = Column(Boolean, default=True)
    compensation_plan = Column(JSONB, nullable=True)
    checkpoint_data = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    initiator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    target_entity_type = Column(String(80), nullable=True, index=True)
    target_entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    timeout_seconds = Column(Integer, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    correlation_id = Column(String(80), nullable=True, index=True)

    initiator = relationship("User", foreign_keys=[initiator_id])
    steps = relationship("WorkflowStep", back_populates="workflow", order_by="WorkflowStep.step_order")


class WorkflowStep(TenantModel):
    __tablename__ = "workflow_steps"

    workflow_id = Column(UUID(as_uuid=True), ForeignKey("durable_workflows.id"), nullable=False, index=True)
    step_order = Column(Integer, nullable=False)
    step_name = Column(String(120), nullable=False)
    step_type = Column(String(50), nullable=False)
    status = Column(String(30), nullable=False, default="pending")
    input_data = Column(JSONB, nullable=True)
    output_data = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_status = Column(String(30), nullable=True)
    approval_note = Column(Text, nullable=True)

    workflow = relationship("DurableWorkflow", foreign_keys=[workflow_id], back_populates="steps")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])

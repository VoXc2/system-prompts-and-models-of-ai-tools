"""Durable sovereign workflows."""

from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, UniqueConstraint

from app.models.base import TenantModel
from app.models.compat import JSONB


class SovereignWorkflow(TenantModel):
    __tablename__ = "sovereign_workflows"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_sovereign_workflow_idempotency_key"),
    )

    workflow_type = Column(String(100), nullable=False, index=True)
    state = Column(String(30), nullable=False, default="pending", index=True)
    payload = Column(JSONB, default=dict)
    approval_class = Column(String(30), nullable=True)
    idempotency_key = Column(String(200), nullable=True)
    last_checkpoint_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    compensation_reason = Column(Text, nullable=True)
    observable_url = Column(String(500), nullable=True)

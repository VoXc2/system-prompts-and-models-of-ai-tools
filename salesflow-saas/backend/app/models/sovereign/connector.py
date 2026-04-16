"""Per-tenant connector health and configuration."""

from sqlalchemy import Column, String, Text, DateTime, UniqueConstraint

from app.models.base import TenantModel
from app.models.compat import JSONB


class SovereignConnectorState(TenantModel):
    __tablename__ = "sovereign_connector_states"
    __table_args__ = (
        UniqueConstraint("tenant_id", "connector_id", name="uq_sovereign_connector_tenant"),
    )

    connector_id = Column(String(100), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    display_name_ar = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="unknown")
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    config = Column(JSONB, default=dict)

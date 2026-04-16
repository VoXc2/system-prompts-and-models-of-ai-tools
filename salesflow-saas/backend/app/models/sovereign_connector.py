"""Sovereign Connector: connector facade registry."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean

from app.models.base import TenantModel
from app.models.compat import JSONB


class ConnectorDefinition(TenantModel):
    __tablename__ = "connector_definitions"

    connector_key = Column(String(80), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=False)
    display_name_ar = Column(String(255), nullable=True)
    version = Column(String(20), nullable=False)
    provider = Column(String(120), nullable=False, index=True)
    contract_schema = Column(JSONB, nullable=False)
    retry_policy = Column(JSONB, nullable=False)
    timeout_seconds = Column(Integer, default=30)
    idempotency_key_template = Column(String(255), nullable=True)
    action_class = Column(String(30), nullable=False, default="auto")
    audit_events = Column(JSONB, nullable=True)
    telemetry_config = Column(JSONB, nullable=True)
    compensation_notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)

"""Agent action contradictions and resolution."""

from sqlalchemy import Column, String, Text, Boolean

from app.models.base import TenantModel
from app.models.compat import JSONB


class SovereignContradiction(TenantModel):
    __tablename__ = "sovereign_contradictions"

    agent_id = Column(String(100), nullable=False, index=True)
    intended_action = Column(Text, nullable=False)
    claimed_action = Column(Text, nullable=True)
    actual_tool_call = Column(Text, nullable=True)
    side_effects = Column(JSONB, default=list)
    contradiction_detected = Column(Boolean, nullable=False, default=False)
    resolution_status = Column(String(20), nullable=False, default="open", index=True)
    resolution_notes = Column(Text, nullable=True)

"""Policy evaluation and tool verification records."""

from sqlalchemy import Column, String, Text, Boolean

from app.models.base import TenantModel
from app.models.compat import JSONB


class SovereignPolicyEvaluation(TenantModel):
    __tablename__ = "sovereign_policy_evaluations"

    action_type = Column(String(100), nullable=False, index=True)
    context = Column(JSONB, default=dict)
    decision = Column(String(20), nullable=False)
    reasons = Column(JSONB, default=list)
    evaluated_by = Column(String(100), nullable=False)


class SovereignToolVerification(TenantModel):
    __tablename__ = "sovereign_tool_verifications"

    agent_id = Column(String(100), nullable=False, index=True)
    tool_name = Column(String(200), nullable=False)
    parameters = Column(JSONB, default=dict)
    verified = Column(Boolean, nullable=False, default=False)
    risk_level = Column(String(20), nullable=False)
    verification_notes = Column(Text, nullable=True)

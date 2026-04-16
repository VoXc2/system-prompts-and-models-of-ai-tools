"""Sovereign Trust Plane: policy rules, evaluations, tool verification, compliance."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship

from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class PolicyRule(TenantModel):
    __tablename__ = "policy_rules"

    rule_code = Column(String(120), nullable=False, unique=True, index=True)
    rule_name = Column(String(255), nullable=False)
    rule_name_ar = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    policy_category = Column(String(80), nullable=False, index=True)
    rule_definition = Column(JSONB, nullable=False)
    severity = Column(String(30), nullable=False, default="info")
    is_active = Column(Boolean, default=True)
    applies_to_roles = Column(JSONB, nullable=True)
    applies_to_entities = Column(JSONB, nullable=True)

    evaluations = relationship("PolicyEvaluation", back_populates="rule")


class PolicyEvaluation(TenantModel):
    __tablename__ = "policy_evaluations"

    rule_id = Column(UUID(as_uuid=True), ForeignKey("policy_rules.id"), nullable=False, index=True)
    action_type = Column(String(80), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    target_entity_type = Column(String(80), nullable=True, index=True)
    target_entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    evaluation_result = Column(String(30), nullable=False, index=True)
    input_context = Column(JSONB, nullable=True)
    violation_details = Column(Text, nullable=True)
    violation_details_ar = Column(Text, nullable=True)

    rule = relationship("PolicyRule", foreign_keys=[rule_id], back_populates="evaluations")
    actor = relationship("User", foreign_keys=[actor_id])


class ToolVerification(TenantModel):
    __tablename__ = "tool_verifications"

    tool_name = Column(String(120), nullable=False, index=True)
    tool_version = Column(String(50), nullable=True)
    invocation_id = Column(String(120), nullable=False, index=True)
    invoked_by = Column(String(80), nullable=False)
    input_hash = Column(String(64), nullable=True)
    output_hash = Column(String(64), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    side_effects = Column(JSONB, nullable=True)
    audit_trail = Column(JSONB, nullable=True)


class ComplianceMapping(TenantModel):
    __tablename__ = "compliance_mappings"

    framework = Column(String(80), nullable=False, index=True)
    control_id = Column(String(80), nullable=False)
    control_name = Column(String(255), nullable=False)
    control_name_ar = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    status = Column(String(30), nullable=False, default="not_started")
    evidence_refs = Column(JSONB, nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_assessed_at = Column(DateTime(timezone=True), nullable=True)
    next_review_at = Column(DateTime(timezone=True), nullable=True)
    risk_level = Column(String(30), nullable=False, default="medium")

    owner = relationship("User", foreign_keys=[owner_id])

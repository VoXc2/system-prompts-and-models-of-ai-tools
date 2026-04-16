"""Executive / Board OS — executive surfaces and governance models."""

from __future__ import annotations

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TenantModel
from app.models.compat import UUID, JSONB


class ExecutiveApproval(TenantModel):
    __tablename__ = "executive_approvals"

    resource_type = Column(String(80), nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(120), nullable=False)
    approval_class = Column(String(30), nullable=False)  # manager, director, vp, c_level, board
    sensitivity_class = Column(String(30), default="internal")
    reversibility_class = Column(String(30), default="fully_reversible")
    status = Column(String(30), default="pending")  # pending, approved, rejected, escalated, expired
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    decided_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    financial_impact_sar = Column(Numeric(16, 2), nullable=True)
    rationale = Column(Text, nullable=True)
    rationale_ar = Column(Text, nullable=True)
    alternatives = Column(JSONB, default=list)
    risk_summary = Column(Text, nullable=True)
    risk_summary_ar = Column(Text, nullable=True)
    evidence_pack_id = Column(String(80), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    escalated_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    trace_id = Column(String(80), nullable=True, index=True)
    correlation_id = Column(String(80), nullable=True, index=True)

    requested_by = relationship("User", foreign_keys=[requested_by_id])
    decided_by = relationship("User", foreign_keys=[decided_by_id])


class BoardMemo(TenantModel):
    __tablename__ = "board_memos"

    title = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=True)
    memo_type = Column(String(50), nullable=False)  # acquisition, partnership, expansion, strategic, quarterly
    status = Column(String(30), default="draft")  # draft, review, submitted, acknowledged
    summary = Column(Text, nullable=True)
    summary_ar = Column(Text, nullable=True)
    financial_highlights = Column(JSONB, default=dict)
    risk_assessment = Column(JSONB, default=dict)
    recommendations = Column(JSONB, default=list)
    evidence_refs = Column(JSONB, default=list)
    prepared_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    meeting_date = Column(DateTime(timezone=True), nullable=True)


class PolicyViolation(TenantModel):
    __tablename__ = "policy_violations"

    violation_type = Column(String(80), nullable=False)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    resource_type = Column(String(80), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    description = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=True)
    policy_ref = Column(String(80), nullable=True)
    detected_by = Column(String(80), default="system")  # system, audit, manual
    status = Column(String(30), default="open")  # open, investigating, resolved, accepted, escalated
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    trace_id = Column(String(80), nullable=True, index=True)


class RiskHeatmapEntry(TenantModel):
    __tablename__ = "risk_heatmap"

    category = Column(String(80), nullable=False)  # sales, partnership, acquisition, expansion, compliance, operational
    risk_name = Column(String(255), nullable=False)
    risk_name_ar = Column(String(255), nullable=True)
    probability = Column(String(20), default="medium")  # low, medium, high
    impact = Column(String(20), default="medium")  # low, medium, high, critical
    score = Column(Integer, default=0)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    mitigation = Column(Text, nullable=True)
    status = Column(String(30), default="active")  # active, mitigated, accepted, resolved
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)


class ForecastEntry(TenantModel):
    __tablename__ = "forecast_entries"

    period = Column(String(20), nullable=False)  # 2026-Q2, 2026-M05
    category = Column(String(50), nullable=False)  # revenue, deals, partnerships, expansion
    forecast_sar = Column(Numeric(16, 2), nullable=True)
    actual_sar = Column(Numeric(16, 2), nullable=True)
    variance_pct = Column(Numeric(5, 2), nullable=True)
    notes = Column(Text, nullable=True)
    updated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)


class ComplianceMatrix(TenantModel):
    __tablename__ = "compliance_matrix"

    framework = Column(String(50), nullable=False)  # PDPL, NCA_ECC, NIST_AI_RMF, OWASP_LLM
    control_id = Column(String(50), nullable=False)
    control_name = Column(String(255), nullable=False)
    control_name_ar = Column(String(255), nullable=True)
    status = Column(String(30), default="not_assessed")  # not_assessed, compliant, partial, non_compliant, not_applicable
    evidence_ref = Column(String(500), nullable=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    last_assessed_at = Column(DateTime(timezone=True), nullable=True)
    next_review_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)


class ModelRoutingLog(TenantModel):
    __tablename__ = "model_routing_logs"

    task_class = Column(String(80), nullable=False)
    selected_model = Column(String(120), nullable=False)
    fallback_model = Column(String(120), nullable=True)
    latency_ms = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)
    schema_adherence = Column(Boolean, default=True)
    tool_call_reliability = Column(Boolean, default=True)
    contradiction_detected = Column(Boolean, default=False)
    arabic_quality_score = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(8, 4), nullable=True)
    trace_id = Column(String(80), nullable=True, index=True)


class ToolVerificationEntry(TenantModel):
    __tablename__ = "tool_verification_ledger"

    tool_id = Column(String(80), nullable=False)
    tool_name = Column(String(255), nullable=False)
    tool_name_ar = Column(String(255), nullable=True)
    version = Column(String(30), nullable=False)
    verified = Column(Boolean, default=False)
    checksum = Column(String(128), nullable=True)
    connector_id = Column(String(80), nullable=True)
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String(80), default="system")
    health_status = Column(String(30), default="unknown")  # healthy, degraded, error, unknown
    notes = Column(Text, nullable=True)

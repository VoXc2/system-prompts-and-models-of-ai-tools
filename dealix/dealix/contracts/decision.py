"""
Decision Output Contract — the canonical artifact every critical agent emits.

Per the blueprint, no critical output leaves the Decision Plane without:
- a trace ID
- evidence references
- classification (approval / reversibility / sensitivity)
- explicit next-actions with policy requirements
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from dealix.classifications import ApprovalClass, ReversibilityClass, SensitivityClass


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def _new_decision_id() -> str:
    return f"dec_{uuid.uuid4().hex[:16]}"


class Evidence(BaseModel):
    """A single piece of evidence backing a decision.

    Evidence MUST identify the source, carry a retrievable URI where possible,
    include a short verbatim excerpt, and a content hash for provenance.
    """

    model_config = ConfigDict(extra="forbid")

    source: str = Field(..., description="Named source (e.g. 'hubspot.contact', 'web:nytimes')")
    uri: str | None = Field(None, description="Retrievable URI or internal reference")
    excerpt: str = Field(..., max_length=2000, description="Short verbatim excerpt")
    content_hash: str | None = Field(None, description="SHA-256 of the full source content")
    retrieved_at: str = Field(default_factory=_utcnow_iso)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class PolicyRequirement(BaseModel):
    """A requirement the Trust Plane must satisfy before this decision executes."""

    model_config = ConfigDict(extra="forbid")

    policy_name: str
    description: str
    required: bool = True


class NextAction(BaseModel):
    """A proposed next action with its classification.

    NextActions are NEVER auto-executed from a decision — they are proposals
    that the Execution Plane picks up after Trust Plane clearance.
    """

    model_config = ConfigDict(extra="forbid")

    action_type: str = Field(..., description="e.g. 'booking_schedule', 'proposal_send'")
    description: str
    approval_class: ApprovalClass
    reversibility_class: ReversibilityClass
    sensitivity_class: SensitivityClass
    payload: dict[str, Any] = Field(default_factory=dict)
    policy_requirements: list[PolicyRequirement] = Field(default_factory=list)


class DecisionOutput(BaseModel):
    """The canonical output of any critical agent decision.

    This matches the JSON Schema in `dealix/contracts/schemas/decision_output.schema.json`.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"

    decision_id: str = Field(default_factory=_new_decision_id)
    tenant_id: str = Field(default="default")
    entity_id: str = Field(..., description="Business entity (lead_id, deal_id, partner_id...)")

    objective: str = Field(
        ..., description="What decision is being made, e.g. 'qualify_lead', 'recommend_proposal'"
    )
    agent_name: str
    model: str | None = None
    model_version: str | None = None

    recommendation: dict[str, Any] = Field(..., description="Structured recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0)
    rationale: str = Field(..., min_length=1, max_length=5000)

    evidence: list[Evidence] = Field(default_factory=list)
    freshness_window_hours: int = Field(default=24, ge=0)

    approval_class: ApprovalClass
    reversibility_class: ReversibilityClass
    sensitivity_class: SensitivityClass

    next_actions: list[NextAction] = Field(default_factory=list)
    policy_requirements: list[PolicyRequirement] = Field(default_factory=list)

    trace_id: str | None = None
    span_id: str | None = None
    correlation_id: str | None = None

    created_at: str = Field(default_factory=_utcnow_iso)
    locale: Literal["ar", "en"] = "ar"

    # ── Validators ──────────────────────────────────────────────
    @model_validator(mode="after")
    def _evidence_required_for_high_stakes(self) -> DecisionOutput:
        """A-class A2+ or R3 decisions MUST carry at least one evidence item."""
        high_stakes = (
            self.approval_class in (ApprovalClass.A2, ApprovalClass.A3)
            or self.reversibility_class == ReversibilityClass.R3
        )
        if high_stakes and len(self.evidence) == 0:
            raise ValueError("High-stakes decisions (A2+/R3) require at least one Evidence item")
        return self

    @property
    def is_high_stakes(self) -> bool:
        return (
            self.approval_class in (ApprovalClass.A2, ApprovalClass.A3)
            or self.reversibility_class == ReversibilityClass.R3
            or self.sensitivity_class == SensitivityClass.S3
        )

    @property
    def requires_human_approval(self) -> bool:
        return self.approval_class.requires_approval

    def to_json(self) -> str:
        return self.model_dump_json(indent=2)

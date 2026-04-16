"""Sovereign OS — Core Pydantic schemas shared across all five planes."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import EnumType, StrEnum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class _LenStrEnumType(EnumType):
    """Metaclass so `len(SomeStrEnum)` returns member count (test / introspection friendly)."""

    def __len__(self) -> int:
        return len(self.__members__)


class SovereigntyDimension(StrEnum, metaclass=_LenStrEnumType):
    DECISION = "DECISION"
    EXECUTION = "EXECUTION"
    TRUST = "TRUST"
    MARKET = "MARKET"


class PlaneType(StrEnum, metaclass=_LenStrEnumType):
    DECISION = "DECISION"
    EXECUTION = "EXECUTION"
    TRUST = "TRUST"
    DATA = "DATA"
    OPERATING = "OPERATING"


class BusinessTrack(StrEnum, metaclass=_LenStrEnumType):
    REVENUE = "REVENUE"
    PARTNERSHIP = "PARTNERSHIP"
    MA_CORPDEV = "MA_CORPDEV"
    EXPANSION = "EXPANSION"
    PMI_PMO = "PMI_PMO"
    EXECUTIVE_BOARD = "EXECUTIVE_BOARD"


class ActionClass(StrEnum, metaclass=_LenStrEnumType):
    FULLY_AUTOMATED = "FULLY_AUTOMATED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    FORBIDDEN = "FORBIDDEN"


class ApprovalClass(StrEnum, metaclass=_LenStrEnumType):
    TEAM_LEAD = "TEAM_LEAD"
    VP_EXECUTIVE = "VP_EXECUTIVE"
    BOARD_LEVEL = "BOARD_LEVEL"


class ReversibilityClass(StrEnum, metaclass=_LenStrEnumType):
    INSTANTLY_REVERSIBLE = "INSTANTLY_REVERSIBLE"
    REVERSIBLE_WITH_COST = "REVERSIBLE_WITH_COST"
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"
    IRREVERSIBLE = "IRREVERSIBLE"


class SensitivityLevel(StrEnum, metaclass=_LenStrEnumType):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    TOP_SECRET = "TOP_SECRET"


class AgentRole(StrEnum, metaclass=_LenStrEnumType):
    ANALYST = "ANALYST"
    EXECUTOR = "EXECUTOR"
    ADVISOR = "ADVISOR"


class SovereignRoutingLane(StrEnum, metaclass=_LenStrEnumType):
    CODING = "CODING"
    EXECUTIVE_REASONING = "EXECUTIVE_REASONING"
    THROUGHPUT_DRAFTING = "THROUGHPUT_DRAFTING"
    ARABIC_NLP = "ARABIC_NLP"
    FALLBACK = "FALLBACK"


class RetryPolicy(BaseModel):
    max_retries: int = 3
    backoff_base_seconds: float = 1.0
    backoff_max_seconds: float = 60.0
    retry_on_status_codes: list[int] = Field(default_factory=lambda: [408, 429, 500, 502, 503, 504])


class ProvenanceInfo(BaseModel):
    source: str
    freshness_seconds: int = 0
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    model_version: str = ""
    retrieved_at: datetime = Field(default_factory=_utc_now)


class EvidenceItem(BaseModel):
    item_id: UUID = Field(default_factory=uuid4)
    title: str
    title_ar: str
    source: str
    content_summary: str
    content_summary_ar: str
    provenance: ProvenanceInfo
    created_at: datetime = Field(default_factory=_utc_now)


class EvidencePack(BaseModel):
    pack_id: UUID = Field(default_factory=uuid4)
    track: BusinessTrack
    items: list[EvidenceItem] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    assumptions_ar: list[str] = Field(default_factory=list)
    financial_model_version: str | None = None
    policy_notes: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utc_now)


class RecommendationPayload(BaseModel):
    recommendation_id: UUID = Field(default_factory=uuid4)
    track: BusinessTrack
    title: str
    title_ar: str
    description: str
    description_ar: str
    action_class: ActionClass
    approval_class: ApprovalClass
    reversibility_class: ReversibilityClass
    sensitivity_level: SensitivityLevel
    evidence_pack: EvidencePack
    policy_evaluation: dict[str, Any] = Field(default_factory=dict)
    next_best_actions: list[str] = Field(default_factory=list)
    next_best_actions_ar: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utc_now)


class ConnectorContract(BaseModel):
    connector_id: str
    display_name: str
    display_name_ar: str
    version: str
    base_url: str
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_ms: int = 30_000
    idempotency_key_header: str = "Idempotency-Key"
    approval_policy: ActionClass = ActionClass.APPROVAL_REQUIRED
    audit_mapping: dict[str, Any] = Field(default_factory=dict)
    telemetry_enabled: bool = True
    rollback_notes: str = ""
    rollback_notes_ar: str = ""


class ContradictionRecord(BaseModel):
    record_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=_utc_now)
    agent_id: str
    intended_action: str
    claimed_action: str
    actual_tool_call: str
    side_effects: list[str] = Field(default_factory=list)
    contradiction_detected: bool = False
    resolution_status: Literal["open", "resolved", "escalated"] = "open"
    resolution_notes: str | None = None


class ModelRoutingDecision(BaseModel):
    lane: SovereignRoutingLane
    model_id: str
    provider: str
    latency_budget_ms: int
    cost_ceiling_usd: float
    arabic_quality_required: bool = False


class ProgramLock(BaseModel):
    lock_id: str
    planes: list[PlaneType]
    tracks: list[BusinessTrack]
    agent_roles: list[AgentRole]
    action_classes: list[ActionClass]
    approval_classes: list[ApprovalClass]
    reversibility_classes: list[ReversibilityClass]
    sensitivity_model: dict[str, Any]
    locked_at: datetime = Field(default_factory=_utc_now)
    locked_by: str


# --- Data plane (governance / quality / contracts) ---


class DataQualityResult(BaseModel):
    """Dataset quality validation summary."""

    dataset_name: str
    score: float = Field(ge=0.0, le=100.0)
    issues_en: list[str] = Field(default_factory=list)
    issues_ar: list[str] = Field(default_factory=list)
    passed: bool = True


class EventValidationResult(BaseModel):
    """Validation of an event against a registered contract."""

    valid: bool
    errors_en: list[str] = Field(default_factory=list)
    errors_ar: list[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """Document ingestion / extraction outcome."""

    document_path: str
    chunks: int = 0
    summary_en: str
    summary_ar: str


class SemanticHit(BaseModel):
    """One semantic search hit."""

    id: str
    score: float
    text_en: str
    text_ar: str


class SemanticQueryResult(BaseModel):
    """Semantic retrieval over a governed collection."""

    collection: str
    hits: list[SemanticHit] = Field(default_factory=list)


class ConnectorHealthStatus(BaseModel):
    """Health of an external or internal data connector."""

    connector_id: str
    healthy: bool
    latency_ms: float | None = None
    detail_en: str
    detail_ar: str


# --- Operating plane (SDLC / releases / evidence) ---


class ReleaseGateResult(BaseModel):
    """Outcome of a release gate check."""

    release_id: str
    passed: bool
    blockers_en: list[str] = Field(default_factory=list)
    blockers_ar: list[str] = Field(default_factory=list)


class ProvenanceResult(BaseModel):
    """Artifact provenance verification."""

    artifact_id: str
    verified: bool
    provenance_chain_en: str
    provenance_chain_ar: str


class DeploymentStatus(BaseModel):
    """Deployment status for an environment."""

    environment: str
    version: str | None = None
    healthy: bool = True
    detail_en: str
    detail_ar: str
    updated_at: datetime = Field(default_factory=_utc_now)


class RulesetEnforcementResult(BaseModel):
    """Branch ruleset enforcement outcome."""

    branch: str
    compliant: bool
    violations_en: list[str] = Field(default_factory=list)
    violations_ar: list[str] = Field(default_factory=list)


class CodeOwnerResult(BaseModel):
    """CODEOWNERS resolution for a path."""

    file_path: str
    owners: list[str] = Field(default_factory=list)
    matched_rule_en: str
    matched_rule_ar: str


class AuditLogEntry(BaseModel):
    """Single audit log row for operating-plane streams."""

    entry_id: str
    tenant_id: str
    timestamp: datetime
    actor: str
    action: str
    resource: str | None = None
    message_en: str
    message_ar: str

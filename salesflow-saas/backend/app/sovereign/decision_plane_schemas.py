"""Decision-plane Pydantic stubs (signals, memos, forecasts, legacy evidence packs)."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class SignalKind(StrEnum):
    """High-level categories for decision-plane signals."""

    INTENT = "intent"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    COMPLIANCE = "compliance"
    ENGAGEMENT = "engagement"


class DecisionSignal(BaseModel):
    """Typed signal emitted from raw operational data."""

    signal_id: str
    kind: SignalKind
    track: str
    strength: float = Field(ge=0.0, le=1.0, description="0–1 confidence in the signal")
    payload: dict[str, Any] = Field(default_factory=dict)
    description_en: str
    description_ar: str


class TriagedSignal(BaseModel):
    """Signal with urgency and ordering metadata."""

    signal: DecisionSignal
    priority_rank: int = Field(ge=1)
    urgency_score: float = Field(ge=0.0, le=100.0)
    rationale_en: str
    rationale_ar: str


class ScenarioAnalysisItem(BaseModel):
    """Single scenario with score and bilingual rationale."""

    scenario_id: str
    label_en: str
    label_ar: str
    score: float
    upside_en: str
    upside_ar: str
    downside_en: str
    downside_ar: str


class ScenarioAnalysisReport(BaseModel):
    """Scored comparison across scenarios."""

    tenant_id: str
    track: str
    items: list[ScenarioAnalysisItem]
    summary_en: str
    summary_ar: str


class MemoSection(BaseModel):
    """Structured section inside an executive memo."""

    heading_en: str
    heading_ar: str
    body_en: str
    body_ar: str


class StructuredMemo(BaseModel):
    """Bilingual decision memo."""

    tenant_id: str
    track: str
    language: str = "ar"
    title_en: str
    title_ar: str
    sections: list[MemoSection]
    executive_summary_en: str
    executive_summary_ar: str


class ForecastPoint(BaseModel):
    """One horizon step in a forecast series."""

    day_offset: int
    point_estimate: float
    lower_bound: float
    upper_bound: float


class ForecastResult(BaseModel):
    """Forecast with confidence intervals."""

    tenant_id: str
    track: str
    horizon_days: int
    unit_en: str = "SAR / probability / count depending on track"
    unit_ar: str = "وحدة القياس تعتمد على المسار (مبيعات/احتمالية/عدد)"
    points: list[ForecastPoint]
    methodology_note_en: str = "Stub forecast — replace with calibrated model."
    methodology_note_ar: str = "تنبؤ تجريبي — يُستبدل بنموذج معاير لاحقًا."
    confidence_level: float = Field(default=0.9, ge=0.5, le=0.99)


class RankedAction(BaseModel):
    """One ranked next-best action."""

    action_id: str
    rank: int = Field(ge=1)
    action_en: str
    action_ar: str
    expected_impact_score: float = Field(ge=0.0, le=100.0)
    notes_en: str
    notes_ar: str


class LegacyDecisionEvidenceItem(BaseModel):
    """Single piece of evidence in a legacy decision-plane pack."""

    item_id: str
    source: str
    snippet_en: str
    snippet_ar: str
    relevance: float = Field(ge=0.0, le=1.0)


class LegacyDecisionEvidencePack(BaseModel):
    """Assembled evidence for human or agent review (decision-plane stub)."""

    tenant_id: str
    track: str
    pack_id: str
    items: list[LegacyDecisionEvidenceItem]
    cover_note_en: str
    cover_note_ar: str


class LegacyDecisionRecommendationPayload(BaseModel):
    """Machine- and human-readable recommendation bundle (decision-plane stub)."""

    tenant_id: str
    track: str
    headline_en: str
    headline_ar: str
    rationale_en: str
    rationale_ar: str
    actions: list[RankedAction]
    evidence_refs: list[str] = Field(default_factory=list)

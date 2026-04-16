"""Decision Plane — intelligence and analysis only (no durable commitments)."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.sovereign.decision_plane_schemas import (
    DecisionSignal,
    ForecastPoint,
    ForecastResult,
    MemoSection,
    RankedAction,
    ScenarioAnalysisItem,
    ScenarioAnalysisReport,
    SignalKind,
    StructuredMemo,
    TriagedSignal,
)
from app.sovereign.schemas import (
    ActionClass,
    ApprovalClass,
    BusinessTrack,
    EvidenceItem,
    EvidencePack,
    ProvenanceInfo,
    RecommendationPayload,
    ReversibilityClass,
    SensitivityLevel,
)

logger = logging.getLogger("dealix.sovereign.decision_plane")


def _business_track(track: str) -> BusinessTrack:
    key = track.strip().upper().replace("-", "_")
    try:
        return BusinessTrack(key)
    except ValueError:
        return BusinessTrack.REVENUE


class DecisionPlaneEngine:
    """Async stubs for signal detection, triage, forecasting, and recommendations."""

    async def detect_signals(
        self,
        tenant_id: str,
        track: str,
        raw_data: dict[str, Any],
    ) -> list[DecisionSignal]:
        logger.info(
            "decision_plane.detect_signals tenant_id=%s track=%s keys=%s",
            tenant_id,
            track,
            list(raw_data.keys()),
        )
        sid = str(uuid.uuid4())
        return [
            DecisionSignal(
                signal_id=sid,
                kind=SignalKind.OPPORTUNITY,
                track=track,
                strength=0.35,
                payload={"stub": True, "keys": list(raw_data.keys())},
                description_en="Stub: potential uplift signal from ingested activity.",
                description_ar="إشارة تجريبية: احتمال تحسن بناءً على النشاط المُدخل.",
            )
        ]

    async def triage(
        self,
        tenant_id: str,
        signals: list[DecisionSignal],
    ) -> list[TriagedSignal]:
        logger.info(
            "decision_plane.triage tenant_id=%s signal_count=%s",
            tenant_id,
            len(signals),
        )
        out: list[TriagedSignal] = []
        for i, s in enumerate(sorted(signals, key=lambda x: -x.strength)):
            out.append(
                TriagedSignal(
                    signal=s,
                    priority_rank=i + 1,
                    urgency_score=min(100.0, 40.0 + 60.0 * s.strength),
                    rationale_en="Ordered by signal strength (stub).",
                    rationale_ar="مرتبة حسب قوة الإشارة (وضع تجريبي).",
                )
            )
        return out

    async def analyze_scenarios(
        self,
        tenant_id: str,
        context: dict[str, Any],
        scenarios: list[dict[str, Any]],
    ) -> ScenarioAnalysisReport:
        logger.info(
            "decision_plane.analyze_scenarios tenant_id=%s scenario_count=%s",
            tenant_id,
            len(scenarios),
        )
        track = str(context.get("track", "REVENUE"))
        items: list[ScenarioAnalysisItem] = []
        for i, sc in enumerate(scenarios):
            label = str(sc.get("label", f"scenario_{i}"))
            items.append(
                ScenarioAnalysisItem(
                    scenario_id=str(sc.get("id", label)),
                    label_en=label,
                    label_ar=f"سيناريو: {label}",
                    score=float(sc.get("score", 50.0 - i * 5)),
                    upside_en="Revenue expansion under favorable conditions.",
                    upside_ar="توسع الإيرادات في ظروف مواتية.",
                    downside_en="Execution risk if demand softens.",
                    downside_ar="مخاطر التنفيذ إذا ضعف الطلب.",
                )
            )
        return ScenarioAnalysisReport(
            tenant_id=tenant_id,
            track=track,
            items=items,
            summary_en="Stub scenario scoring for sovereign decisioning.",
            summary_ar="تقييم تجريبي للسيناريوهات لمسار القرار السيادي.",
        )

    async def generate_memo(
        self,
        tenant_id: str,
        track: str,
        context: dict[str, Any],
        language: str = "ar",
    ) -> StructuredMemo:
        logger.info(
            "decision_plane.generate_memo tenant_id=%s track=%s language=%s",
            tenant_id,
            track,
            language,
        )
        _ = context
        return StructuredMemo(
            tenant_id=tenant_id,
            track=track,
            language=language,
            title_en=f"Executive memo — {track}",
            title_ar=f"مذكرة تنفيذية — {track}",
            sections=[
                MemoSection(
                    heading_en="Situation",
                    heading_ar="الوضع",
                    body_en="Stub narrative built from provided context keys.",
                    body_ar="نص تجريبي مبني على مفاتيح السياق المقدّمة.",
                ),
                MemoSection(
                    heading_en="Recommendation",
                    heading_ar="التوصية",
                    body_en="Proceed with governed experiments on the growth track.",
                    body_ar="المضي بتجارب محكومة على مسار النمو.",
                ),
            ],
            executive_summary_en="Decision plane memo stub — replace with LLM pipeline.",
            executive_summary_ar="مسودة مذكرة من مستوى القرار — تُستبدل بمسار نموذج لغوي.",
        )

    async def forecast(
        self,
        tenant_id: str,
        track: str,
        historical_data: list[dict[str, Any]],
        horizon_days: int,
    ) -> ForecastResult:
        logger.info(
            "decision_plane.forecast tenant_id=%s track=%s horizon_days=%s points=%s",
            tenant_id,
            track,
            horizon_days,
            len(historical_data),
        )
        base = float(historical_data[-1].get("value", 1.0)) if historical_data else 1.0
        points: list[ForecastPoint] = []
        for d in range(1, max(1, min(horizon_days, 14)) + 1):
            est = base * (1.0 + 0.01 * d)
            margin = 0.05 * est * d**0.5
            points.append(
                ForecastPoint(
                    day_offset=d,
                    point_estimate=est,
                    lower_bound=est - margin,
                    upper_bound=est + margin,
                )
            )
        return ForecastResult(
            tenant_id=tenant_id,
            track=track,
            horizon_days=horizon_days,
            points=points,
        )

    def _ranked_actions_stub(self) -> list[RankedAction]:
        return [
            RankedAction(
                action_id="act_qualify_pipeline",
                rank=1,
                action_en="Qualify top pipeline opportunities with PDPL-safe outreach.",
                action_ar="تأهيل أهم الفرص في خط الأنابيب مع تواصل آمن وفق حوكمة البيانات الشخصية.",
                expected_impact_score=72.0,
                notes_en="Highest leverage when conversion data is thin.",
                notes_ar="أعلى أثر عندما تكون بيانات التحويل محدودة.",
            ),
            RankedAction(
                action_id="act_refresh_icp",
                rank=2,
                action_en="Refresh ICP scoring using recent closed-won/lost reasons.",
                action_ar="تحديث تصنيف العميل المثالي باستخدام أسباب الإغلاق الأخيرة.",
                expected_impact_score=58.0,
                notes_en="Improves targeting for outbound sequences.",
                notes_ar="يحسن استهداف تسلسلات التواصل الصادر.",
            ),
        ]

    def _stub_evidence_pack(self, track: BusinessTrack) -> EvidencePack:
        return EvidencePack(
            track=track,
            items=[
                EvidenceItem(
                    title="Pipeline velocity snapshot",
                    title_ar="لقطة سرعة خط الأنابيب",
                    source="decision_plane_stub",
                    content_summary="Synthetic evidence for sovereign recommendation wiring.",
                    content_summary_ar="أدلة تركيبية لربط التوصية السيادية.",
                    provenance=ProvenanceInfo(
                        source="decision_plane",
                        freshness_seconds=0,
                        confidence=0.5,
                        model_version="stub-0",
                    ),
                )
            ],
            assumptions=["Figures are illustrative until analytics wiring completes."],
            assumptions_ar=["الأرقام توضيحية حتى اكتمال ربط التحليلات."],
            policy_notes=["Respect tenant isolation and PDPL consent before outreach."],
            alternatives=["Wait for more data", "Run a narrow pilot cohort"],
        )

    async def recommend(
        self,
        tenant_id: str,
        track: str,
        context: dict[str, Any],
    ) -> RecommendationPayload:
        logger.info(
            "decision_plane.recommend tenant_id=%s track=%s",
            tenant_id,
            track,
        )
        bt = _business_track(track)
        actions = self._ranked_actions_stub()
        pack = self._stub_evidence_pack(bt)
        return RecommendationPayload(
            track=bt,
            title="Prioritize qualification and ICP refresh (stub)",
            title_ar="أولوية للتأهيل وتحديث العميل المثالي (وضع تجريبي)",
            description="Balanced short-term revenue vs. learning velocity.",
            description_ar="موازنة بين الإيرادات قصيرة الأجل وسرعة التعلم.",
            action_class=ActionClass.APPROVAL_REQUIRED,
            approval_class=ApprovalClass.TEAM_LEAD,
            reversibility_class=ReversibilityClass.REVERSIBLE_WITH_COST,
            sensitivity_level=SensitivityLevel.INTERNAL,
            evidence_pack=pack,
            policy_evaluation={"tenant_id": tenant_id, "context_keys": list(context.keys())},
            next_best_actions=[a.action_en for a in actions],
            next_best_actions_ar=[a.action_ar for a in actions],
        )

    async def next_best_action(
        self,
        tenant_id: str,
        track: str,
        current_state: dict[str, Any],
    ) -> list[RankedAction]:
        logger.info(
            "decision_plane.next_best_action tenant_id=%s track=%s",
            tenant_id,
            track,
        )
        _ = current_state
        return self._ranked_actions_stub()

    async def assemble_evidence_pack(
        self,
        tenant_id: str,
        track: str,
        items: list[dict[str, Any]],
    ) -> EvidencePack:
        logger.info(
            "decision_plane.assemble_evidence_pack tenant_id=%s track=%s count=%s",
            tenant_id,
            track,
            len(items),
        )
        bt = _business_track(track)
        ev: list[EvidenceItem] = []
        for i, it in enumerate(items):
            ev.append(
                EvidenceItem(
                    title=str(it.get("title_en", it.get("title", f"Item {i + 1}"))),
                    title_ar=str(it.get("title_ar", f"عنصر {i + 1}")),
                    source=str(it.get("source", "internal")),
                    content_summary=str(
                        it.get("text_en", it.get("content_summary", "Evidence stub."))
                    ),
                    content_summary_ar=str(
                        it.get("text_ar", it.get("content_summary_ar", "دليل تجريبي."))
                    ),
                    provenance=ProvenanceInfo(
                        source=str(it.get("provenance_source", "assembled")),
                        freshness_seconds=int(it.get("freshness_seconds", 0)),
                        confidence=float(it.get("relevance", 0.5)),
                        model_version=str(it.get("model_version", "stub")),
                    ),
                )
            )
        if not ev:
            return self._stub_evidence_pack(bt)
        return EvidencePack(
            track=bt,
            items=ev,
            assumptions=[f"Assembled {len(ev)} items for tenant {tenant_id}."],
            assumptions_ar=[f"تم تجميع {len(ev)} عناصر للمستأجر {tenant_id}."],
        )


class DecisionPlane(DecisionPlaneEngine):
    """Sovereign Decision Plane — public entry type."""

    pass

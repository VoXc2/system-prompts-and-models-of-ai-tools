"""Sovereign OS — six business tracks."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, status
from pydantic import BaseModel, Field

from app.api.v1.sovereign.tenant import TenantIdQuery
from app.sovereign.tracks.executive_board.manager import (
    ApprovalCenterItem,
    BoardMemo,
    ExecutiveBoardTrackManager,
    PipelineOverview,
    PolicyViolation,
    RiskHeatmap,
)
from app.sovereign.tracks.expansion.manager import ExpansionTrackManager, LaunchReadiness, VarianceReport
from app.sovereign.tracks.ma_corpdev.manager import (
    BoardPack,
    DDProcess,
    ICMemo,
    MACorporateDevTrackManager,
    ScreeningResult,
    ValuationRange,
)
from app.sovereign.tracks.partnership.manager import (
    PartnershipTrackManager,
    PartnerScorecard,
    StrategicFitScore,
    TermSheetDraft,
)
from app.sovereign.tracks.pmi_pmo.manager import (
    IntegrationPlan,
    PMITrackManager,
    RiskRegister,
    WeeklyReview,
)
from app.sovereign.tracks.revenue.manager import (
    EnrichmentResult,
    FunnelMetrics,
    LeadCaptureResult,
    QualificationResult,
    RevenueTrackManager,
)

revenue_mgr = RevenueTrackManager()
partnership_mgr = PartnershipTrackManager()
ma_mgr = MACorporateDevTrackManager()
expansion_mgr = ExpansionTrackManager()
pmi_mgr = PMITrackManager()
executive_mgr = ExecutiveBoardTrackManager()

revenue_router = APIRouter(prefix="/tracks/revenue", tags=["Sovereign — Revenue"])
partnership_router = APIRouter(prefix="/tracks/partnership", tags=["Sovereign — Partnership"])
ma_router = APIRouter(prefix="/tracks/ma", tags=["Sovereign — M&A"])
expansion_router = APIRouter(prefix="/tracks/expansion", tags=["Sovereign — Expansion"])
pmi_router = APIRouter(prefix="/tracks/pmi", tags=["Sovereign — PMI"])
executive_router = APIRouter(prefix="/tracks/executive", tags=["Sovereign — Executive"])


# --- Revenue ---


class LeadCaptureBody(BaseModel):
    source: str = "web"
    channel: str = "organic"
    data: dict[str, Any] = Field(default_factory=dict)


@revenue_router.post(
    "/lead/capture",
    response_model=LeadCaptureResult,
    status_code=status.HTTP_201_CREATED,
    summary="Capture lead",
)
async def revenue_lead_capture(
    tenant_id: TenantIdQuery,
    body: LeadCaptureBody = Body(default_factory=LeadCaptureBody),
) -> LeadCaptureResult:
    try:
        return await revenue_mgr.capture_lead(tenant_id, body.source, body.channel, body.data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Lead capture failed.",
                "message_ar": "فشل تسجيل العميل المحتمل.",
                "error": str(exc),
            },
        ) from exc


@revenue_router.post(
    "/lead/{lead_id}/enrich",
    response_model=EnrichmentResult,
    summary="Enrich lead",
)
async def revenue_lead_enrich(tenant_id: TenantIdQuery, lead_id: str) -> EnrichmentResult:
    try:
        return await revenue_mgr.enrich_lead(tenant_id, lead_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Lead enrichment failed.",
                "message_ar": "فشل إثراء العميل المحتمل.",
                "error": str(exc),
            },
        ) from exc


@revenue_router.post(
    "/lead/{lead_id}/qualify",
    response_model=QualificationResult,
    summary="Qualify lead",
)
async def revenue_lead_qualify(tenant_id: TenantIdQuery, lead_id: str) -> QualificationResult:
    try:
        return await revenue_mgr.qualify_lead(tenant_id, lead_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Lead qualification failed.",
                "message_ar": "فشل تأهيل العميل المحتمل.",
                "error": str(exc),
            },
        ) from exc


@revenue_router.post(
    "/lead/{lead_id}/score",
    response_model=dict[str, Any],
    summary="Score lead",
)
async def revenue_lead_score(tenant_id: TenantIdQuery, lead_id: str) -> dict[str, Any]:
    try:
        return await revenue_mgr.score_lead(tenant_id, lead_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Lead scoring failed.",
                "message_ar": "فشل تسجيل درجة العميل المحتمل.",
                "error": str(exc),
            },
        ) from exc


@revenue_router.post(
    "/lead/{lead_id}/route",
    response_model=dict[str, Any],
    summary="Route lead",
)
async def revenue_lead_route(tenant_id: TenantIdQuery, lead_id: str) -> dict[str, Any]:
    try:
        return await revenue_mgr.route_lead(tenant_id, lead_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Lead routing failed.",
                "message_ar": "فشل توجيه العميل المحتمل.",
                "error": str(exc),
            },
        ) from exc


@revenue_router.get(
    "/funnel/metrics",
    response_model=FunnelMetrics,
    summary="Funnel metrics",
)
async def revenue_funnel_metrics(tenant_id: TenantIdQuery) -> FunnelMetrics:
    try:
        return await revenue_mgr.get_funnel_metrics(tenant_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Funnel metrics failed.",
                "message_ar": "فشل جلب مقاييس القمع.",
                "error": str(exc),
            },
        ) from exc


# --- Partnership (static paths before {partner_id}) ---


class ScoutBody(BaseModel):
    criteria: dict[str, Any] = Field(default_factory=dict)


@partnership_router.post("/scout", summary="Scout partners")
async def partnership_scout(
    tenant_id: TenantIdQuery,
    body: ScoutBody = Body(default_factory=ScoutBody),
) -> list[dict[str, Any]]:
    try:
        candidates = await partnership_mgr.scout_partners(tenant_id, body.criteria)
        return [c.model_dump() for c in candidates]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Partner scouting failed.",
                "message_ar": "فشل استكشاف الشركاء.",
                "error": str(exc),
            },
        ) from exc


@partnership_router.post(
    "/{partner_id}/fit-score",
    response_model=StrategicFitScore,
    summary="Strategic fit score",
)
async def partnership_fit_score(tenant_id: TenantIdQuery, partner_id: str) -> StrategicFitScore:
    try:
        return await partnership_mgr.score_strategic_fit(tenant_id, partner_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Fit scoring failed.",
                "message_ar": "فشل حساب درجة الملاءمة.",
                "error": str(exc),
            },
        ) from exc


@partnership_router.post(
    "/{partner_id}/term-sheet",
    response_model=TermSheetDraft,
    summary="Draft term sheet",
)
async def partnership_term_sheet(tenant_id: TenantIdQuery, partner_id: str) -> TermSheetDraft:
    try:
        return await partnership_mgr.draft_term_sheet(tenant_id, partner_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Term sheet drafting failed.",
                "message_ar": "فشل صياغة ورقة الشروط.",
                "error": str(exc),
            },
        ) from exc


@partnership_router.get(
    "/{partner_id}/scorecard",
    response_model=PartnerScorecard,
    summary="Partner scorecard",
)
async def partnership_scorecard(tenant_id: TenantIdQuery, partner_id: str) -> PartnerScorecard:
    try:
        return await partnership_mgr.get_partner_scorecard(tenant_id, partner_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Scorecard lookup failed.",
                "message_ar": "فشل جلب بطاقة الأداء.",
                "error": str(exc),
            },
        ) from exc


# --- M&A ---


class SourceTargetsBody(BaseModel):
    criteria: dict[str, Any] = Field(default_factory=dict)


class DDBody(BaseModel):
    dd_type: str = "full"


@ma_router.post("/targets/source", summary="Source targets")
async def ma_source_targets(
    tenant_id: TenantIdQuery,
    body: SourceTargetsBody = Body(default_factory=SourceTargetsBody),
) -> list[dict[str, Any]]:
    try:
        targets = await ma_mgr.source_targets(tenant_id, body.criteria)
        return [t.model_dump() for t in targets]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Target sourcing failed.",
                "message_ar": "فشل توليد قائمة الأهداف.",
                "error": str(exc),
            },
        ) from exc


@ma_router.post(
    "/{target_id}/screen",
    response_model=ScreeningResult,
    summary="Screen target",
)
async def ma_screen(tenant_id: TenantIdQuery, target_id: str) -> ScreeningResult:
    try:
        return await ma_mgr.screen_target(tenant_id, target_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Screening failed.",
                "message_ar": "فشل الفرز.",
                "error": str(exc),
            },
        ) from exc


@ma_router.post(
    "/{target_id}/dd",
    response_model=DDProcess,
    summary="Orchestrate diligence",
)
async def ma_dd(
    tenant_id: TenantIdQuery,
    target_id: str,
    body: DDBody = Body(default_factory=DDBody),
) -> DDProcess:
    try:
        return await ma_mgr.orchestrate_dd(tenant_id, target_id, body.dd_type)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Diligence orchestration failed.",
                "message_ar": "فشل تنسيق العناية الواجبة.",
                "error": str(exc),
            },
        ) from exc


@ma_router.get(
    "/{target_id}/valuation",
    response_model=ValuationRange,
    summary="Valuation range",
)
async def ma_valuation(tenant_id: TenantIdQuery, target_id: str) -> ValuationRange:
    try:
        return await ma_mgr.estimate_valuation_range(tenant_id, target_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Valuation failed.",
                "message_ar": "فشل التقييم.",
                "error": str(exc),
            },
        ) from exc


@ma_router.post(
    "/{target_id}/ic-memo",
    response_model=ICMemo,
    summary="IC memo",
)
async def ma_ic_memo(tenant_id: TenantIdQuery, target_id: str) -> ICMemo:
    try:
        return await ma_mgr.generate_ic_memo(tenant_id, target_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "IC memo generation failed.",
                "message_ar": "فشل إنشاء مذكرة لجنة الاستثمار.",
                "error": str(exc),
            },
        ) from exc


@ma_router.post(
    "/{target_id}/board-pack",
    response_model=BoardPack,
    summary="Board pack",
)
async def ma_board_pack(tenant_id: TenantIdQuery, target_id: str) -> BoardPack:
    try:
        return await ma_mgr.generate_board_pack(tenant_id, target_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Board pack generation failed.",
                "message_ar": "فشل إنشاء حزمة مجلس الإدارة.",
                "error": str(exc),
            },
        ) from exc


# --- Expansion ---


class ScanMarketsBody(BaseModel):
    criteria: dict[str, Any] = Field(default_factory=dict)


class PrioritizeMarketsBody(BaseModel):
    market_ids: list[str] = Field(default_factory=list)


@expansion_router.post("/markets/scan", summary="Scan markets")
async def expansion_markets_scan(
    tenant_id: TenantIdQuery,
    body: ScanMarketsBody = Body(default_factory=ScanMarketsBody),
) -> list[dict[str, Any]]:
    try:
        markets = await expansion_mgr.scan_markets(tenant_id, body.criteria)
        return [m.model_dump() for m in markets]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Market scan failed.",
                "message_ar": "فشل مسح الأسواق.",
                "error": str(exc),
            },
        ) from exc


@expansion_router.post("/markets/prioritize", summary="Prioritize markets")
async def expansion_markets_prioritize(
    tenant_id: TenantIdQuery,
    body: PrioritizeMarketsBody = Body(default_factory=PrioritizeMarketsBody),
) -> list[dict[str, Any]]:
    try:
        return await expansion_mgr.prioritize_markets(tenant_id, body.market_ids)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Market prioritization failed.",
                "message_ar": "فشل ترتيب الأسواق.",
                "error": str(exc),
            },
        ) from exc


@expansion_router.get(
    "/{market_id}/launch-readiness",
    response_model=LaunchReadiness,
    summary="Launch readiness",
)
async def expansion_launch_readiness(tenant_id: TenantIdQuery, market_id: str) -> LaunchReadiness:
    try:
        return await expansion_mgr.check_launch_readiness(tenant_id, market_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Launch readiness check failed.",
                "message_ar": "فشل فحص جاهزية الإطلاق.",
                "error": str(exc),
            },
        ) from exc


@expansion_router.get(
    "/{market_id}/actual-vs-forecast",
    response_model=VarianceReport,
    summary="Actual vs forecast",
)
async def expansion_actual_vs_forecast(tenant_id: TenantIdQuery, market_id: str) -> VarianceReport:
    try:
        return await expansion_mgr.compare_actual_vs_forecast(tenant_id, market_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Variance analysis failed.",
                "message_ar": "فشل تحليل الانحراف.",
                "error": str(exc),
            },
        ) from exc


# --- PMI ---


class IntegrationPlanBody(BaseModel):
    phase: str = "30_60_90"


class RiskRegisterBody(BaseModel):
    risk: dict[str, str] = Field(
        default_factory=lambda: {
            "title_ar": "مخاطر تقنية",
            "title_en": "Technical risk",
            "impact_ar": "متوسط",
            "impact_en": "Medium",
            "likelihood_ar": "منخفض",
            "likelihood_en": "Low",
        },
    )


@pmi_router.get(
    "/{deal_id}/day1-readiness",
    response_model=dict[str, Any],
    summary="Day-1 readiness",
)
async def pmi_day1_readiness(tenant_id: TenantIdQuery, deal_id: str) -> dict[str, Any]:
    try:
        r = await pmi_mgr.check_day1_readiness(tenant_id, deal_id)
        return r.model_dump()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Day-1 readiness check failed.",
                "message_ar": "فشل فحص جاهزية اليوم الأول.",
                "error": str(exc),
            },
        ) from exc


@pmi_router.post(
    "/{deal_id}/integration-plan",
    response_model=IntegrationPlan,
    summary="Integration plan",
)
async def pmi_integration_plan(
    tenant_id: TenantIdQuery,
    deal_id: str,
    body: IntegrationPlanBody = Body(default_factory=IntegrationPlanBody),
) -> IntegrationPlan:
    try:
        return await pmi_mgr.generate_integration_plan(tenant_id, deal_id, body.phase)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Integration plan generation failed.",
                "message_ar": "فشل إنشاء خطة التكامل.",
                "error": str(exc),
            },
        ) from exc


@pmi_router.post(
    "/{deal_id}/risk-register",
    response_model=RiskRegister,
    summary="Update risk register",
)
async def pmi_risk_register(
    tenant_id: TenantIdQuery,
    deal_id: str,
    body: RiskRegisterBody = Body(default_factory=RiskRegisterBody),
) -> RiskRegister:
    try:
        return await pmi_mgr.update_risk_register(tenant_id, deal_id, body.risk)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Risk register update failed.",
                "message_ar": "فشل تحديث سجل المخاطر.",
                "error": str(exc),
            },
        ) from exc


@pmi_router.get(
    "/{deal_id}/weekly-review",
    response_model=WeeklyReview,
    summary="Weekly review",
)
async def pmi_weekly_review(tenant_id: TenantIdQuery, deal_id: str) -> WeeklyReview:
    try:
        return await pmi_mgr.generate_weekly_review(tenant_id, deal_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Weekly review generation failed.",
                "message_ar": "فشل إنشاء المراجعة الأسبوعية.",
                "error": str(exc),
            },
        ) from exc


# --- Executive ---


class BoardMemoBody(BaseModel):
    topic: str = "Q2 portfolio review"
    language: str = "ar"


@executive_router.post(
    "/board-memo",
    response_model=BoardMemo,
    summary="Board memo",
)
async def executive_board_memo(
    tenant_id: TenantIdQuery,
    body: BoardMemoBody = Body(default_factory=BoardMemoBody),
) -> BoardMemo:
    try:
        return await executive_mgr.generate_board_memo(tenant_id, body.topic, body.language)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Board memo generation failed.",
                "message_ar": "فشل إنشاء مذكرة مجلس الإدارة.",
                "error": str(exc),
            },
        ) from exc


@executive_router.get(
    "/approval-center",
    response_model=list[ApprovalCenterItem],
    summary="Approval center",
)
async def executive_approval_center(tenant_id: TenantIdQuery) -> list[ApprovalCenterItem]:
    try:
        return await executive_mgr.get_approval_center(tenant_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Approval center lookup failed.",
                "message_ar": "فشل جلب مركز الموافقات.",
                "error": str(exc),
            },
        ) from exc


@executive_router.get(
    "/risk-heatmap",
    response_model=RiskHeatmap,
    summary="Risk heatmap",
)
async def executive_risk_heatmap(tenant_id: TenantIdQuery) -> RiskHeatmap:
    try:
        return await executive_mgr.get_risk_heatmap(tenant_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Risk heatmap failed.",
                "message_ar": "فشل جلب الخريطة الحرارية للمخاطر.",
                "error": str(exc),
            },
        ) from exc


@executive_router.get(
    "/policy-violations",
    response_model=list[PolicyViolation],
    summary="Policy violations",
)
async def executive_policy_violations(tenant_id: TenantIdQuery) -> list[PolicyViolation]:
    try:
        return await executive_mgr.get_policy_violations(tenant_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Policy violation lookup failed.",
                "message_ar": "فشل جلب مخالفات السياسة.",
                "error": str(exc),
            },
        ) from exc


@executive_router.get(
    "/pipeline",
    response_model=PipelineOverview,
    summary="Unified pipeline",
)
async def executive_pipeline(tenant_id: TenantIdQuery) -> PipelineOverview:
    try:
        return await executive_mgr.get_pipeline_overview(tenant_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Pipeline overview failed.",
                "message_ar": "فشل جلب نظرة الأنابيب الموحدة.",
                "error": str(exc),
            },
        ) from exc


@executive_router.get(
    "/next-actions",
    response_model=list[dict[str, Any]],
    summary="Next best actions",
)
async def executive_next_actions(tenant_id: TenantIdQuery) -> list[dict[str, Any]]:
    try:
        return await executive_mgr.get_next_best_actions(tenant_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message_en": "Next actions lookup failed.",
                "message_ar": "فشل جلب الإجراءات التالية.",
                "error": str(exc),
            },
        ) from exc

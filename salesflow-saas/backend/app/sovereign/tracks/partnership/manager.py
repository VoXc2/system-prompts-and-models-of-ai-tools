"""Partnership OS — alliances, channels, and partner lifecycle."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class PartnerCandidate(BaseModel):
    """A scored partner prospect surfaced for evaluation."""

    partner_id: str
    name_ar: str
    name_en: str
    headline_ar: str
    headline_en: str
    region: str
    fit_preview_ar: str
    fit_preview_en: str
    score: float = Field(ge=0.0, le=100.0, default=0.0)


class StrategicFitScore(BaseModel):
    """Strategic alignment score for a partner."""

    tenant_id: str
    partner_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    strategic_fit: float = Field(ge=0.0, le=100.0)
    dimensions: Dict[str, float] = Field(default_factory=dict)


class TermSheetDraft(BaseModel):
    """Draft commercial term sheet for a partner engagement."""

    tenant_id: str
    partner_id: str
    term_sheet_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    clauses: List[Dict[str, str]] = Field(default_factory=list)


class PartnerScorecard(BaseModel):
    """Operational and commercial scorecard for an active partner."""

    tenant_id: str
    partner_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    kpis: Dict[str, float] = Field(default_factory=dict)


class ContributionMarginReport(BaseModel):
    """Channel contribution margin view."""

    tenant_id: str
    partner_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    revenue_sar: float
    variable_cost_sar: float
    contribution_margin_pct: float


class PartnershipTrackManager:
    """Async manager for Partnership OS workflows."""

    async def scout_partners(
        self,
        tenant_id: str,
        criteria: Dict[str, Any],
    ) -> List[PartnerCandidate]:
        _ = criteria
        return [
            PartnerCandidate(
                partner_id=f"pc_{tenant_id}_1",
                name_ar="شريك قناة أول",
                name_en="Channel Partner Alpha",
                headline_ar="تغطية قوية في المدن الرئيسية",
                headline_en="Strong coverage in tier-1 cities",
                region="GCC",
                fit_preview_ar="ملاءمة عالية مع منتجات الخدمات المهنية.",
                fit_preview_en="High fit with professional services SKUs.",
                score=81.0,
            ),
            PartnerCandidate(
                partner_id=f"pc_{tenant_id}_2",
                name_ar="شريك استراتيجي ثانٍ",
                name_en="Strategic Partner Beta",
                headline_ar="وصول للقطاع الصحي",
                headline_en="Healthcare vertical access",
                region="KSA",
                fit_preview_ar="قنوات امتثال جاهزة للتوسع.",
                fit_preview_en="Compliance-ready routes to scale.",
                score=74.5,
            ),
        ]

    async def score_strategic_fit(
        self,
        tenant_id: str,
        partner_id: str,
    ) -> StrategicFitScore:
        return StrategicFitScore(
            tenant_id=tenant_id,
            partner_id=partner_id,
            title_ar="درجة الملاءمة الاستراتيجية",
            title_en="Strategic fit score",
            summary_ar="تقييم متعدد الأبعاد للثقافة والمنتج والامتثال.",
            summary_en="Multi-dimensional view across culture, product, and compliance.",
            strategic_fit=79.0,
            dimensions={"brand": 82.0, "gtm": 76.0, "risk": 88.0},
        )

    async def analyze_channel_economics(
        self,
        tenant_id: str,
        partner_id: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "partner_id": partner_id,
            "title_ar": "تحليل اقتصاديات القناة",
            "title_en": "Channel economics report",
            "summary_ar": "CAC المقدر وهامش المساهمة عبر القناة.",
            "summary_en": "Estimated CAC and contribution margin through the channel.",
            "cac_sar": 4200.0,
            "ltv_sar": 38_000.0,
        }

    async def recommend_alliance_structure(
        self,
        tenant_id: str,
        partner_id: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "partner_id": partner_id,
            "title_ar": "توصية هيكل التحالف",
            "title_en": "Alliance recommendation",
            "summary_ar": "نموذج مرجعي: موزع مع حماية إقليمية وشفافية تسعير.",
            "summary_en": "Reference design: distributor with territory guardrails and transparent pricing.",
            "structure": "tiered_reseller",
        }

    async def draft_term_sheet(
        self,
        tenant_id: str,
        partner_id: str,
    ) -> TermSheetDraft:
        ts_id = f"ts_{partner_id}"
        return TermSheetDraft(
            tenant_id=tenant_id,
            partner_id=partner_id,
            term_sheet_id=ts_id,
            title_ar="مسودة ورقة الشروط",
            title_en="Term sheet draft",
            summary_ar="شروط تجارية أولية جاهزة للمراجعة القانونية.",
            summary_en="Initial commercial terms ready for legal review.",
            clauses=[
                {
                    "topic_ar": "العمولات",
                    "topic_en": "Commissions",
                    "body_ar": "جدول عمولة متدرج حسب الحجم.",
                    "body_en": "Tiered commission schedule by volume.",
                }
            ],
        )

    async def route_for_approval(
        self,
        tenant_id: str,
        partner_id: str,
        term_sheet_id: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "partner_id": partner_id,
            "term_sheet_id": term_sheet_id,
            "title_ar": "توجيه للموافقة",
            "title_en": "Approval routing",
            "summary_ar": "تم إرسال الحزمة إلى المالية ثم الإدارة التنفيذية.",
            "summary_en": "Routed to finance then executive sponsor.",
            "approval_chain": ["finance", "legal", "exec_sponsor"],
        }

    async def activate_partner(
        self,
        tenant_id: str,
        partner_id: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "partner_id": partner_id,
            "title_ar": "تفعيل الشريك",
            "title_en": "Partner activation",
            "summary_ar": "تم تفعيل الحساب وربطه ببوابة الشريك.",
            "summary_en": "Account enabled and linked to partner portal.",
            "status": "active",
        }

    async def get_partner_scorecard(
        self,
        tenant_id: str,
        partner_id: str,
    ) -> PartnerScorecard:
        return PartnerScorecard(
            tenant_id=tenant_id,
            partner_id=partner_id,
            title_ar="بطاقة أداء الشريك",
            title_en="Partner scorecard",
            summary_ar="مؤشرات الأداء التجاري والتشغيلي للربع الحالي.",
            summary_en="Commercial and operational KPIs for the current quarter.",
            kpis={"pipeline_sar": 210_000.0, "win_rate": 0.31, "nps": 42.0},
        )

    async def track_contribution_margin(
        self,
        tenant_id: str,
        partner_id: str,
    ) -> ContributionMarginReport:
        revenue = 180_000.0
        var_cost = 63_000.0
        margin_pct = ((revenue - var_cost) / revenue) * 100 if revenue else 0.0
        return ContributionMarginReport(
            tenant_id=tenant_id,
            partner_id=partner_id,
            title_ar="تتبع هامش المساهمة",
            title_en="Contribution margin tracking",
            summary_ar="عرض هامش المساهمة بعد التكاليف المتغيرة للقناة.",
            summary_en="Contribution margin after channel variable costs.",
            revenue_sar=revenue,
            variable_cost_sar=var_cost,
            contribution_margin_pct=round(margin_pct, 2),
        )

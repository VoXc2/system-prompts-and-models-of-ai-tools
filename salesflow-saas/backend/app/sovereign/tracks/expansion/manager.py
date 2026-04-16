"""Expansion OS — geographic and market expansion."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class MarketOpportunity(BaseModel):
    """A market surfaced for expansion evaluation."""

    market_id: str
    name_ar: str
    name_en: str
    headline_ar: str
    headline_en: str
    tam_sar: float
    rationale_ar: str
    rationale_en: str


class ComplianceReadiness(BaseModel):
    """Regulatory and PDPL-style readiness for a market."""

    tenant_id: str
    market_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    score: float = Field(ge=0.0, le=100.0)
    gaps: List[Dict[str, str]] = Field(default_factory=list)


class LaunchReadiness(BaseModel):
    """Go-live readiness for a market launch."""

    tenant_id: str
    market_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    readiness_score: float = Field(ge=0.0, le=100.0)
    checklist: List[Dict[str, str]] = Field(default_factory=list)


class VarianceReport(BaseModel):
    """Actual versus forecast variance for a market."""

    tenant_id: str
    market_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    forecast_revenue_sar: float
    actual_revenue_sar: float
    variance_pct: float
    commentary_ar: str
    commentary_en: str


class ExpansionTrackManager:
    """Async manager for Expansion OS workflows."""

    async def scan_markets(
        self,
        tenant_id: str,
        criteria: Dict[str, Any],
    ) -> List[MarketOpportunity]:
        _ = (tenant_id, criteria)
        return [
            MarketOpportunity(
                market_id="ae_dubai",
                name_ar="الإمارات — دبي",
                name_en="UAE — Dubai",
                headline_ar="طلب قوي على الأتمتة التجارية",
                headline_en="Strong demand for commercial automation",
                tam_sar=320_000_000.0,
                rationale_ar="قرب جغرافي وتكامل بنكي ناضج.",
                rationale_en="Geographic proximity and mature banking rails.",
            ),
            MarketOpportunity(
                market_id="eg_cairo",
                name_ar="مصر — القاهرة",
                name_en="Egypt — Cairo",
                headline_ar="قاعدة مطورين كبيرة وتكلفة اكتساب معتدلة",
                headline_en="Large developer base with moderate CAC",
                tam_sar=210_000_000.0,
                rationale_ar="توسع طبيعي بعد تثبيت المملكة.",
                rationale_en="Natural next step after KSA consolidation.",
            ),
        ]

    async def prioritize_markets(
        self,
        tenant_id: str,
        market_ids: List[str],
    ) -> List[Dict[str, Any]]:
        ranked: List[Dict[str, Any]] = []
        for idx, mid in enumerate(market_ids):
            ranked.append(
                {
                    "tenant_id": tenant_id,
                    "market_id": mid,
                    "rank": idx + 1,
                    "title_ar": "ترتيب الأسواق",
                    "title_en": "Market prioritization",
                    "reason_ar": "درجة جاهزية وتوقيت دخول متوازن.",
                    "reason_en": "Balanced readiness and time-to-entry score.",
                }
            )
        return ranked

    async def assess_compliance_readiness(
        self,
        tenant_id: str,
        market_id: str,
    ) -> ComplianceReadiness:
        return ComplianceReadiness(
            tenant_id=tenant_id,
            market_id=market_id,
            title_ar="جاهزية الامتثال",
            title_en="Compliance readiness",
            summary_ar="تقييم PDPL/SAMA والمتطلبات المحلية للبيانات.",
            summary_en="Assessment of data residency, consent, and sector rules.",
            score=76.0,
            gaps=[
                {
                    "item_ar": "سياسة الاحتفاظ بالبيانات",
                    "item_en": "Data retention policy",
                    "action_ar": "تحديث السياسة وربطها بالتخزين الإقليمي.",
                    "action_en": "Update policy and bind to regional storage.",
                }
            ],
        )

    async def localize(
        self,
        tenant_id: str,
        market_id: str,
        content_type: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "market_id": market_id,
            "content_type": content_type,
            "title_ar": "خطة التوطين",
            "title_en": "Localization plan",
            "summary_ar": "RTL، العملة، والصياغة السعودية/المحلية حسب السياق.",
            "summary_en": "RTL, currency, and locale phrasing tuned for the market.",
            "tasks": ["copy_audit", "legal_disclaimers", "pricing_labels"],
        }

    async def plan_pricing_channel(
        self,
        tenant_id: str,
        market_id: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "market_id": market_id,
            "title_ar": "خطة التسعير والقنوات",
            "title_en": "Pricing and channel plan",
            "summary_ar": "شرائح SAR مع قنوات شراكة محلية مقترحة.",
            "summary_en": "SAR list bands with proposed local channel mix.",
            "channels": ["direct", "referral", "si_partner"],
        }

    async def check_launch_readiness(
        self,
        tenant_id: str,
        market_id: str,
    ) -> LaunchReadiness:
        return LaunchReadiness(
            tenant_id=tenant_id,
            market_id=market_id,
            title_ar="جاهزية الإطلاق",
            title_en="Launch readiness",
            summary_ar="جاهزية تشغيلية عالية مع بعض الفجوات في الدعم.",
            summary_en="Strong operational readiness with support gaps to close.",
            readiness_score=82.0,
            checklist=[
                {
                    "item_ar": "مركز الدعم",
                    "item_en": "Support center",
                    "status_ar": "قيد الإكمال",
                    "status_en": "In progress",
                }
            ],
        )

    async def evaluate_stop_loss(
        self,
        tenant_id: str,
        market_id: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "market_id": market_id,
            "title_ar": "تقييم وقف الخسارة",
            "title_en": "Stop-loss evaluation",
            "summary_ar": "لا حاجة لوقف كامل؛ تقليص استثمار تسويقي مقترح.",
            "summary_en": "No full exit; recommend marketing spend pullback.",
            "recommendation": "reduce_spend_20pct",
        }

    async def compare_actual_vs_forecast(
        self,
        tenant_id: str,
        market_id: str,
    ) -> VarianceReport:
        forecast = 4_200_000.0
        actual = 3_650_000.0
        var_pct = ((actual - forecast) / forecast) * 100 if forecast else 0.0
        return VarianceReport(
            tenant_id=tenant_id,
            market_id=market_id,
            title_ar="المقارنة بين الفعلي والتوقعات",
            title_en="Actual vs forecast variance",
            summary_ar="انحراف سلبي طفيف بسبب تأخير الإطلاق التسويقي.",
            summary_en="Slight negative variance driven by marketing launch delay.",
            forecast_revenue_sar=forecast,
            actual_revenue_sar=actual,
            variance_pct=round(var_pct, 2),
            commentary_ar="إعادة توجيه الحملة قد تستعيد المسار خلال ربعين.",
            commentary_en="Campaign reallocation likely restores trajectory within two quarters.",
        )

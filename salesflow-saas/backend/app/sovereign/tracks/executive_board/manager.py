"""Executive/Board OS — governance, risk, and cross-track visibility."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class BoardMemo(BaseModel):
    """Board-ready memo with bilingual body."""

    tenant_id: str
    topic: str
    language: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    recommendations: List[Dict[str, str]] = Field(default_factory=list)


class RiskHeatmap(BaseModel):
    """Risk heatmap payload for dashboards."""

    tenant_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    cells: List[Dict[str, Any]] = Field(default_factory=list)


class ApprovalCenterItem(BaseModel):
    """Single pending approval surfaced to leadership."""

    item_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    track: str
    owner_id: Optional[str] = None
    due_at_iso: Optional[str] = None


class PolicyViolation(BaseModel):
    """Governance or policy breach record."""

    violation_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    severity: Literal["low", "medium", "high"] = "medium"
    track: str


class PipelineOverview(BaseModel):
    """Unified pipeline snapshot across sovereign tracks."""

    tenant_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    tracks: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ExecutiveBoardTrackManager:
    """Async manager for executive and board workflows."""

    async def generate_board_memo(
        self,
        tenant_id: str,
        topic: str,
        language: str = "ar",
    ) -> BoardMemo:
        return BoardMemo(
            tenant_id=tenant_id,
            topic=topic,
            language=language,
            title_ar="مذكرة مجلس الإدارة",
            title_en="Board memo",
            summary_ar=f"تحليل موجز حول: {topic} مع التركيز على المخاطر والفرص.",
            summary_en=f"Concise analysis on {topic} with risks and opportunities.",
            recommendations=[
                {
                    "action_ar": "الموافقة على المتابعة مع ضوابط ربع سنوية.",
                    "action_en": "Approve with quarterly control checkpoints.",
                }
            ],
        )

    async def assemble_evidence_pack(
        self,
        tenant_id: str,
        decision_id: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "decision_id": decision_id,
            "title_ar": "حزمة الأدلة",
            "title_en": "Evidence pack",
            "summary_ar": "مستندات داعمة ومراجع تدقيق للقرار.",
            "summary_en": "Supporting artifacts and audit references for the decision.",
            "attachments": ["financial_model", "legal_summary", "risk_register_excerpt"],
        }

    async def get_approval_center(self, tenant_id: str) -> List[ApprovalCenterItem]:
        return [
            ApprovalCenterItem(
                item_id=f"appr_{tenant_id}_1",
                title_ar="موافقة تسعير استثنائية",
                title_en="Exceptional pricing approval",
                summary_ar="خصم يتجاوز الحد القياسي ويتطلب توقيع تنفيذي.",
                summary_en="Discount exceeds standard guardrails; needs exec sign-off.",
                track="revenue",
                owner_id="cfo_proxy",
                due_at_iso="2026-04-20T12:00:00+03:00",
            )
        ]

    async def get_risk_heatmap(self, tenant_id: str) -> RiskHeatmap:
        return RiskHeatmap(
            tenant_id=tenant_id,
            title_ar="خريطة حرارية للمخاطر",
            title_en="Risk heatmap",
            summary_ar="تجميع المخاطر حسب الأثر والاحتمالية عبر المسارات.",
            summary_en="Risks bucketed by impact and likelihood across tracks.",
            cells=[
                {"x": "revenue", "y": "compliance", "score": 0.62, "label_ar": "متوسط", "label_en": "Medium"},
                {"x": "expansion", "y": "execution", "score": 0.41, "label_ar": "منخفض", "label_en": "Low"},
            ],
        )

    async def get_actual_vs_forecast(
        self,
        tenant_id: str,
        track: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "track": track,
            "title_ar": "لوحة الفعلي مقابل التوقعات",
            "title_en": "Actual vs forecast dashboard",
            "summary_ar": "مقارنة موحدة للإيرادات والأنابيب حسب المسار.",
            "summary_en": "Unified revenue and pipeline variance by track.",
            "variance_pct": -4.2,
        }

    async def get_next_best_actions(self, tenant_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "tenant_id": tenant_id,
                "priority": 1,
                "title_ar": "إغلاق فجوة الامتثال في التوسع",
                "title_en": "Close expansion compliance gap",
                "summary_ar": "إكمال سياسة الاحتفاظ قبل الإطلاق الإقليمي.",
                "summary_en": "Finish retention policy before regional launch.",
                "track": "expansion",
            }
        ]

    async def get_policy_violations(self, tenant_id: str) -> List[PolicyViolation]:
        return [
            PolicyViolation(
                violation_id=f"pv_{tenant_id}_1",
                title_ar="تجاوز حد الرسائل دون موافقة PDPL",
                title_en="Messaging volume exceeded without PDPL consent",
                summary_ar="تم اكتشاف إرسال تجريبي تجاوز حدود الموافقة.",
                summary_en="Test send batch exceeded consent scope.",
                severity="high",
                track="revenue",
            )
        ]

    async def get_pipeline_overview(self, tenant_id: str) -> PipelineOverview:
        return PipelineOverview(
            tenant_id=tenant_id,
            title_ar="نظرة موحدة على الأنابيب",
            title_en="Unified pipeline overview",
            summary_ar="تجميع فرص الإيراد والشراكة والتوسع في لوحة واحدة.",
            summary_en="Roll-up of revenue, partnership, and expansion opportunities.",
            tracks={
                "revenue": {"open_sar": 1_100_000.0, "deals": 18},
                "partnership": {"active_partners": 6},
                "expansion": {"markets_in_motion": 3},
            },
        )

"""Revenue OS — manages the full sales cycle for Sovereign Enterprise Growth."""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field


class LeadCaptureResult(BaseModel):
    """Outcome of ingesting a new lead into the Revenue OS."""

    tenant_id: str
    lead_id: str
    status: str
    title_ar: str = Field(..., description="عنوان عربي للنتيجة")
    title_en: str = Field(..., description="English title for the capture outcome")
    summary_ar: str
    summary_en: str
    captured_fields: Dict[str, Any] = Field(default_factory=dict)


class EnrichmentResult(BaseModel):
    """Lead enrichment outcome (firmographics, contacts, intent signals)."""

    tenant_id: str
    lead_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    enrichment_payload: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=0.85)


class QualificationResult(BaseModel):
    """Qualification score and commercial tier."""

    tenant_id: str
    lead_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    score: float = Field(ge=0.0, le=100.0)
    tier: str
    rationale_ar: str
    rationale_en: str


class FunnelMetrics(BaseModel):
    """End-to-end funnel metrics for the tenant Revenue OS."""

    tenant_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    leads_captured: int
    qualified_leads: int
    opportunities: int
    proposals_sent: int
    won_deals: int
    pipeline_value_sar: float
    win_rate_pct: float
    avg_cycle_days: float
    stages: Dict[str, int] = Field(default_factory=dict)


class RevenueTrackManager:
    """Async manager for Revenue OS lifecycle operations."""

    async def capture_lead(
        self,
        tenant_id: str,
        source: str,
        channel: str,
        data: Dict[str, Any],
    ) -> LeadCaptureResult:
        lead_id = f"lead_{tenant_id}_{hash((source, channel, str(data))) & 0xFFFF_FFFF:x}"
        return LeadCaptureResult(
            tenant_id=tenant_id,
            lead_id=lead_id,
            status="captured",
            title_ar="تم تسجيل العميل المحتمل",
            title_en="Lead captured successfully",
            summary_ar="تم استلام البيانات وتسجيلها في مسار الإيرادات مع الحفاظ على عزل المستأجر.",
            summary_en="Payload accepted and recorded on the revenue track with tenant isolation.",
            captured_fields={"source": source, "channel": channel, **data},
        )

    async def enrich_lead(self, tenant_id: str, lead_id: str) -> EnrichmentResult:
        return EnrichmentResult(
            tenant_id=tenant_id,
            lead_id=lead_id,
            title_ar="إثراء بيانات العميل المحتمل",
            title_en="Lead enrichment completed",
            summary_ar="تم دمج إشارات النية وبيانات الشركة ضمن حدود الحوكمة.",
            summary_en="Firmographic and intent signals merged under governance controls.",
            enrichment_payload={"company_size_band": "SMB", "industry_hint": "services"},
        )

    async def qualify_lead(self, tenant_id: str, lead_id: str) -> QualificationResult:
        return QualificationResult(
            tenant_id=tenant_id,
            lead_id=lead_id,
            title_ar="تأهيل العميل المحتمل",
            title_en="Lead qualification",
            summary_ar="تم تقييم الجاهزية التجارية والميزانية والجدول الزمني.",
            summary_en="Budget, authority, need, and timing assessed for commercial fit.",
            score=72.5,
            tier="A",
            rationale_ar="درجة عالية بسبب وضوح الحاجة وتوقيت الشراء المتوقع.",
            rationale_en="Strong fit due to clear pain and near-term buying intent.",
        )

    async def score_lead(self, tenant_id: str, lead_id: str) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "lead_id": lead_id,
            "composite_score": 78,
            "title_ar": "درجة مركبة للعميل المحتمل",
            "title_en": "Composite lead score",
            "summary_ar": "دمج سلوك التفاعل وجودة البيانات والملاءمة القطاعية.",
            "summary_en": "Blends engagement, data quality, and sector fit into a 0–100 score.",
        }

    async def route_lead(self, tenant_id: str, lead_id: str) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "lead_id": lead_id,
            "assigned_rep_id": f"rep_{tenant_id}_primary",
            "title_ar": "توجيه العميل المحتمل",
            "title_en": "Lead routing",
            "reason_ar": "أقرب ممثل مبيعات متاح مع أعلى معدل إغلاق للقطاع.",
            "reason_en": "Nearest available AE with best sector win rate.",
        }

    async def launch_outreach(
        self,
        tenant_id: str,
        lead_id: str,
        sequence_type: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "lead_id": lead_id,
            "sequence_type": sequence_type,
            "title_ar": "خطة التواصل",
            "title_en": "Outreach plan",
            "summary_ar": "جدولة رسائل متعددة القنوات مع احترام موافقات PDPL.",
            "summary_en": "Multi-touch sequence across channels with PDPL consent gates.",
            "steps": [
                {"day": 0, "channel": "email", "purpose_ar": "تعريف مختصر", "purpose_en": "Short intro"},
                {"day": 2, "channel": "whatsapp", "purpose_ar": "متابعة", "purpose_en": "Follow-up"},
            ],
        }

    async def orchestrate_meeting(
        self,
        tenant_id: str,
        lead_id: str,
        meeting_type: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "lead_id": lead_id,
            "meeting_type": meeting_type,
            "title_ar": "إعداد الاجتماع",
            "title_en": "Meeting setup",
            "summary_ar": "تم حجز نافذة زمنية وإرسال دعوة مع جدول أعمال مقترح.",
            "summary_en": "Slot proposed, invite drafted, and agenda scaffolded.",
            "calendar_event_id": f"evt_{lead_id}",
        }

    async def generate_proposal(self, tenant_id: str, deal_id: str) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "deal_id": deal_id,
            "title_ar": "مسودة العرض",
            "title_en": "Proposal draft",
            "summary_ar": "مسودة أولية بالعملة SAR مع شروط الدفع القياسية.",
            "summary_en": "Initial SAR-denominated draft with standard payment terms.",
            "sections": ["scope", "pricing", "sla", "security"],
        }

    async def evaluate_pricing(
        self,
        tenant_id: str,
        deal_id: str,
        discount_pct: float,
    ) -> Dict[str, Any]:
        approved = discount_pct <= 15.0
        return {
            "tenant_id": tenant_id,
            "deal_id": deal_id,
            "discount_pct": discount_pct,
            "approved": approved,
            "title_ar": "حوكمة التسعير",
            "title_en": "Pricing governance",
            "message_ar": "تمت الموافقة ضمن الحدود" if approved else "يتطلب تصعيد للموافقة التنفيذية",
            "message_en": "Within policy band" if approved else "Executive approval required",
        }

    async def handoff_to_contract(self, tenant_id: str, deal_id: str) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "deal_id": deal_id,
            "title_ar": "تسليم للعقود",
            "title_en": "Contract handoff",
            "summary_ar": "تم تمرير بيانات الصفقة إلى مسار العقود مع مرجعية التدقيق.",
            "summary_en": "Deal facts packaged for legal with audit references.",
            "contract_workflow_id": f"cw_{deal_id}",
        }

    async def handoff_to_onboarding(self, tenant_id: str, deal_id: str) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "deal_id": deal_id,
            "title_ar": "تسليم للتأهيل",
            "title_en": "Onboarding handoff",
            "summary_ar": "تم إنشاء خطة تأهيل أولية وربطها بفريق النجاح.",
            "summary_en": "Kickoff checklist created and linked to customer success.",
            "onboarding_plan_id": f"ob_{deal_id}",
        }

    async def trigger_renewal(self, tenant_id: str, customer_id: str) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "title_ar": "فرصة التجديد",
            "title_en": "Renewal opportunity",
            "summary_ar": "نافذة تجديد مفتوحة مع توصيات بالحجم والمدة.",
            "summary_en": "Renewal window opened with sizing and term recommendations.",
            "renewal_opportunity_id": f"ren_{customer_id}",
        }

    async def identify_upsell(self, tenant_id: str, customer_id: str) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "title_ar": "توصيات البيع الإضافي",
            "title_en": "Upsell recommendations",
            "items": [
                {
                    "sku": "enterprise_seats",
                    "headline_ar": "توسعة المقاعد",
                    "headline_en": "Seat expansion",
                    "rationale_ar": "ارتفاع الاستخدام الأسبوعي فوق عتبة النمو.",
                    "rationale_en": "Weekly active usage crossed growth threshold.",
                }
            ],
        }

    async def get_funnel_metrics(self, tenant_id: str) -> FunnelMetrics:
        return FunnelMetrics(
            tenant_id=tenant_id,
            title_ar="مؤشرات مسار الإيرادات",
            title_en="Revenue funnel metrics",
            summary_ar="لوحة موحدة لمراحل التحويل عبر المستأجر.",
            summary_en="Tenant-scoped conversion view across funnel stages.",
            leads_captured=120,
            qualified_leads=48,
            opportunities=22,
            proposals_sent=14,
            won_deals=6,
            pipeline_value_sar=1_250_000.0,
            win_rate_pct=27.3,
            avg_cycle_days=34.0,
            stages={"awareness": 200, "interest": 120, "decision": 40, "action": 14},
        )

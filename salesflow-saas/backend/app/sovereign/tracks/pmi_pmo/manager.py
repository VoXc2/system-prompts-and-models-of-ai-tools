"""PMI/PMO OS — post-merger integration and program governance."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, Field


class Day1Readiness(BaseModel):
    """Day-1 operational readiness checklist."""

    tenant_id: str
    deal_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    readiness_score: float = Field(ge=0.0, le=100.0)
    items: List[Dict[str, str]] = Field(default_factory=list)


class IntegrationPlan(BaseModel):
    """Phased integration plan (30/60/90 style)."""

    tenant_id: str
    deal_id: str
    phase: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    milestones: List[Dict[str, str]] = Field(default_factory=list)


class DependencyGraph(BaseModel):
    """Program dependency graph snapshot."""

    tenant_id: str
    plan_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, str]] = Field(default_factory=list)


class SynergyRealization(BaseModel):
    """Synergy realization tracking."""

    tenant_id: str
    deal_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    realized_sar: float
    planned_sar: float
    realization_pct: float


class RiskRegister(BaseModel):
    """Risk register state for an integration program."""

    tenant_id: str
    deal_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    risks: List[Dict[str, str]] = Field(default_factory=list)


class WeeklyReview(BaseModel):
    """Executive weekly review pack."""

    tenant_id: str
    deal_id: str
    title_ar: str
    title_en: str
    summary_ar: str
    summary_en: str
    highlights: List[Dict[str, str]] = Field(default_factory=list)
    decisions_needed: List[Dict[str, str]] = Field(default_factory=list)


class PMITrackManager:
    """Async manager for PMI/PMO workflows."""

    async def check_day1_readiness(self, tenant_id: str, deal_id: str) -> Day1Readiness:
        return Day1Readiness(
            tenant_id=tenant_id,
            deal_id=deal_id,
            title_ar="جاهزية اليوم الأول",
            title_en="Day-1 readiness",
            summary_ar="قائمة تحقق للأنظمة والموارد البشرية والاتصالات.",
            summary_en="Systems, HR, and communications readiness checklist.",
            readiness_score=74.0,
            items=[
                {
                    "name_ar": "الهوية والوصول",
                    "name_en": "Identity & access",
                    "status_ar": "جاهز",
                    "status_en": "Ready",
                },
                {
                    "name_ar": "الدعم للعملاء",
                    "name_en": "Customer support",
                    "status_ar": "يحتاج متابعة",
                    "status_en": "Needs follow-up",
                },
            ],
        )

    async def generate_integration_plan(
        self,
        tenant_id: str,
        deal_id: str,
        phase: str,
    ) -> IntegrationPlan:
        return IntegrationPlan(
            tenant_id=tenant_id,
            deal_id=deal_id,
            phase=phase,
            title_ar="خطة التكامل",
            title_en="Integration plan",
            summary_ar="خطة مرحلية مع بوابات قبول واضحة.",
            summary_en="Phased plan with crisp acceptance gates.",
            milestones=[
                {
                    "name_ar": "تثبيت القيادة",
                    "name_en": "Leadership stabilization",
                    "due_ar": "30 يوماً",
                    "due_en": "30 days",
                },
                {
                    "name_ar": "توحيد الأنظمة",
                    "name_en": "Systems convergence",
                    "due_ar": "60 يوماً",
                    "due_en": "60 days",
                },
            ],
        )

    async def track_dependencies(self, tenant_id: str, plan_id: str) -> DependencyGraph:
        return DependencyGraph(
            tenant_id=tenant_id,
            plan_id=plan_id,
            title_ar="رسم بياني للتبعيات",
            title_en="Dependency graph",
            summary_ar="عرض المسارات الحرجة بين فرق العمل.",
            summary_en="Critical path view across workstreams.",
            nodes=[
                {"id": "hr", "label_ar": "الموارد البشرية", "label_en": "HR"},
                {"id": "it", "label_ar": "تقنية المعلومات", "label_en": "IT"},
            ],
            edges=[{"from": "hr", "to": "it", "type": "blocking"}],
        )

    async def assign_owners(
        self,
        tenant_id: str,
        plan_id: str,
        assignments: Dict[str, str],
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "plan_id": plan_id,
            "title_ar": "تعيين المالكين",
            "title_en": "Owner assignment",
            "summary_ar": "تم ربط مهام الخطة بمالكين واضحين.",
            "summary_en": "Plan tasks bound to named owners.",
            "assignments": assignments,
        }

    async def escalate(
        self,
        tenant_id: str,
        plan_id: str,
        issue: str,
    ) -> Dict[str, Any]:
        return {
            "tenant_id": tenant_id,
            "plan_id": plan_id,
            "issue": issue,
            "title_ar": "تصعيد المشكلة",
            "title_en": "Escalation",
            "summary_ar": "تم فتح مسار تصعيد للجنة التكامل التنفيذية.",
            "summary_en": "Opened executive integration committee path.",
            "ticket_id": f"esc_{plan_id}",
        }

    async def track_synergy_realization(
        self,
        tenant_id: str,
        deal_id: str,
    ) -> SynergyRealization:
        planned = 8_000_000.0
        realized = 2_400_000.0
        pct = (realized / planned) * 100 if planned else 0.0
        return SynergyRealization(
            tenant_id=tenant_id,
            deal_id=deal_id,
            title_ar="تحقيق التآزر",
            title_en="Synergy realization",
            summary_ar="تتبع شهري للتآزر الإيرادي والتكلفة مقابل الخطة.",
            summary_en="Monthly revenue and cost synergy tracking vs plan.",
            realized_sar=realized,
            planned_sar=planned,
            realization_pct=round(pct, 2),
        )

    async def update_risk_register(
        self,
        tenant_id: str,
        deal_id: str,
        risk: Dict[str, str],
    ) -> RiskRegister:
        return RiskRegister(
            tenant_id=tenant_id,
            deal_id=deal_id,
            title_ar="سجل المخاطر",
            title_en="Risk register",
            summary_ar="تمت إضافة/تحديث خطر مع تصنيف الأثر والاحتمالية.",
            summary_en="Risk appended or updated with impact and likelihood.",
            risks=[risk],
        )

    async def generate_weekly_review(self, tenant_id: str, deal_id: str) -> WeeklyReview:
        return WeeklyReview(
            tenant_id=tenant_id,
            deal_id=deal_id,
            title_ar="حزمة المراجعة الأسبوعية",
            title_en="Weekly executive review",
            summary_ar="ملخص للإدارة التنفيذية مع قرارات مطلوبة.",
            summary_en="Executive digest with explicit decisions required.",
            highlights=[
                {
                    "topic_ar": "التقدم",
                    "topic_en": "Progress",
                    "detail_ar": "اكتمال 62٪ من مهام المرحلة الأولى.",
                    "detail_en": "62% of phase-1 tasks complete.",
                }
            ],
            decisions_needed=[
                {
                    "topic_ar": "استثناء تقني",
                    "topic_en": "Technical exception",
                    "ask_ar": "الموافقة على نافذة تقنية مؤقتة.",
                    "ask_en": "Approve a temporary technical waiver.",
                }
            ],
        )

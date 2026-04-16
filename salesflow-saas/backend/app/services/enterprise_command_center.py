from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategic_deal import DealMatch, MatchStatus, StrategicDeal, DealStatus, DealType
from app.models.user import User
from app.openclaw.memory_bridge import memory_bridge
from app.openclaw.media_bridge import media_bridge
from app.openclaw.observability_bridge import observability_bridge
from app.services.model_router import ModelRouter
from app.services.operations_hub import count_events_since, count_pending_approvals, list_integration_connectors


class CommandCenterHeadline(BaseModel):
    system_name_ar: str
    subtitle_ar: str
    operating_mode: str
    status: str
    readiness_percent: float
    traceability_status: str
    policy_posture: str


class CommandCenterMetric(BaseModel):
    key: str
    label_ar: str
    value: float | int | str
    unit: Optional[str] = None
    status: str = "info"


class CommandCenterPlane(BaseModel):
    key: str
    title_ar: str
    status: str
    description_ar: str
    backbone: List[str] = Field(default_factory=list)
    live_signals: List[str] = Field(default_factory=list)
    control_focus: List[str] = Field(default_factory=list)


class OperatingSystemCard(BaseModel):
    key: str
    title_ar: str
    status: str
    automation_summary_ar: str
    auto_scope: List[str] = Field(default_factory=list)
    approval_scope: List[str] = Field(default_factory=list)
    coverage_metrics: Dict[str, int] = Field(default_factory=dict)


class GovernanceClass(BaseModel):
    key: str
    title_ar: str
    description_ar: str
    examples: List[str] = Field(default_factory=list)


class CommitmentGate(BaseModel):
    action: str
    title_ar: str
    approval_class: str
    reversibility_class: str
    sensitivity_class: str
    why_ar: str


class SurfaceCard(BaseModel):
    slug: str
    title_ar: str
    plane: str
    status: str
    backing_routes: List[str] = Field(default_factory=list)
    status_reason_ar: str


class ModelProviderCard(BaseModel):
    provider: str
    label_ar: str
    task_count: int
    task_types: List[str] = Field(default_factory=list)


class ModelRoutingSummary(BaseModel):
    providers: List[ModelProviderCard] = Field(default_factory=list)
    benchmark_dimensions: List[str] = Field(default_factory=list)
    recommended_fabric_ar: str


class ComplianceControl(BaseModel):
    framework: str
    control_id: str
    title_ar: str
    status: str
    evidence: List[str] = Field(default_factory=list)


class GapItem(BaseModel):
    slug: str
    title_ar: str
    severity: str
    status_needed: str
    next_step_ar: str


class EnterpriseCommandCenterResponse(BaseModel):
    demo_mode: bool
    headline: CommandCenterHeadline
    metrics: List[CommandCenterMetric] = Field(default_factory=list)
    planes: List[CommandCenterPlane] = Field(default_factory=list)
    operating_systems: List[OperatingSystemCard] = Field(default_factory=list)
    approval_classes: List[GovernanceClass] = Field(default_factory=list)
    reversibility_classes: List[GovernanceClass] = Field(default_factory=list)
    sensitivity_classes: List[GovernanceClass] = Field(default_factory=list)
    commitment_gates: List[CommitmentGate] = Field(default_factory=list)
    surfaces: List[SurfaceCard] = Field(default_factory=list)
    model_routing: ModelRoutingSummary
    saudi_compliance: List[ComplianceControl] = Field(default_factory=list)
    gaps: List[GapItem] = Field(default_factory=list)
    note_ar: str


def _demo_connectors() -> List[Dict[str, Any]]:
    return [
        {"connector_key": "crm_salesforce", "display_name_ar": "Salesforce CRM", "status": "ok"},
        {"connector_key": "whatsapp_cloud", "display_name_ar": "واتساب Cloud API", "status": "degraded"},
        {"connector_key": "stripe_billing", "display_name_ar": "Stripe - الفوترة", "status": "ok"},
        {"connector_key": "email_sync", "display_name_ar": "مزامنة البريد", "status": "ok"},
    ]


def _status_rank(status: str) -> int:
    return {"live": 3, "partial": 2, "planned": 1}.get(status, 0)


def _summarize_overall_status(readiness_percent: float, gaps: List[GapItem]) -> str:
    high_severity = sum(1 for item in gaps if item.severity == "high")
    if readiness_percent >= 85 and high_severity == 0:
        return "live"
    if readiness_percent >= 60:
        return "partial"
    return "planned"


def _build_model_routing_summary() -> ModelRoutingSummary:
    groups: Dict[str, List[str]] = {}
    counts = Counter(ModelRouter.ROUTING_TABLE.values())
    for task_type, provider in ModelRouter.ROUTING_TABLE.items():
        groups.setdefault(provider, []).append(task_type)

    labels = {
        "glm5": "قرارات المبيعات والاستراتيجية",
        "groq": "التصنيف والسرعة التشغيلية",
        "claude": "الصياغة والعروض",
        "gemini": "البحث والتحليل",
        "deepseek": "التنفيذ البرمجي والتكامل",
    }
    providers = [
        ModelProviderCard(
            provider=provider,
            label_ar=labels.get(provider, provider),
            task_count=counts.get(provider, 0),
            task_types=sorted(groups.get(provider, [])),
        )
        for provider in sorted(groups.keys())
    ]
    return ModelRoutingSummary(
        providers=providers,
        benchmark_dimensions=[
            "latency",
            "success_rate",
            "schema_adherence",
            "tool_call_reliability",
            "contradiction_rate",
            "arabic_memo_quality",
            "cost_per_successful_task",
        ],
        recommended_fabric_ar="الراوتر الحالي موجود، لكن السيادة الفعلية تكتمل عند إضافة benchmark harness حي يقيّم النماذج على المهام العربية والأدوات.",
    )


def _build_governance() -> Dict[str, List[BaseModel]]:
    approval_classes = [
        GovernanceClass(
            key="A0",
            title_ar="تنفيذ تلقائي",
            description_ar="أفعال قابلة للعكس ومنخفضة المخاطر يمكن للنظام تنفيذها دون انتظار بشري.",
            examples=["lead capture", "enrichment", "routing", "reminders"],
        ),
        GovernanceClass(
            key="A1",
            title_ar="اعتماد مدير",
            description_ar="أفعال خارجية متوسطة الأثر تحتاج موافقة مالك المسار أو المدير.",
            examples=["term sheet draft send", "partner activation", "discount exception"],
        ),
        GovernanceClass(
            key="A2",
            title_ar="اعتماد تنفيذي",
            description_ar="التزامات استراتيجية أو قانونية أو مالية يجب أن تمر عبر executive / legal / board gate.",
            examples=["M&A offer", "exclusive partnership", "market commitment", "prod rollout"],
        ),
    ]
    reversibility_classes = [
        GovernanceClass(
            key="R1",
            title_ar="قابل للعكس",
            description_ar="يمكن التراجع عنه بسرعة وبأثر محدود.",
            examples=["follow-up sequence", "memo draft", "connector retry"],
        ),
        GovernanceClass(
            key="R2",
            title_ar="شبه غير قابل للعكس",
            description_ar="ينشئ التزاماً خارجياً أو يغير علاقة تجارية أو تشغيلية.",
            examples=["term sheet send", "launch canary", "partner activation"],
        ),
        GovernanceClass(
            key="R3",
            title_ar="غير قابل للعكس عملياً",
            description_ar="يخلق أثراً قانونياً أو مالياً أو سمعة يصعب سحبه.",
            examples=["final signature", "M&A offer", "production release"],
        ),
    ]
    sensitivity_classes = [
        GovernanceClass(
            key="S1",
            title_ar="منخفض الحساسية",
            description_ar="بيانات وتشغيل داخلي عادي.",
            examples=["pipeline telemetry", "connector health", "task assignment"],
        ),
        GovernanceClass(
            key="S2",
            title_ar="حساسية تجارية",
            description_ar="شروط وصفقات وشراكات وأرقام مالية.",
            examples=["discount margins", "channel economics", "board memo"],
        ),
        GovernanceClass(
            key="S3",
            title_ar="عالي الحساسية",
            description_ar="بيانات شخصية أو مستندات قانونية أو تبادل بيانات حساس.",
            examples=["PDPL data sharing", "DD room docs", "signature packet"],
        ),
    ]
    commitment_gates = [
        CommitmentGate(
            action="send_term_sheet",
            title_ar="إرسال ورقة شروط",
            approval_class="A1",
            reversibility_class="R2",
            sensitivity_class="S2",
            why_ar="ينشئ التزاماً خارجياً أولياً ويجب أن يمر عبر approval center.",
        ),
        CommitmentGate(
            action="activate_strategic_partner",
            title_ar="تفعيل شريك استراتيجي",
            approval_class="A1",
            reversibility_class="R2",
            sensitivity_class="S2",
            why_ar="التفعيل يفتح التزامات تشغيلية وتجارية بين الطرفين.",
        ),
        CommitmentGate(
            action="send_mna_offer",
            title_ar="إرسال عرض استحواذ",
            approval_class="A2",
            reversibility_class="R3",
            sensitivity_class="S3",
            why_ar="قرار مجلس/استثمار عالي الحساسية وغير قابل للعكس عملياً.",
        ),
        CommitmentGate(
            action="launch_new_market",
            title_ar="إطلاق دخول سوق جديد",
            approval_class="A2",
            reversibility_class="R2",
            sensitivity_class="S2",
            why_ar="يرتبط بإنفاق وقنوات وشركاء ومخاطر امتثال محلية.",
        ),
        CommitmentGate(
            action="rollout_production",
            title_ar="نشر إلى الإنتاج",
            approval_class="A2",
            reversibility_class="R3",
            sensitivity_class="S2",
            why_ar="ينبغي ربطه بحماية البيئات وprovenance وrelease gate.",
        ),
    ]
    return {
        "approval_classes": approval_classes,
        "reversibility_classes": reversibility_classes,
        "sensitivity_classes": sensitivity_classes,
        "commitment_gates": commitment_gates,
    }


def _build_surfaces() -> List[SurfaceCard]:
    return [
        SurfaceCard(slug="executive-room", title_ar="Executive Room", plane="decision", status="live", backing_routes=["/api/v1/autonomous-foundation/dashboard/executive-roi", "/dashboard?tab=analytics"], status_reason_ar="موجود عبر Executive ROI وAnalytics View ويعرض أثر القرار ومؤشرات القيادة."),
        SurfaceCard(slug="approval-center", title_ar="Approval Center", plane="trust", status="live", backing_routes=["/api/v1/operations/approvals", "/api/v1/operations/approvals/sla"], status_reason_ar="موجود فعلياً عبر approvals + SLA escalation metadata."),
        SurfaceCard(slug="evidence-pack-viewer", title_ar="Evidence Pack Viewer", plane="trust", status="partial", backing_routes=["/api/v1/operations/snapshot", "/api/v1/operations/domain-events"], status_reason_ar="توجد أحداث وتدقيق وذاكرة، لكن لا توجد شاشة مخصصة لتجميع evidence packs بعد."),
        SurfaceCard(slug="partner-room", title_ar="Partner Room", plane="execution", status="partial", backing_routes=["/api/v1/strategic-deals", "/api/v1/strategic-deals/matches"], status_reason_ar="الـ API موجودة، لكن الواجهة المخصصة للشركاء لم تُربط كتجربة مستقلة بعد."),
        SurfaceCard(slug="dd-room", title_ar="DD Room", plane="execution", status="partial", backing_routes=["/api/v1/strategic-deals", "/api/v1/operations/domain-events"], status_reason_ar="مسارات due diligence مدعومة بالبيانات، لكن غرفة DD التفاعلية لم تكتمل بعد."),
        SurfaceCard(slug="risk-board", title_ar="Risk Board", plane="trust", status="partial", backing_routes=["/api/v1/operations/snapshot"], status_reason_ar="المخاطر تظهر عبر approval SLA والكناري والتكاملات، لكن heatmap موحّد للمخاطر لم يُفصل بعد."),
        SurfaceCard(slug="policy-violations-board", title_ar="Policy Violations Board", plane="trust", status="partial", backing_routes=["/api/v1/autonomous-foundation/openclaw/policy/check", "/api/v1/operations/approvals"], status_reason_ar="المحرك والسياسات موجودان، لكن لوحة الانتهاكات المجمعة ما زالت جزئية."),
        SurfaceCard(slug="actual-vs-forecast-dashboard", title_ar="Actual vs Forecast Dashboard", plane="decision", status="live", backing_routes=["/api/v1/autonomous-foundation/intelligence/predictive", "/api/v1/autonomous-foundation/dashboard/executive-roi"], status_reason_ar="موجودة عبر predictive + ROI وتخدم القراءة التنفيذية الحالية."),
        SurfaceCard(slug="revenue-funnel-control-center", title_ar="Revenue Funnel Control Center", plane="decision", status="live", backing_routes=["/dashboard?tab=pipeline", "/dashboard?tab=scoring"], status_reason_ar="الواجهة الحالية تعرض pipeline وscoring وSales OS بشكل فعلي."),
        SurfaceCard(slug="partnership-scorecards", title_ar="Partnership Scorecards", plane="decision", status="partial", backing_routes=["/api/v1/strategic-deals/analytics/overview"], status_reason_ar="تحليلات الشراكات موجودة backend لكن scorecard واجهي منفصل لم يكتمل."),
        SurfaceCard(slug="mna-pipeline-board", title_ar="M&A Pipeline Board", plane="execution", status="partial", backing_routes=["/api/v1/strategic-deals", "/api/v1/strategic-deals/analytics/overview"], status_reason_ar="توجد deal types للاستحواذ ومسارات تفاوض وتحليل، لكن board مخصص للاستحواذات لم يُربط بعد."),
        SurfaceCard(slug="expansion-launch-console", title_ar="Expansion Launch Console", plane="operating", status="partial", backing_routes=["/api/v1/autonomous-foundation/integrations/live-readiness", "/api/v1/autonomous-foundation/integrations/go-live-gate"], status_reason_ar="بوابة readiness حية، لكن launch console متعدد الأسواق لم يكتمل بعد."),
        SurfaceCard(slug="pmi-30-60-90-engine", title_ar="PMI 30/60/90 Engine", plane="execution", status="partial", backing_routes=["/api/v1/operations/snapshot"], status_reason_ar="يوجد execution durable جزئي عبر OpenClaw، لكن engine مخصص لـ 30/60/90 لم يُعرض كسطح مستقل بعد."),
        SurfaceCard(slug="tool-verification-ledger", title_ar="Tool Verification Ledger", plane="trust", status="live", backing_routes=["/api/v1/operations/domain-events", "/api/v1/operations/audit-logs"], status_reason_ar="سجل التتبع والتدقيق والأحداث موجود ويغطي verification trail الأساسي."),
        SurfaceCard(slug="connector-health-board", title_ar="Connector Health Board", plane="data", status="live", backing_routes=["/api/v1/operations/integration-connectors", "/api/v1/operations/snapshot"], status_reason_ar="موجود فعلياً ضمن Full Auto Ops مع حالات تكامل واضحة."),
        SurfaceCard(slug="release-gate-dashboard", title_ar="Release Gate Dashboard", plane="operating", status="live", backing_routes=["/api/v1/autonomous-foundation/integrations/go-live-gate"], status_reason_ar="بوابة الإطلاق التجاري موجودة وتعيد readiness + blocked reasons."),
        SurfaceCard(slug="saudi-compliance-matrix", title_ar="Saudi Compliance Matrix", plane="trust", status="live", backing_routes=["/api/v1/operations/command-center"], status_reason_ar="الواجهة الجديدة تجمع PDPL / NCA / AI governance control mapping في مكان واحد."),
        SurfaceCard(slug="model-routing-dashboard", title_ar="Model Routing Dashboard", plane="decision", status="live", backing_routes=["/api/v1/operations/command-center"], status_reason_ar="الواجهة الجديدة تعرض fabric التوزيع الحالي وأبعاد benchmark المطلوبة لتطويره."),
    ]


def _build_compliance_controls() -> List[ComplianceControl]:
    return [
        ComplianceControl(
            framework="PDPL",
            control_id="PDPL-01",
            title_ar="ربط الموافقات والبيانات الحساسة بمسارات approval-aware",
            status="live",
            evidence=["consent-aware outbound controls", "approval center", "tenant isolation"],
        ),
        ComplianceControl(
            framework="NCA ECC 2-2024",
            control_id="NCA-OPS-02",
            title_ar="ربط الإطلاقات والتكاملات والحوادث بسجل تشغيل وتتبّع",
            status="live",
            evidence=["go-live gate", "connector health", "audit logs", "domain events"],
        ),
        ComplianceControl(
            framework="NIST AI RMF / GenAI Profile",
            control_id="AI-GOV-03",
            title_ar="تصنيف الأفعال الحساسة وربطها بـ guardrails وHITL",
            status="live",
            evidence=["OpenClaw policy check", "approval classes", "sensitivity metadata"],
        ),
        ComplianceControl(
            framework="OWASP LLM Top 10",
            control_id="LLM-SEC-04",
            title_ar="حصر الأفعال الخارجية في gates قابلة للتدقيق مع trace trail",
            status="partial",
            evidence=["policy check", "audit logs", "tool verification ledger"],
        ),
    ]


def _build_gaps(surfaces: List[SurfaceCard]) -> List[GapItem]:
    gap_map = {
        "evidence-pack-viewer": ("high", "live", "اربط evidence packs بواجهة مخصصة تجمع القرار والدليل ومسار الاعتماد."),
        "partner-room": ("high", "live", "ابنِ واجهة شراكات تربط strategic-deals APIs بغرفة تنفيذية موحدة."),
        "dd-room": ("high", "live", "أضف غرفة DD تعرض streams القانونية والمالية والمنتج والأمن بسجل قابل للاستئناف."),
        "risk-board": ("medium", "live", "اجمع approval breaches وconnector failures وpolicy escalations في heatmap موحد."),
        "policy-violations-board": ("medium", "live", "اعرض violations وguardrail hits وapproval denials في لوحة واحدة."),
        "partnership-scorecards": ("medium", "live", "حوّل analytics الحالية إلى scorecards تنفيذية للشركاء والمساهمة الربحية."),
        "mna-pipeline-board": ("high", "live", "اربط acquisition deal types بواجهة board + IC pack + next action."),
        "expansion-launch-console": ("medium", "live", "أضف launch console للأسواق مع stop-loss وrollback rules."),
        "pmi-30-60-90-engine": ("medium", "live", "قدّم workstreams وowners وdependencies وsynergy tracking كسطح مستقل."),
    }
    items: List[GapItem] = []
    for surface in surfaces:
        if surface.status == "live":
            continue
        severity, target_status, next_step = gap_map.get(
            surface.slug,
            ("medium", "live", "حوّل السطح الجزئي إلى تجربة تنفيذية كاملة مرتبطة بالأحداث والاعتمادات."),
        )
        items.append(
            GapItem(
                slug=surface.slug,
                title_ar=surface.title_ar,
                severity=severity,
                status_needed=target_status,
                next_step_ar=next_step,
            )
        )
    return items


async def _tenant_strategy_metrics(db: AsyncSession, tenant_id) -> Dict[str, int]:
    deal_counts_q = await db.execute(
        select(StrategicDeal.deal_type, func.count())
        .where(StrategicDeal.tenant_id == tenant_id)
        .group_by(StrategicDeal.deal_type)
    )
    deal_counts = {row[0]: int(row[1]) for row in deal_counts_q.all()}

    deal_status_q = await db.execute(
        select(StrategicDeal.status, func.count())
        .where(StrategicDeal.tenant_id == tenant_id)
        .group_by(StrategicDeal.status)
    )
    deal_status_counts = {row[0]: int(row[1]) for row in deal_status_q.all()}

    match_status_q = await db.execute(
        select(DealMatch.status, func.count())
        .where(DealMatch.tenant_id == tenant_id)
        .group_by(DealMatch.status)
    )
    match_status_counts = {row[0]: int(row[1]) for row in match_status_q.all()}

    return {
        "partnerships": deal_counts.get(DealType.PARTNERSHIP.value, 0),
        "acquisitions": deal_counts.get(DealType.ACQUISITION.value, 0),
        "due_diligence": deal_status_counts.get(DealStatus.DUE_DILIGENCE.value, 0),
        "term_sheets": deal_status_counts.get(DealStatus.TERM_SHEET.value, 0),
        "approved_matches": match_status_counts.get(MatchStatus.APPROVED.value, 0),
        "converted_matches": match_status_counts.get(MatchStatus.CONVERTED.value, 0),
    }


def _demo_strategy_metrics() -> Dict[str, int]:
    return {
        "partnerships": 6,
        "acquisitions": 3,
        "due_diligence": 2,
        "term_sheets": 4,
        "approved_matches": 8,
        "converted_matches": 3,
    }


async def build_enterprise_command_center(
    db: AsyncSession,
    user: Optional[User],
) -> EnterpriseCommandCenterResponse:
    from app.api.v1.autonomous_foundation import build_go_live_readiness_report

    governance = _build_governance()
    surfaces = _build_surfaces()
    gaps = _build_gaps(surfaces)
    readiness = build_go_live_readiness_report()

    if user:
        demo_mode = False
        tenant_id = user.tenant_id
        tenant_id_str = str(user.tenant_id)
        connectors = await list_integration_connectors(db, tenant_id)
        pending_approvals = await count_pending_approvals(db, tenant_id)
        domain_events_24h = await count_events_since(db, tenant_id, 24)
        strategy_metrics = await _tenant_strategy_metrics(db, tenant_id)
        runs = observability_bridge.list_runs(tenant_id=tenant_id_str, limit=25)
        promoted_memories = len(memory_bridge.list_items(tenant_id=tenant_id_str, promoted_only=True, limit=500))
        media_drafts = len(media_bridge.list_drafts(tenant_id=tenant_id_str, limit=500))
    else:
        demo_mode = True
        connectors = _demo_connectors()
        pending_approvals = 3
        domain_events_24h = 18
        strategy_metrics = _demo_strategy_metrics()
        runs = [
            {"run_id": "run_sales_01", "task_type": "prospecting_flow", "status": "completed", "approval_required": False},
            {"run_id": "run_term_02", "task_type": "term_sheet_gate", "status": "awaiting_approval", "approval_required": True},
            {"run_id": "run_mna_03", "task_type": "dd_stream_sync", "status": "completed", "approval_required": False},
        ]
        promoted_memories = 11
        media_drafts = 2

    healthy_connectors = sum(1 for connector in connectors if connector.get("status") == "ok")
    overall_status = _summarize_overall_status(readiness["readiness_percent"], gaps)
    traceability_status = "مفعّل" if domain_events_24h > 0 or runs else "جزئي"
    policy_posture = "approval-aware" if pending_approvals >= 0 else "basic"

    metrics = [
        CommandCenterMetric(key="readiness", label_ar="جاهزية الإطلاق", value=readiness["readiness_percent"], unit="%", status="success" if readiness["launch_allowed"] else "warning"),
        CommandCenterMetric(key="approvals", label_ar="موافقات حرجة معلّقة", value=pending_approvals, status="warning" if pending_approvals else "success"),
        CommandCenterMetric(key="connectors", label_ar="موصلات سليمة", value=healthy_connectors, unit=f"/{len(connectors)}", status="success" if healthy_connectors == len(connectors) else "warning"),
        CommandCenterMetric(key="events", label_ar="أحداث قابلة للتتبع / 24 ساعة", value=domain_events_24h, status="info"),
        CommandCenterMetric(key="partnerships", label_ar="صفقات شراكات", value=strategy_metrics["partnerships"], status="info"),
        CommandCenterMetric(key="acquisitions", label_ar="مسارات M&A", value=strategy_metrics["acquisitions"], status="info"),
    ]

    planes = [
        CommandCenterPlane(
            key="decision",
            title_ar="Decision Plane",
            status="live",
            description_ar="طبقة القرار التنفيذي: metrics + routing + policy-aware recommendations بدل chat transcript خام.",
            backbone=["executive ROI", "predictive endpoints", "model routing fabric", "structured command center payload"],
            live_signals=["actual vs forecast", "revenue funnel", "model routing dashboard"],
            control_focus=["decision context", "evidence-backed summaries", "board-facing visibility"],
        ),
        CommandCenterPlane(
            key="execution",
            title_ar="Execution Plane",
            status="partial",
            description_ar="طبقة التنفيذ الطويل: OpenClaw flows حية الآن، مع هدف واضح لتحويل الالتزامات الثقيلة إلى runtime durable كامل.",
            backbone=["OpenClaw gateway", "prospecting durable flow", "approval queue", "strategic deals pipelines"],
            live_signals=["pending approvals", "recent runs", "term sheet + due diligence states"],
            control_focus=["resumable workflows", "handoffs", "approval checkpoints"],
        ),
        CommandCenterPlane(
            key="trust",
            title_ar="Trust Plane",
            status="live",
            description_ar="طبقة الحوكمة: approvals + reversibility + sensitivity + audit + policy checks.",
            backbone=["approval center", "OpenClaw policy check", "audit logs", "tool verification ledger"],
            live_signals=["approval SLA", "policy-aware gates", "Saudi compliance matrix"],
            control_focus=["HITL", "sensitive actions", "traceable approvals"],
        ),
        CommandCenterPlane(
            key="data",
            title_ar="Data Plane",
            status="live",
            description_ar="طبقة البيانات والتكاملات: موصلات، أحداث نطاق، واسترجاع تشغيلي قريب من القرار.",
            backbone=["integration connectors", "domain events", "memory bridge", "document-aware flows"],
            live_signals=["connector health", "event counts", "promoted memories"],
            control_focus=["connector governance", "audit mapping", "event observability"],
        ),
        CommandCenterPlane(
            key="operating",
            title_ar="Operating Plane",
            status="live",
            description_ar="طبقة التسليم والتشغيل: readiness gate، إطلاقات محكومة، وسردية تشغيلية جاهزة للمؤسسة.",
            backbone=["go-live gate", "launch readiness report", "canary posture", "environment-aware checks"],
            live_signals=["readiness percent", "blocked reasons", "release gate dashboard"],
            control_focus=["release protection", "provenance readiness", "environment discipline"],
        ),
    ]

    operating_systems = [
        OperatingSystemCard(
            key="sales_revenue_os",
            title_ar="Sales & Revenue OS",
            status="live",
            automation_summary_ar="الالتقاط والإثراء والتقييم والمتابعة والتذكير وبناء المقترح مؤتمتة؛ التزامات الخصم والتوقيع تمر عبر بوابات اعتماد.",
            auto_scope=["capture", "enrichment", "scoring", "routing", "follow-ups", "meeting reminders", "memo drafting"],
            approval_scope=["discount exception", "signature trigger", "non-standard terms"],
            coverage_metrics={"pending_approvals": pending_approvals, "openclaw_runs": len(runs), "healthy_connectors": healthy_connectors},
        ),
        OperatingSystemCard(
            key="partnership_os",
            title_ar="Partnership OS",
            status="partial",
            automation_summary_ar="الاكتشاف والتحليل والمطابقة والتفاوض والتحضير موجودة؛ الغرفة التنفيذية للشركاء والـ scorecards ما زالت جزئية.",
            auto_scope=["partner scouting", "fit scoring", "channel economics", "proposal drafting"],
            approval_scope=["term sheet send", "rev-share change", "exclusivity", "data sharing"],
            coverage_metrics={"partnerships": strategy_metrics["partnerships"], "approved_matches": strategy_metrics["approved_matches"], "converted_matches": strategy_metrics["converted_matches"]},
        ),
        OperatingSystemCard(
            key="mna_os",
            title_ar="M&A / Corp Dev OS",
            status="partial",
            automation_summary_ar="مسارات الاكتشاف والتحليل والتفاوض والـ due diligence ممثلة في backend؛ الـ board surface المخصص ما زال يحتاج واجهة كاملة.",
            auto_scope=["target sourcing", "fit screening", "management mapping", "DD orchestration"],
            approval_scope=["offer strategy", "offer send", "signing", "close approvals"],
            coverage_metrics={"acquisitions": strategy_metrics["acquisitions"], "due_diligence": strategy_metrics["due_diligence"], "term_sheets": strategy_metrics["term_sheets"]},
        ),
        OperatingSystemCard(
            key="expansion_os",
            title_ar="Expansion OS",
            status="partial",
            automation_summary_ar="Readiness gates والتكاملات الحية موجودة، لكن launch console السوقي وstop-loss workflow يحتاجان واجهة مخصصة.",
            auto_scope=["market scan framing", "readiness checks", "connector syncs", "launch diagnostics"],
            approval_scope=["market launch", "partner-assisted entry", "capital commitments"],
            coverage_metrics={"launch_readiness": int(readiness["readiness_percent"]), "blocked_items": readiness["missing_count"], "healthy_connectors": healthy_connectors},
        ),
        OperatingSystemCard(
            key="pmi_pmo_os",
            title_ar="PMI / Strategic PMO OS",
            status="partial",
            automation_summary_ar="الاستئناف والتذكير والتصعيد موجودة جزئياً عبر flows وSLA، لكن 30/60/90 engine مستقل لم يكتمل بعد.",
            auto_scope=["task reminders", "escalation signals", "owner tracking", "telemetry updates"],
            approval_scope=["integration sign-off", "synergy realization acceptance"],
            coverage_metrics={"media_drafts": media_drafts, "promoted_memories": promoted_memories, "tracked_events": domain_events_24h},
        ),
        OperatingSystemCard(
            key="executive_board_os",
            title_ar="Executive / Board OS",
            status="live",
            automation_summary_ar="السطح التنفيذي حاضر الآن عبر command center الجديد مع مؤشرات القرار والاعتماد والجاهزية والفجوات.",
            auto_scope=["executive snapshot", "actual vs forecast", "approval load", "policy posture"],
            approval_scope=["board pack approval", "external commitments", "production release"],
            coverage_metrics={"live_surfaces": sum(1 for s in surfaces if s.status == "live"), "partial_surfaces": sum(1 for s in surfaces if s.status == "partial"), "readiness": int(readiness["readiness_percent"])},
        ),
    ]

    note = (
        "هذا السطح يجعل دستور Dealix حيًا داخل المنتج: typed + observable + approval-aware + executive-facing."
        if not demo_mode
        else "وضع توضيحي: السطح التنفيذي يعمل بدون جلسة أيضاً ليعرض حالة الجاهزية والحوكمة والفجوات الحالية."
    )

    return EnterpriseCommandCenterResponse(
        demo_mode=demo_mode,
        headline=CommandCenterHeadline(
            system_name_ar="Dealix Sovereign Growth, Execution & Governance OS",
            subtitle_ar="قرار منظّم + تنفيذ قابل للاستئناف + حوكمة قابلة للتدقيق + أسطح تنفيذية عربية.",
            operating_mode="executive_command_center",
            status=overall_status,
            readiness_percent=round(float(readiness["readiness_percent"]), 1),
            traceability_status=traceability_status,
            policy_posture=policy_posture,
        ),
        metrics=metrics,
        planes=planes,
        operating_systems=operating_systems,
        approval_classes=governance["approval_classes"],
        reversibility_classes=governance["reversibility_classes"],
        sensitivity_classes=governance["sensitivity_classes"],
        commitment_gates=governance["commitment_gates"],
        surfaces=sorted(surfaces, key=lambda item: (_status_rank(item.status) * -1, item.title_ar)),
        model_routing=_build_model_routing_summary(),
        saudi_compliance=_build_compliance_controls(),
        gaps=gaps,
        note_ar=note,
    )

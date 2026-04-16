from __future__ import annotations

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_optional_user
from app.api.v1.autonomous_foundation import live_readiness_report
from app.api.v1.operations import operations_snapshot
from app.database import get_db
from app.models.user import User

StatusKind = Literal["live", "foundation", "gap"]

router = APIRouter(prefix="/operating-system", tags=["Operating System"])


class StatusCounts(BaseModel):
    live: int = 0
    foundation: int = 0
    gap: int = 0


class PlaneMetric(BaseModel):
    label_ar: str
    value: str
    hint_ar: Optional[str] = None


class PlaneCard(BaseModel):
    id: str
    title_ar: str
    status: StatusKind
    current_state_ar: str
    target_state_ar: str
    summary_ar: str
    evidence_sources: List[str] = Field(default_factory=list)
    metrics: List[PlaneMetric] = Field(default_factory=list)


class BusinessSystemCard(BaseModel):
    id: str
    title_ar: str
    status: StatusKind
    summary_ar: str
    stages: List[str] = Field(default_factory=list)
    automation_now: List[str] = Field(default_factory=list)
    approval_gates: List[str] = Field(default_factory=list)


class LiveSurfaceCard(BaseModel):
    id: str
    title_ar: str
    status: StatusKind
    plane_owner_ar: str
    route_hint: Optional[str] = None
    api_hint: Optional[str] = None
    note_ar: str


class MetadataClassCard(BaseModel):
    family: Literal["approval", "reversibility", "sensitivity"]
    code: str
    label_ar: str
    mode_ar: str
    examples: List[str] = Field(default_factory=list)


class AutomationBucket(BaseModel):
    id: str
    label_ar: str
    mode: Literal["auto", "approval"]
    items: List[str] = Field(default_factory=list)


class ComplianceControlCard(BaseModel):
    id: str
    title_ar: str
    status: StatusKind
    control_ar: str
    note_ar: str


class BenchmarkHarness(BaseModel):
    status: StatusKind
    title_ar: str
    note_ar: str
    metrics: List[str] = Field(default_factory=list)


class LaunchGateSummary(BaseModel):
    overall: str
    readiness_percent: float
    missing_count: int
    summary_ar: str
    blocked_reasons: List[str] = Field(default_factory=list)


class OperationalPulse(BaseModel):
    demo_mode: bool
    pending_approvals: int
    domain_events_24h: int
    audit_events_24h: int
    connectors_total: int
    openclaw_runs: int
    approval_health: str
    note_ar: Optional[str] = None


class ExecutiveRoomResponse(BaseModel):
    title_ar: str
    title_en: str
    summary_ar: str
    north_star_ar: str
    mode: Literal["demo", "tenant"]
    surface_coverage: StatusCounts
    system_coverage: StatusCounts
    operational_pulse: OperationalPulse
    launch_gate: LaunchGateSummary
    planes: List[PlaneCard] = Field(default_factory=list)
    business_systems: List[BusinessSystemCard] = Field(default_factory=list)
    live_surfaces: List[LiveSurfaceCard] = Field(default_factory=list)
    decision_metadata_classes: List[MetadataClassCard] = Field(default_factory=list)
    automation_policy: List[AutomationBucket] = Field(default_factory=list)
    compliance_matrix: List[ComplianceControlCard] = Field(default_factory=list)
    benchmark_harness: BenchmarkHarness
    next_moves: List[str] = Field(default_factory=list)


def _status_counts(items: list[PlaneCard] | list[BusinessSystemCard] | list[LiveSurfaceCard]) -> StatusCounts:
    counts = {"live": 0, "foundation": 0, "gap": 0}
    for item in items:
        counts[item.status] += 1
    return StatusCounts(**counts)


def _build_planes(ops: dict, launch: dict) -> list[PlaneCard]:
    openclaw = ops.get("openclaw") or {}
    approval_sla = openclaw.get("approval_sla") or {}
    recent_runs = len(openclaw.get("recent_runs") or [])
    connectors_total = len(ops.get("connectors") or [])
    readiness_percent = float(launch.get("readiness_percent") or 0)
    missing_count = len(launch.get("missing") or [])

    return [
        PlaneCard(
            id="decision",
            title_ar="Decision Plane",
            status="foundation",
            current_state_ar=(
                "يوجد تنسيق agentic وسياسات واعتماد وتشغيلات مرصودة، لكن طبقة Responses API + Structured Outputs + MCP "
                "لم تصبح بعد المعيار الموحد لكل القرار."
            ),
            target_state_ar="كل قرار business-critical يخرج typed + evidence-backed + approval-aware.",
            summary_ar="طبقة القرار موجودة كأساس حي، وتحتاج توحيدًا نهائيًا على عقود قرار structured قابلة للتتبع.",
            evidence_sources=[
                "/api/v1/autonomous-foundation/openclaw/policy/check",
                "/api/v1/autonomous-foundation/openclaw/runs",
                "/api/v1/operations/snapshot",
            ],
            metrics=[
                PlaneMetric(label_ar="موافقات معلقة", value=str(ops.get("pending_approvals") or 0), hint_ar="إشارة مباشرة للحِمل البشري على القرارات الحساسة."),
                PlaneMetric(label_ar="تشغيلات مرصودة", value=str(recent_runs), hint_ar="Runs قابلة للمراقبة في OpenClaw."),
            ],
        ),
        PlaneCard(
            id="execution",
            title_ar="Execution Plane",
            status="foundation",
            current_state_ar=(
                "هناك flows وOpenClaw وعمليات قابلة للاستئناف جزئيًا، لكن الالتزامات الطويلة العابرة للأنظمة لم تُرحَّل بعد إلى runtime durable موحّد."
            ),
            target_state_ar="كل workflow طويل العمر أو حساس يصبح durable/resumable مع gates واضحة.",
            summary_ar="الأساس التنفيذي حي، لكنه ليس بعد Runtime مؤسسي موحد لكل approvals والتزامات الشراكات والتوسع وPMI.",
            evidence_sources=[
                "/api/v1/autonomous-foundation/flows/prospecting",
                "/api/v1/autonomous-foundation/flows/self-improvement",
                "/api/v1/operations/snapshot",
            ],
            metrics=[
                PlaneMetric(label_ar="تشغيلات OpenClaw", value=str(recent_runs), hint_ar="مؤشر on-platform execution الحالي."),
                PlaneMetric(label_ar="إطلاقات محجوبة", value=str(missing_count), hint_ar="فجوات تشغيلية تمنع الإطلاق الكامل."),
            ],
        ),
        PlaneCard(
            id="trust",
            title_ar="Trust Plane",
            status="foundation",
            current_state_ar=(
                "الموافقات والسياسات وPDPL والتدقيق موجودة، لكن OPA/OpenFGA/Vault/Keycloak لم تُجمّع بعد ضمن طبقة trust موحدة."
            ),
            target_state_ar="Approval / Reversibility / Sensitivity metadata على كل فعل حساس مع فصل policy وauthorization عن الكود.",
            summary_ar="الحوكمة حية داخل المنتج، لكنها ما زالت موزعة بين جسور وسياسات وخدمات وتحتاج طبقة trust سيادية موحدة.",
            evidence_sources=[
                "/api/v1/operations/approvals",
                "/api/v1/operations/approvals/sla",
                "backend/app/services/pdpl/consent_manager.py",
            ],
            metrics=[
                PlaneMetric(label_ar="صحة SLA", value=str(approval_sla.get("health") or "ok"), hint_ar="الصحة الحالية لسير الموافقات."),
                PlaneMetric(label_ar="موافقات معلقة", value=str(ops.get("pending_approvals") or 0), hint_ar="كلما ارتفعت، ارتفع احتكاك القرارات الحرجة."),
            ],
        ),
        PlaneCard(
            id="data",
            title_ar="Data Plane",
            status="foundation",
            current_state_ar=(
                "البيانات التشغيلية والأحداث والموصلات موجودة، لكن عقود CloudEvents/AsyncAPI والقياس الدلالي والـ OTel لم تُوَحَّد بعد."
            ),
            target_state_ar="Operational truth + event contracts + memory + telemetry بعقود machine-readable موحدة.",
            summary_ar="طبقة البيانات موجودة كأساس تشغيلي، وتحتاج ترقية من بيانات حيّة إلى بيانات متعاقد عليها وقابلة للحوكمة عبر السطوح كلها.",
            evidence_sources=[
                "/api/v1/operations/domain-events",
                "/api/v1/operations/integration-connectors",
                "/api/v1/operations/snapshot",
            ],
            metrics=[
                PlaneMetric(label_ar="أحداث 24 ساعة", value=str(ops.get("domain_events_24h") or 0), hint_ar="نشاط event backbone الحالي."),
                PlaneMetric(label_ar="موصلات ظاهرة", value=str(connectors_total), hint_ar="جزء من data plane الحي الآن."),
            ],
        ),
        PlaneCard(
            id="operating",
            title_ar="Operating Plane",
            status="foundation",
            current_state_ar=(
                "بوابة الجاهزية والإطلاق الحي موجودة، لكن rulesets/provenance/OIDC/attestations لم تظهر بعد كسطح تشغيلي موحّد داخل المنتج."
            ),
            target_state_ar="كل release يمر عبر gates محمية، provenance، environments، وأدلة merge/deploy واضحة.",
            summary_ar="التشغيل المؤسسي بدأ حيًا عبر launch gate، ويحتاج إكمال سلسلة السيادة من repo إلى release.",
            evidence_sources=[
                "/api/v1/autonomous-foundation/integrations/live-readiness",
                "/api/v1/autonomous-foundation/integrations/go-live-gate",
            ],
            metrics=[
                PlaneMetric(label_ar="جاهزية الإطلاق", value=f"{readiness_percent:.1f}%", hint_ar="النسبة الحالية لفحوص الإطلاق التجاري."),
                PlaneMetric(label_ar="عناصر ناقصة", value=str(missing_count), hint_ar="بنود تمنع الإطلاق الكامل."),
            ],
        ),
    ]


def _build_business_systems() -> list[BusinessSystemCard]:
    return [
        BusinessSystemCard(
            id="sales_revenue_os",
            title_ar="Sales & Revenue OS",
            status="live",
            summary_ar="الأقرب للاكتمال اليوم: capture → scoring → routing → pipeline → proposals → onboarding → revenue ops.",
            stages=[
                "capture",
                "enrichment",
                "scoring",
                "routing",
                "outreach",
                "proposal/CPQ",
                "approval",
                "signature",
                "handoff",
                "renewal/expansion",
            ],
            automation_now=[
                "lead capture",
                "enrichment",
                "scoring",
                "follow-ups",
                "meeting reminders",
                "memo drafting",
            ],
            approval_gates=[
                "discount خارج السياسة",
                "non-standard terms",
                "signature trigger النهائي",
            ],
        ),
        BusinessSystemCard(
            id="partnership_os",
            title_ar="Partnership OS",
            status="foundation",
            summary_ar="التحليل والحوكمة قابلان للبناء فوق الأساس الحالي، لكن partner room والاقتصاديات والscorecards ليست أسطحًا حية كاملة بعد.",
            stages=[
                "scouting",
                "fit scoring",
                "channel economics",
                "term sheet",
                "approval routing",
                "activation",
                "scorecards",
            ],
            automation_now=[
                "research and drafting",
                "fit analysis",
                "activation checklists",
            ],
            approval_gates=[
                "term sheet",
                "rev-share changes",
                "exclusivity",
                "data sharing",
            ],
        ),
        BusinessSystemCard(
            id="ma_os",
            title_ar="M&A / Corporate Development OS",
            status="foundation",
            summary_ar="هناك بذور strategic deals وdeal room logic، لكن DD room والcommittee packs ومسار offer/close لم تصبح workflow حيًا متكاملاً بعد.",
            stages=[
                "target sourcing",
                "screening",
                "management mapping",
                "DD orchestration",
                "valuation",
                "committee pack",
                "offer strategy",
                "signing/close",
            ],
            automation_now=[
                "screening",
                "document assembly",
                "DD reminders",
                "evidence collection",
            ],
            approval_gates=[
                "send offer",
                "signing documents",
                "close approvals",
            ],
        ),
        BusinessSystemCard(
            id="expansion_os",
            title_ar="Expansion OS",
            status="foundation",
            summary_ar="بوابات الجاهزية والإطلاق موجودة، لكن market scanning وstop-loss وpartner-assisted entry ما زالت تحتاج surface تشغيلي موحّد.",
            stages=[
                "market scanning",
                "segment prioritization",
                "regulatory readiness",
                "localized GTM",
                "launch readiness",
                "canary launch",
                "stop-loss",
            ],
            automation_now=[
                "launch readiness checks",
                "connector health",
                "release gating",
            ],
            approval_gates=[
                "market launch",
                "strategic partner entry",
                "stop-loss override",
            ],
        ),
        BusinessSystemCard(
            id="pmi_pmo_os",
            title_ar="PMI / Strategic PMO OS",
            status="gap",
            summary_ar="هذا المسار ما زال أوضح فجوة تشغيلية: لا يوجد بعد engine حي لإدارة Day-1 و30/60/90 والتبعيات والتصعيد التنفيذي.",
            stages=[
                "day-1 readiness",
                "30/60/90",
                "workstreams",
                "dependencies",
                "escalations",
                "synergy tracking",
                "exec reporting",
            ],
            automation_now=[],
            approval_gates=[
                "executive escalation",
                "integration risk acceptance",
            ],
        ),
        BusinessSystemCard(
            id="executive_board_os",
            title_ar="Executive / Board OS",
            status="live",
            summary_ar="هذا السطح أصبح حيًا الآن كغرفة تنفيذية موحّدة تعرض القرار، الجاهزية، الفجوات، والحوكمة بدل chat transcript.",
            stages=[
                "executive room",
                "approval center",
                "risk board",
                "actual vs forecast",
                "next best action",
            ],
            automation_now=[
                "board-style summaries",
                "evidence-backed status",
                "launch/readiness visibility",
            ],
            approval_gates=[
                "board-level commitments",
                "capital commitments",
                "policy exception approval",
            ],
        ),
    ]


def _build_live_surfaces() -> list[LiveSurfaceCard]:
    return [
        LiveSurfaceCard(
            id="executive_room",
            title_ar="Executive Room",
            status="live",
            plane_owner_ar="Decision + Operating",
            route_hint="/dashboard → الغرفة التنفيذية والسيادية",
            api_hint="/api/v1/operating-system/executive-room",
            note_ar="واجهة تنفيذية موحدة تعرض الطبقات، الجاهزية، الفجوات، والسياسات.",
        ),
        LiveSurfaceCard(
            id="approval_center",
            title_ar="Approval Center",
            status="foundation",
            plane_owner_ar="Trust",
            route_hint="/dashboard → التشغيل الشامل",
            api_hint="/api/v1/operations/approvals",
            note_ar="الـ API حي، لكن ما يزال ينقصه مركز اعتماد مخصص كواجهة مستقلة.",
        ),
        LiveSurfaceCard(
            id="evidence_pack_viewer",
            title_ar="Evidence Pack Viewer",
            status="foundation",
            plane_owner_ar="Trust + Data",
            api_hint="/api/v1/strategy/summary",
            note_ar="الأدلة والوثائق موجودة عبر APIs وملفات استراتيجية، لكن viewer موحّد لم يكتمل بعد.",
        ),
        LiveSurfaceCard(
            id="partner_room",
            title_ar="Partner Room",
            status="gap",
            plane_owner_ar="Execution",
            note_ar="سطح شراكات تشغيلي متكامل غير موجود بعد.",
        ),
        LiveSurfaceCard(
            id="dd_room",
            title_ar="DD Room",
            status="foundation",
            plane_owner_ar="Execution + Data",
            api_hint="backend/app/services/strategic_deals/deal_room.py",
            note_ar="منطق deal room موجود كأساس، لكن DD room التنفيذي لم يصبح UI حيًا بعد.",
        ),
        LiveSurfaceCard(
            id="risk_board",
            title_ar="Risk Board",
            status="foundation",
            plane_owner_ar="Trust",
            route_hint="/dashboard → التشغيل الشامل",
            api_hint="/api/v1/operations/approvals/sla",
            note_ar="إشارات الخطر وSLA موجودة، لكن لوحة مخاطر تنفيذية مخصصة لا تزال ناقصة.",
        ),
        LiveSurfaceCard(
            id="policy_violations_board",
            title_ar="Policy Violations Board",
            status="foundation",
            plane_owner_ar="Trust",
            api_hint="/api/v1/autonomous-foundation/openclaw/policy/check",
            note_ar="فحص السياسة موجود، لكن board حي لانتهاكات السياسة لم يكتمل.",
        ),
        LiveSurfaceCard(
            id="actual_vs_forecast_dashboard",
            title_ar="Actual vs Forecast Dashboard",
            status="live",
            plane_owner_ar="Decision + Data",
            route_hint="/dashboard → التحليلات ونبض السوق",
            api_hint="/api/v1/autonomous-foundation/dashboard/executive-roi",
            note_ar="يوجد سطح تحليلي/تنفيذي حي يمكن البناء عليه مباشرة.",
        ),
        LiveSurfaceCard(
            id="revenue_funnel_control_center",
            title_ar="Revenue Funnel Control Center",
            status="live",
            plane_owner_ar="Execution",
            route_hint="/dashboard → مسار الصفقات / Sales OS",
            api_hint="/api/v1/sales-os/overview",
            note_ar="القمع البيعي وسير الصفقات ظاهر الآن داخل المنتج.",
        ),
        LiveSurfaceCard(
            id="partnership_scorecards",
            title_ar="Partnership Scorecards",
            status="gap",
            plane_owner_ar="Decision + Data",
            note_ar="نقطة نقص مباشرة في النسخة المؤسسية الحالية.",
        ),
        LiveSurfaceCard(
            id="ma_pipeline_board",
            title_ar="M&A Pipeline Board",
            status="foundation",
            plane_owner_ar="Execution",
            api_hint="/api/v1/strategic-deals/*",
            note_ar="توجد طبقة strategic deals، لكن board مؤسسي كامل لـ M&A لم يكتمل بعد.",
        ),
        LiveSurfaceCard(
            id="expansion_launch_console",
            title_ar="Expansion Launch Console",
            status="foundation",
            plane_owner_ar="Operating",
            route_hint="/dashboard → التشغيل الشامل",
            api_hint="/api/v1/autonomous-foundation/integrations/go-live-gate",
            note_ar="بوابة الإطلاق حيّة، وتحتاج console أوسع لسيناريوهات التوسع.",
        ),
        LiveSurfaceCard(
            id="pmi_engine",
            title_ar="PMI 30/60/90 Engine",
            status="gap",
            plane_owner_ar="Execution",
            note_ar="غير موجود بعد كسطح durable حي.",
        ),
        LiveSurfaceCard(
            id="tool_verification_ledger",
            title_ar="Tool Verification Ledger",
            status="foundation",
            plane_owner_ar="Trust",
            api_hint="backend/app/services/tool_receipts.py",
            note_ar="الأساس البرمجي موجود، لكن viewer تنفيذي مباشر لا يزال مفقودًا.",
        ),
        LiveSurfaceCard(
            id="connector_health_board",
            title_ar="Connector Health Board",
            status="live",
            plane_owner_ar="Data + Operating",
            route_hint="/dashboard → التشغيل الشامل",
            api_hint="/api/v1/operations/snapshot",
            note_ar="صحة الموصلات تُعرض اليوم حيًا داخل Full Ops.",
        ),
        LiveSurfaceCard(
            id="release_gate_dashboard",
            title_ar="Release Gate Dashboard",
            status="live",
            plane_owner_ar="Operating",
            api_hint="/api/v1/autonomous-foundation/integrations/live-readiness",
            note_ar="بوابة جاهزية الإطلاق موجودة بالفعل ويمكن البناء عليها كلوحة release مؤسسية.",
        ),
        LiveSurfaceCard(
            id="saudi_compliance_matrix",
            title_ar="Saudi Compliance Matrix",
            status="foundation",
            plane_owner_ar="Trust",
            api_hint="backend/app/services/pdpl/consent_manager.py",
            note_ar="ضوابط PDPL حية، لكن matrix تنفيذية سعودية موحدة غير ظاهرة بعد داخل المنتج.",
        ),
        LiveSurfaceCard(
            id="model_routing_dashboard",
            title_ar="Model Routing Dashboard",
            status="gap",
            plane_owner_ar="Decision",
            note_ar="ما زال benchmark harness والرصد المقارن للموديلات فجوة واضحة.",
        ),
    ]


def _build_metadata_classes() -> list[MetadataClassCard]:
    return [
        MetadataClassCard(
            family="approval",
            code="A0",
            label_ar="تلقائي وآمن",
            mode_ar="ينفذ دون اعتماد",
            examples=["lead capture", "enrichment", "scoring", "dashboard updates"],
        ),
        MetadataClassCard(
            family="approval",
            code="A1",
            label_ar="اعتماد إداري",
            mode_ar="مدير / مالك الخدمة",
            examples=["discount خارج السياسة", "partner activation", "market launch"],
        ),
        MetadataClassCard(
            family="approval",
            code="A2",
            label_ar="اعتماد تنفيذي / مجلس",
            mode_ar="قرار غير قابل للعكس أو عالي الأثر",
            examples=["M&A offer", "capital commitments", "board-level exceptions"],
        ),
        MetadataClassCard(
            family="reversibility",
            code="R1",
            label_ar="قابل للعكس",
            mode_ar="يمكن التنفيذ تلقائيًا إذا كان منخفض المخاطر",
            examples=["draft memo", "meeting reminder", "task assignment"],
        ),
        MetadataClassCard(
            family="reversibility",
            code="R2",
            label_ar="التزام خارجي",
            mode_ar="يتطلب اعتمادًا قبل الإرسال",
            examples=["term sheet", "e-sign request", "partner commitment"],
        ),
        MetadataClassCard(
            family="reversibility",
            code="R3",
            label_ar="غير قابل للعكس / قانوني",
            mode_ar="بوابة تنفيذية إلزامية",
            examples=["final signature", "close approval", "external capital commitment"],
        ),
        MetadataClassCard(
            family="sensitivity",
            code="S1",
            label_ar="تشغيلي",
            mode_ar="حساسية منخفضة",
            examples=["internal tasks", "pipeline reminders"],
        ),
        MetadataClassCard(
            family="sensitivity",
            code="S2",
            label_ar="تجاري سري",
            mode_ar="قيود وصول وسياسة",
            examples=["pricing", "partner economics", "board memo"],
        ),
        MetadataClassCard(
            family="sensitivity",
            code="S3",
            label_ar="PDPL / بيانات عالية الحساسية",
            mode_ar="موافقة + تدقيق + تتبع",
            examples=["customer PII", "data sharing", "sensitive DD material"],
        ),
    ]


def _build_automation_policy() -> list[AutomationBucket]:
    return [
        AutomationBucket(
            id="fully_automated",
            label_ar="مؤتمت بالكامل بلا اعتماد",
            mode="auto",
            items=[
                "lead capture",
                "enrichment",
                "scoring",
                "routing",
                "follow-ups",
                "meeting reminders",
                "memo drafting",
                "evidence pack assembly",
                "DD checklist orchestration",
                "task assignment",
                "SLA reminders",
                "dashboard updates",
                "telemetry",
                "quality checks",
                "document extraction",
                "connector syncs",
                "variance detection",
                "anomaly alerts",
            ],
        ),
        AutomationBucket(
            id="approval_gated",
            label_ar="مؤتمت مع اعتماد قبل الالتزام",
            mode="approval",
            items=[
                "إرسال term sheet",
                "طلب توقيع",
                "تفعيل شراكة استراتيجية",
                "إطلاق دخول سوق جديد",
                "اعتماد discount خارج السياسة",
                "إرسال offer في M&A",
                "closing approvals",
                "data sharing عالي الحساسية",
                "rollout إلى prod",
                "external capital commitments",
            ],
        ),
    ]


def _build_compliance_matrix() -> list[ComplianceControlCard]:
    return [
        ComplianceControlCard(
            id="pdpl_outbound",
            title_ar="PDPL Outbound Control",
            status="live",
            control_ar="التحقق من الموافقة قبل أي تواصل outbound + trail للتغييرات.",
            note_ar="يوجد محرك موافقة/امتثال فعلي داخل المنتج ويمكن البناء عليه مباشرة.",
        ),
        ComplianceControlCard(
            id="approval_governance",
            title_ar="Approval-aware Actions",
            status="live",
            control_ar="إيقاف الأفعال الحساسة وغير القابلة للعكس عند policy gate.",
            note_ar="الموافقات وpolicy checks حية، لكنها تحتاج تصنيفًا أوسع عبر كل workflows.",
        ),
        ComplianceControlCard(
            id="saudi_control_mapping",
            title_ar="Saudi Control Mapping",
            status="foundation",
            control_ar="ربط workflows الحساسة بمتطلبات PDPL / NCA / ECC.",
            note_ar="مطلوب matrix حي داخل المنتج بدل الاكتفاء بالمعرفة المرجعية.",
        ),
        ComplianceControlCard(
            id="nist_ai_rmf",
            title_ar="NIST AI RMF / GenAI Profile",
            status="foundation",
            control_ar="ربط المخاطر والضوابط والاختبارات بمسارات AI التشغيلية.",
            note_ar="يحتاج لوحات تقييم ومتابعة risk treatment واضحة.",
        ),
        ComplianceControlCard(
            id="owasp_llm",
            title_ar="OWASP LLM Controls",
            status="foundation",
            control_ar="ضوابط prompt/tool/output ومراجعة المخاطر agentic.",
            note_ar="الأساس موجود في guardrails والسياسات، لكن البرنامج الأمني ما زال يحتاج surface حي.",
        ),
        ComplianceControlCard(
            id="traceability",
            title_ar="Traceability / OTel",
            status="foundation",
            control_ar="trace_id / correlation_id وقياس موحّد عبر السطوح الحساسة.",
            note_ar="الأحداث موجودة، لكن توحيد observability المؤسسي لم يكتمل بعد.",
        ),
    ]


def _benchmark_harness() -> BenchmarkHarness:
    return BenchmarkHarness(
        status="gap",
        title_ar="Model Routing Benchmark Harness",
        note_ar="المطلوب الآن هو routing intelligence مبني على benchmark pool داخلي لا على الانطباع.",
        metrics=[
            "latency",
            "success rate",
            "schema adherence",
            "tool-call reliability",
            "contradiction rate",
            "Arabic memo quality",
            "cost per successful task",
        ],
    )


@router.get("/executive-room", response_model=ExecutiveRoomResponse)
async def executive_room(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
) -> ExecutiveRoomResponse:
    ops = await operations_snapshot(db=db, user=user)
    launch = await live_readiness_report()
    live_surfaces = _build_live_surfaces()
    business_systems = _build_business_systems()
    planes = _build_planes(ops=ops, launch=launch)

    return ExecutiveRoomResponse(
        title_ar="الغرفة التنفيذية والسيادية",
        title_en="Dealix Sovereign Growth, Execution & Governance OS",
        summary_ar=(
            "سطح تنفيذي حي يجمع القرار والتنفيذ والثقة والبيانات والإطلاق في مشهد واحد: ما هو live الآن، ما هو foundation، وما الذي ما يزال gap."
        ),
        north_star_ar=(
            "Dealix كنسيج قرار + تنفيذ + ثقة + تسليم مؤسسي: typed، enforced، observable، approvable، durable، bilingual، compliance-aware."
        ),
        mode="demo" if ops.get("demo_mode") else "tenant",
        surface_coverage=_status_counts(live_surfaces),
        system_coverage=_status_counts(business_systems),
        operational_pulse=OperationalPulse(
            demo_mode=bool(ops.get("demo_mode")),
            pending_approvals=int(ops.get("pending_approvals") or 0),
            domain_events_24h=int(ops.get("domain_events_24h") or 0),
            audit_events_24h=int(ops.get("audit_events_24h") or 0),
            connectors_total=len(ops.get("connectors") or []),
            openclaw_runs=len(((ops.get("openclaw") or {}).get("recent_runs") or [])),
            approval_health=str((((ops.get("openclaw") or {}).get("approval_sla") or {}).get("health") or "ok")),
            note_ar=ops.get("note_ar"),
        ),
        launch_gate=LaunchGateSummary(
            overall=str(launch.get("overall") or "FAIL"),
            readiness_percent=float(launch.get("readiness_percent") or 0),
            missing_count=len(launch.get("missing") or []),
            summary_ar=str(launch.get("summary") or ""),
            blocked_reasons=list(launch.get("blocked_reasons") or []),
        ),
        planes=planes,
        business_systems=business_systems,
        live_surfaces=live_surfaces,
        decision_metadata_classes=_build_metadata_classes(),
        automation_policy=_build_automation_policy(),
        compliance_matrix=_build_compliance_matrix(),
        benchmark_harness=_benchmark_harness(),
        next_moves=[
            "حوّل Approval Center وRisk Board إلى surfaces مستقلة بدل الاكتفاء بالإشارات داخل Full Ops.",
            "اربط كل workflow حساس بتصنيف Approval / Reversibility / Sensitivity على مستوى العقد والحدث.",
            "أنشئ Saudi Compliance Matrix حي يربط PDPL/NCA controls بالأسطح والـ workflows.",
            "ابنِ Model Routing Dashboard فوق benchmark harness داخلي بدل اختيار الموديلات بالحدس.",
        ],
    )

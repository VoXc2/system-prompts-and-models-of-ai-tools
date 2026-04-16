"""Dealix Sovereign Growth, Execution & Governance OS kernel."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.config import Settings


class ExecutionMode(str, Enum):
    AUTO = "auto"
    AUTO_WITH_APPROVAL = "auto_with_approval"
    BLOCKED = "blocked"


class ApprovalClass(str, Enum):
    AUTO_ALLOWED = "auto_allowed"
    APPROVAL_REQUIRED = "approval_required"
    FORBIDDEN = "forbidden"


class ReversibilityClass(str, Enum):
    REVERSIBLE = "reversible"
    CONTROLLED = "controlled_rollback"
    IRREVERSIBLE = "irreversible"


class SensitivityClass(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class SurfaceStatus(str, Enum):
    LIVE = "live"
    PARTIAL = "partial"
    MISSING = "missing"


class EvidenceRequirement(BaseModel):
    key: str
    title_ar: str
    required: bool = True


class GovernedActionPolicy(BaseModel):
    action_key: str
    action_name_ar: str
    domain: str
    default_execution_mode: ExecutionMode
    approval_class: ApprovalClass
    reversibility_class: ReversibilityClass
    sensitivity_class: SensitivityClass
    approval_roles: List[str] = Field(default_factory=list)
    policy_refs: List[str] = Field(default_factory=list)
    evidence_requirements: List[EvidenceRequirement] = Field(default_factory=list)
    rationale_ar: str


class GovernedActionRequest(BaseModel):
    action_key: str
    financial_commitment_sar: Optional[float] = Field(default=None, ge=0)
    external_commitment: bool = False
    touches_sensitive_data: bool = False
    rollout_target: Optional[str] = Field(default=None, description="prod|staging|internal")
    approval_ticket_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class GovernedActionDecision(BaseModel):
    action_key: str
    resolved_execution_mode: ExecutionMode
    can_execute_now: bool
    requires_approval: bool
    approval_roles: List[str]
    policy: GovernedActionPolicy
    reasons_ar: List[str]
    blockers: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OperatingSurface(BaseModel):
    key: str
    title_ar: str
    domain: str
    status: SurfaceStatus
    endpoint: str
    owner_hint: str


class PlaneStatus(BaseModel):
    plane: str
    status: SurfaceStatus
    capabilities: Dict[str, Any]
    gaps: List[str] = Field(default_factory=list)


class ControlCenterSnapshot(BaseModel):
    planes: List[PlaneStatus]
    surfaces: List[OperatingSurface]
    readiness_score_percent: float
    readiness_breakdown: Dict[str, Any]
    commitment_controls: Dict[str, Any]
    runtime: Dict[str, Any]


class ReadinessCriterion(BaseModel):
    key: str
    title_ar: str
    description_ar: str
    enforceable: bool


def _policy(
    *,
    action_key: str,
    action_name_ar: str,
    domain: str,
    mode: ExecutionMode,
    approval_class: ApprovalClass,
    reversibility: ReversibilityClass,
    sensitivity: SensitivityClass,
    rationale_ar: str,
    approval_roles: Optional[List[str]] = None,
) -> GovernedActionPolicy:
    return GovernedActionPolicy(
        action_key=action_key,
        action_name_ar=action_name_ar,
        domain=domain,
        default_execution_mode=mode,
        approval_class=approval_class,
        reversibility_class=reversibility,
        sensitivity_class=sensitivity,
        approval_roles=approval_roles or [],
        policy_refs=["approval_class", "reversibility_class", "sensitivity_class"],
        evidence_requirements=[
            EvidenceRequirement(key="trace_id", title_ar="معرّف تتبع القرار"),
            EvidenceRequirement(key="evidence_pack", title_ar="حزمة أدلة القرار"),
        ],
        rationale_ar=rationale_ar,
    )


_AUTO_POLICIES = [
    ("lead_capture", "التقاط العملاء", "sales_revenue_os"),
    ("enrichment", "إثراء البيانات", "sales_revenue_os"),
    ("scoring", "التقييم الذكي", "sales_revenue_os"),
    ("routing", "توجيه الفرص", "sales_revenue_os"),
    ("follow_ups", "المتابعات", "sales_revenue_os"),
    ("meeting_reminders", "تذكيرات الاجتماعات", "sales_revenue_os"),
    ("memo_drafting", "صياغة المذكرات", "executive_board_os"),
    ("evidence_pack_assembly", "تجميع حزم الأدلة", "executive_board_os"),
    ("dd_checklist_orchestration", "تنسيق قوائم الفحص النافي للجهالة", "mna_os"),
    ("task_assignment", "تعيين المهام", "pmi_pmo_os"),
    ("sla_reminders", "تنبيهات SLA", "pmi_pmo_os"),
    ("dashboard_updates", "تحديث اللوحات", "executive_board_os"),
    ("telemetry", "التتبّع التشغيلي", "operating_plane"),
    ("quality_checks", "فحوص الجودة", "data_plane"),
    ("document_extraction", "استخراج المستندات", "data_plane"),
    ("connector_syncs", "مزامنة الموصلات", "data_plane"),
    ("variance_detection", "كشف الانحرافات", "executive_board_os"),
    ("anomaly_alerts", "تنبيهات الشذوذ", "executive_board_os"),
]


_APPROVAL_POLICIES = [
    ("send_term_sheet", "إرسال ورقة شروط", "partnership_os", ReversibilityClass.CONTROLLED),
    ("request_signature", "طلب توقيع", "sales_revenue_os", ReversibilityClass.IRREVERSIBLE),
    ("activate_strategic_partnership", "تفعيل شراكة استراتيجية", "partnership_os", ReversibilityClass.CONTROLLED),
    ("launch_new_market_entry", "إطلاق دخول سوق جديد", "expansion_os", ReversibilityClass.CONTROLLED),
    ("approve_discount_outside_policy", "اعتماد خصم خارج السياسة", "sales_revenue_os", ReversibilityClass.CONTROLLED),
    ("send_mna_offer", "إرسال عرض استحواذ", "mna_os", ReversibilityClass.IRREVERSIBLE),
    ("closing_approvals", "اعتمادات الإغلاق", "mna_os", ReversibilityClass.IRREVERSIBLE),
    ("high_sensitivity_data_sharing", "مشاركة بيانات عالية الحساسية", "trust_plane", ReversibilityClass.IRREVERSIBLE),
    ("rollout_to_production", "إطلاق للإنتاج", "operating_plane", ReversibilityClass.CONTROLLED),
    ("external_capital_commitment", "التزام رأسمالي خارجي", "mna_os", ReversibilityClass.IRREVERSIBLE),
]


ACTION_POLICIES: Dict[str, GovernedActionPolicy] = {
    p[0]: _policy(
        action_key=p[0],
        action_name_ar=p[1],
        domain=p[2],
        mode=ExecutionMode.AUTO,
        approval_class=ApprovalClass.AUTO_ALLOWED,
        reversibility=ReversibilityClass.REVERSIBLE,
        sensitivity=SensitivityClass.LOW,
        rationale_ar="نشاط منخفض المخاطر وقابل للعكس، ينفذ تلقائيًا.",
    )
    for p in _AUTO_POLICIES
}

for item in _APPROVAL_POLICIES:
    ACTION_POLICIES[item[0]] = _policy(
        action_key=item[0],
        action_name_ar=item[1],
        domain=item[2],
        mode=ExecutionMode.AUTO_WITH_APPROVAL,
        approval_class=ApprovalClass.APPROVAL_REQUIRED,
        reversibility=item[3],
        sensitivity=SensitivityClass.HIGH,
        rationale_ar="هذا الإجراء يولّد التزامًا خارجيًا أو غير قابل للعكس، ويتطلب موافقة بشرية.",
        approval_roles=["owner", "admin", "manager"],
    )

ACTION_POLICIES["commit_irreversible_without_approval"] = _policy(
    action_key="commit_irreversible_without_approval",
    action_name_ar="التزام غير قابل للعكس بدون اعتماد",
    domain="trust_plane",
    mode=ExecutionMode.BLOCKED,
    approval_class=ApprovalClass.FORBIDDEN,
    reversibility=ReversibilityClass.IRREVERSIBLE,
    sensitivity=SensitivityClass.CRITICAL,
    rationale_ar="سلوك محظور بالكامل.",
)


SURFACE_REGISTRY: List[OperatingSurface] = [
    OperatingSurface(key="executive_room", title_ar="غرفة التنفيذيين", domain="executive_board_os", status=SurfaceStatus.LIVE, endpoint="/api/v1/autonomous-foundation/dashboard/executive-roi", owner_hint="executive"),
    OperatingSurface(key="approval_center", title_ar="مركز الاعتمادات", domain="trust_plane", status=SurfaceStatus.LIVE, endpoint="/api/v1/operations/approvals", owner_hint="operations"),
    OperatingSurface(key="evidence_pack_viewer", title_ar="عارض حزم الأدلة", domain="trust_plane", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/autonomous-foundation/openclaw/runs", owner_hint="risk"),
    OperatingSurface(key="partner_room", title_ar="غرفة الشركاء", domain="partnership_os", status=SurfaceStatus.LIVE, endpoint="/api/v1/strategic-deals/profiles", owner_hint="partnerships"),
    OperatingSurface(key="dd_room", title_ar="غرفة الفحص النافي للجهالة", domain="mna_os", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/strategic-deals", owner_hint="corpdev"),
    OperatingSurface(key="risk_board", title_ar="لوحة المخاطر", domain="executive_board_os", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/operations/snapshot", owner_hint="risk"),
    OperatingSurface(key="policy_violations_board", title_ar="لوحة مخالفات السياسات", domain="trust_plane", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/autonomous-foundation/openclaw/policy/check", owner_hint="trust"),
    OperatingSurface(key="actual_vs_forecast_dashboard", title_ar="لوحة الفعلي مقابل المتوقع", domain="executive_board_os", status=SurfaceStatus.LIVE, endpoint="/api/v1/autonomous-foundation/intelligence/predictive", owner_hint="finance"),
    OperatingSurface(key="revenue_funnel_control_center", title_ar="مركز تحكم قمع الإيرادات", domain="sales_revenue_os", status=SurfaceStatus.LIVE, endpoint="/api/v1/sales-os/overview", owner_hint="sales"),
    OperatingSurface(key="partnership_scorecards", title_ar="بطاقات أداء الشراكات", domain="partnership_os", status=SurfaceStatus.LIVE, endpoint="/api/v1/strategic-deals/analytics/overview", owner_hint="partnerships"),
    OperatingSurface(key="mna_pipeline_board", title_ar="لوحة خط أنابيب الاستحواذ", domain="mna_os", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/strategic-deals?deal_type=acquisition", owner_hint="corpdev"),
    OperatingSurface(key="expansion_launch_console", title_ar="كونسول إطلاق التوسع", domain="expansion_os", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/autonomous-foundation/integrations/go-live-gate", owner_hint="growth"),
    OperatingSurface(key="pmi_30_60_90_engine", title_ar="محرك PMI 30/60/90", domain="pmi_pmo_os", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/operations/approvals/sla", owner_hint="pmo"),
    OperatingSurface(key="tool_verification_ledger", title_ar="دفتر تحقق الأدوات", domain="trust_plane", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/operations/snapshot", owner_hint="trust"),
    OperatingSurface(key="connector_health_board", title_ar="لوحة صحة الموصلات", domain="data_plane", status=SurfaceStatus.LIVE, endpoint="/api/v1/operations/integration-connectors", owner_hint="data"),
    OperatingSurface(key="release_gate_dashboard", title_ar="لوحة بوابة الإصدار", domain="operating_plane", status=SurfaceStatus.LIVE, endpoint="/api/v1/autonomous-foundation/integrations/live-readiness", owner_hint="platform"),
    OperatingSurface(key="saudi_compliance_matrix", title_ar="مصفوفة الامتثال السعودي", domain="trust_plane", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/compliance/health", owner_hint="compliance"),
    OperatingSurface(key="model_routing_dashboard", title_ar="لوحة توجيه النماذج", domain="decision_plane", status=SurfaceStatus.PARTIAL, endpoint="/api/v1/revenue-room/status", owner_hint="ai_platform"),
]


def list_governed_action_policies() -> List[GovernedActionPolicy]:
    return list(ACTION_POLICIES.values())


def list_operating_surfaces() -> List[OperatingSurface]:
    return SURFACE_REGISTRY


def evaluate_governed_action(request: GovernedActionRequest) -> GovernedActionDecision:
    policy = ACTION_POLICIES.get(request.action_key)
    if not policy:
        policy = _policy(
            action_key=request.action_key,
            action_name_ar=f"إجراء غير مصنّف: {request.action_key}",
            domain="decision_plane",
            mode=ExecutionMode.AUTO_WITH_APPROVAL,
            approval_class=ApprovalClass.APPROVAL_REQUIRED,
            reversibility=ReversibilityClass.CONTROLLED,
            sensitivity=SensitivityClass.MODERATE,
            rationale_ar="الإجراء غير معروف؛ يُحوَّل تلقائيًا لمسار يعتمد موافقة بشرية.",
            approval_roles=["owner", "admin"],
        )

    mode = policy.default_execution_mode
    reasons = [policy.rationale_ar]
    blockers: List[str] = []

    if request.external_commitment and mode == ExecutionMode.AUTO:
        mode = ExecutionMode.AUTO_WITH_APPROVAL
        reasons.append("تمت الترقية إلى مسار اعتماد بسبب وجود التزام خارجي.")

    if request.rollout_target == "prod" and mode != ExecutionMode.BLOCKED:
        mode = ExecutionMode.AUTO_WITH_APPROVAL
        reasons.append("أي إجراء على بيئة الإنتاج يحتاج اعتمادًا مسبقًا.")

    if request.financial_commitment_sar and request.financial_commitment_sar >= 100_000 and mode != ExecutionMode.BLOCKED:
        mode = ExecutionMode.AUTO_WITH_APPROVAL
        reasons.append("قيمة الالتزام المالي مرتفعة وتتطلب اعتمادًا.")

    if request.touches_sensitive_data and mode == ExecutionMode.AUTO:
        mode = ExecutionMode.AUTO_WITH_APPROVAL
        reasons.append("الإجراء يمس بيانات حساسة ولذلك يتطلب اعتمادًا.")

    requires_approval = mode == ExecutionMode.AUTO_WITH_APPROVAL
    if requires_approval and not request.approval_ticket_id:
        blockers.append("approval_ticket_missing")
    if mode == ExecutionMode.BLOCKED:
        blockers.append("policy_blocked_action")

    can_execute_now = mode == ExecutionMode.AUTO or (
        mode == ExecutionMode.AUTO_WITH_APPROVAL and bool(request.approval_ticket_id)
    )

    return GovernedActionDecision(
        action_key=request.action_key,
        resolved_execution_mode=mode,
        can_execute_now=can_execute_now,
        requires_approval=requires_approval,
        approval_roles=policy.approval_roles,
        policy=policy,
        reasons_ar=reasons,
        blockers=blockers,
        metadata={
            "approval_class": policy.approval_class.value,
            "reversibility_class": policy.reversibility_class.value,
            "sensitivity_class": policy.sensitivity_class.value,
        },
    )


def _to_surface_status(score: float) -> SurfaceStatus:
    if score >= 0.8:
        return SurfaceStatus.LIVE
    if score >= 0.5:
        return SurfaceStatus.PARTIAL
    return SurfaceStatus.MISSING


def _plane_statuses(settings: Settings) -> List[PlaneStatus]:
    responses_ready = bool(settings.OPENAI_API_KEY)
    decision_score = 0.8 if responses_ready else 0.6
    execution_score = 0.75 if settings.OPENCLAW_SAFE_CORE_ENABLED else 0.5
    trust_score = 0.7 if settings.OPENCLAW_APPROVAL_SLA_HOURS_BREACH > 0 else 0.4
    data_score = 0.7 if settings.EMBEDDING_PROVIDER else 0.4
    operating_score = 0.8 if settings.EXPOSE_OPENAPI else 0.65

    return [
        PlaneStatus(
            plane="decision_plane",
            status=_to_surface_status(decision_score),
            capabilities={
                "structured_outputs_contracts": True,
                "responses_api_ready": responses_ready,
                "guardrails_policy_router": True,
                "tracing_hooks": True,
            },
            gaps=[] if responses_ready else ["OPENAI_API_KEY not configured for Responses API by default"],
        ),
        PlaneStatus(
            plane="execution_plane",
            status=_to_surface_status(execution_score),
            capabilities={
                "durable_workflows": settings.OPENCLAW_SAFE_CORE_ENABLED,
                "hitl_interrupts": True,
                "approval_sla_controls": True,
            },
            gaps=[] if settings.OPENCLAW_SAFE_CORE_ENABLED else ["Safe core runtime disabled"],
        ),
        PlaneStatus(
            plane="trust_plane",
            status=_to_surface_status(trust_score),
            capabilities={
                "approval_classes": True,
                "reversibility_classes": True,
                "sensitivity_classes": True,
                "audit_trail": True,
            },
            gaps=[],
        ),
        PlaneStatus(
            plane="data_plane",
            status=_to_surface_status(data_score),
            capabilities={
                "operational_truth_postgres": True,
                "semantic_memory_ready": bool(settings.EMBEDDING_MODEL),
                "connector_sync_governance": True,
            },
            gaps=[] if settings.EMBEDDING_MODEL else ["Embedding model not configured"],
        ),
        PlaneStatus(
            plane="operating_plane",
            status=_to_surface_status(operating_score),
            capabilities={
                "release_gates": True,
                "environment_controls": True,
                "deployment_readiness_checks": True,
            },
            gaps=[] if settings.EXPOSE_OPENAPI else ["OpenAPI docs disabled in current settings"],
        ),
    ]


def _readiness_breakdown(surfaces: List[OperatingSurface]) -> Dict[str, Any]:
    total = len(surfaces)
    live = sum(1 for item in surfaces if item.status == SurfaceStatus.LIVE)
    partial = sum(1 for item in surfaces if item.status == SurfaceStatus.PARTIAL)
    missing = total - live - partial
    score = ((live + (partial * 0.5)) / max(total, 1)) * 100
    by_domain: Dict[str, Dict[str, int]] = {}
    for item in surfaces:
        bucket = by_domain.setdefault(item.domain, {"live": 0, "partial": 0, "missing": 0})
        bucket[item.status.value] += 1
    return {
        "total_required_surfaces": total,
        "live": live,
        "partial": partial,
        "missing": missing,
        "by_domain": by_domain,
        "score_percent": round(score, 1),
    }


def build_control_center_snapshot(
    *,
    settings: Settings,
    runtime: Optional[Dict[str, Any]] = None,
) -> ControlCenterSnapshot:
    surfaces = list_operating_surfaces()
    readiness = _readiness_breakdown(surfaces)
    auto_actions = sum(
        1 for item in ACTION_POLICIES.values() if item.default_execution_mode == ExecutionMode.AUTO
    )
    approval_actions = sum(
        1
        for item in ACTION_POLICIES.values()
        if item.default_execution_mode == ExecutionMode.AUTO_WITH_APPROVAL
    )
    blocked_actions = sum(
        1 for item in ACTION_POLICIES.values() if item.default_execution_mode == ExecutionMode.BLOCKED
    )

    return ControlCenterSnapshot(
        planes=_plane_statuses(settings),
        surfaces=surfaces,
        readiness_score_percent=readiness["score_percent"],
        readiness_breakdown=readiness,
        commitment_controls={
            "auto_actions": auto_actions,
            "approval_gated_actions": approval_actions,
            "blocked_actions": blocked_actions,
            "contract_model": "approval + reversibility + sensitivity",
        },
        runtime=runtime or {
            "pending_approvals": 0,
            "domain_events_24h": 0,
            "audit_events_24h": 0,
        },
    )


def readiness_definition() -> List[ReadinessCriterion]:
    return [
        ReadinessCriterion(
            key="structured_evidence_backed_decisions",
            title_ar="قرارات مهيكلة ومدعومة بالأدلة",
            description_ar="كل قرار مؤثر يصدر بصيغة Typed مع أدلة وسياق اعتماد.",
            enforceable=True,
        ),
        ReadinessCriterion(
            key="durable_long_running_commitments",
            title_ar="التزامات طويلة العمر قابلة للاستئناف",
            description_ar="كل التزامات طويلة الأمد تعمل عبر workflow durable/resumable.",
            enforceable=True,
        ),
        ReadinessCriterion(
            key="commitment_metadata_triplet",
            title_ar="ثلاثية الحوكمة لكل إجراء حساس",
            description_ar="كل فعل حساس يحمل Approval/Reversibility/Sensitivity metadata.",
            enforceable=True,
        ),
        ReadinessCriterion(
            key="versioned_connector_contracts",
            title_ar="عقود موصلات مُرقّمة",
            description_ar="كل connector يلتزم version/retry/idempotency/audit mapping.",
            enforceable=True,
        ),
        ReadinessCriterion(
            key="release_policy_controls",
            title_ar="حوكمة إصدار مؤسسية",
            description_ar="كل release يمر عبر قواعد merge/deploy/provenance قابلة للتدقيق.",
            enforceable=True,
        ),
        ReadinessCriterion(
            key="traceable_surfaces",
            title_ar="قابلية تتبع شاملة",
            description_ar="كل surface يحمل trace_id/correlation_id وlogs قابلة للتحليل.",
            enforceable=True,
        ),
        ReadinessCriterion(
            key="agentic_security_controls",
            title_ar="ضوابط أمنية للطبقة العاملية",
            description_ar="الأسطح العاملية لها controls للأمن، الحراسة، واختبارات حمراء.",
            enforceable=False,
        ),
        ReadinessCriterion(
            key="saudi_pdpl_nca_mapping",
            title_ar="مواءمة PDPL/NCA",
            description_ar="كل workflow حساس في السعودية موصول بتحكمات امتثال محلية.",
            enforceable=False,
        ),
    ]

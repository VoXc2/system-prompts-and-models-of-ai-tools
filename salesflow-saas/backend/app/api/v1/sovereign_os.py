"""Dealix Sovereign Growth, Execution & Governance OS control center."""

from __future__ import annotations

import os
from collections import defaultdict
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_optional_user
from app.database import get_db
from app.models.operations import ApprovalRequest
from app.models.strategic_deal import CompanyProfile, DealMatch, DealStatus, StrategicDeal
from app.models.user import User
from app.services.audit_service import count_audits_since
from app.services.model_router import get_router
from app.services.operations_hub import (
    count_events_since,
    count_pending_approvals,
    list_integration_connectors,
)

router = APIRouter(prefix="/sovereign-os", tags=["Sovereign Growth OS"])

Status = Literal["live", "partial", "planned"]
PlaneId = Literal["decision", "execution", "trust", "data", "operating"]


class SovereignMetric(BaseModel):
    label_ar: str
    value: str


class RoomDefinition(BaseModel):
    id: str
    plane_id: PlaneId
    name_ar: str
    name_en: str
    status: Status
    outcome_ar: str
    approval_class: str
    reversibility_class: str
    sensitivity_class: str
    evidence_source: str
    primary_surface: str
    metric: Optional[SovereignMetric] = None


class PlaneDefinition(BaseModel):
    id: PlaneId
    name_ar: str
    name_en: str
    mission_ar: str
    operating_model_ar: str
    status: Status
    trace_ar: str
    rooms: List[RoomDefinition]


class ComplianceControl(BaseModel):
    framework: str
    control_ar: str
    status: Status
    mapped_surface: str


class ModelRoute(BaseModel):
    provider: str
    role_ar: str
    configured: bool
    tasks: List[str]


class AutomationLane(BaseModel):
    title_ar: str
    policy_ar: str
    examples: List[str]


class SovereignSnapshot(BaseModel):
    demo_mode: bool
    pending_approvals: int
    domain_events_24h: int
    audit_events_24h: int
    connectors_total: int
    connectors_healthy: int
    company_profiles_total: int
    strategic_deals_total: int
    active_matches_total: int
    dd_rooms_live: int
    policy_alerts_total: int
    note_ar: str


class SovereignControlCenter(BaseModel):
    product_name: str
    product_tagline_ar: str
    executive_thesis_ar: str
    snapshot: SovereignSnapshot
    planes: List[PlaneDefinition]
    automation_matrix: List[AutomationLane]
    compliance_matrix: List[ComplianceControl]
    model_routing: List[ModelRoute]


def _provider_configured(provider: str) -> bool:
    if provider == "groq":
        return bool((os.getenv("GROQ_API_KEY") or "").strip())
    if provider == "glm5":
        return bool((os.getenv("ZAI_API_KEY") or "").strip())
    if provider == "claude":
        return bool((os.getenv("ANTHROPIC_API_KEY") or "").strip())
    if provider == "gemini":
        return bool((os.getenv("GOOGLE_API_KEY") or "").strip())
    if provider == "deepseek":
        return bool((os.getenv("DEEPSEEK_API_KEY") or "").strip())
    return False


def _model_routes() -> List[ModelRoute]:
    router_instance = get_router()
    grouped: Dict[str, List[str]] = defaultdict(list)
    for task, provider in sorted(router_instance.ROUTING_TABLE.items()):
        grouped[provider].append(task)

    labels = {
        "glm5": "قرارات البيع والاستراتيجية",
        "groq": "تصنيف سريع وتشغيل منخفض الكمون",
        "claude": "صياغة العروض والمحتوى التنفيذي",
        "gemini": "بحث وتحليل وثائق وسوق",
        "deepseek": "تكاملات وهندسة وبرمجة",
    }
    ordered = ["groq", "glm5", "claude", "gemini", "deepseek"]
    return [
        ModelRoute(
            provider=provider,
            role_ar=labels.get(provider, "توجيه مهام"),
            configured=_provider_configured(provider),
            tasks=grouped.get(provider, []),
        )
        for provider in ordered
        if provider in grouped
    ]


async def _live_snapshot(db: AsyncSession, user: Optional[User]) -> SovereignSnapshot:
    if not user:
        return SovereignSnapshot(
            demo_mode=True,
            pending_approvals=0,
            domain_events_24h=0,
            audit_events_24h=0,
            connectors_total=4,
            connectors_healthy=0,
            company_profiles_total=0,
            strategic_deals_total=0,
            active_matches_total=0,
            dd_rooms_live=0,
            policy_alerts_total=0,
            note_ar="وضع توضيحي: سجّل الدخول لعرض مؤشرات المستأجر وربطها بالحوكمة والتنفيذ.",
        )

    pending_approvals = await count_pending_approvals(db, user.tenant_id)
    domain_events_24h = await count_events_since(db, user.tenant_id, 24)
    audit_events_24h = await count_audits_since(db, user.tenant_id, 24)
    connectors = await list_integration_connectors(db, user.tenant_id)
    healthy_connectors = sum(1 for item in connectors if item.get("status") == "ok")
    degraded_connectors = sum(
        1 for item in connectors if item.get("status") in {"degraded", "error"}
    )

    profiles_total = int(
        (
            await db.execute(
                select(func.count()).select_from(CompanyProfile).where(
                    CompanyProfile.tenant_id == user.tenant_id
                )
            )
        ).scalar()
        or 0
    )
    deals_total = int(
        (
            await db.execute(
                select(func.count()).select_from(StrategicDeal).where(
                    StrategicDeal.tenant_id == user.tenant_id
                )
            )
        ).scalar()
        or 0
    )
    matches_total = int(
        (
            await db.execute(
                select(func.count()).select_from(DealMatch).where(
                    DealMatch.tenant_id == user.tenant_id
                )
            )
        ).scalar()
        or 0
    )
    dd_rooms_live = int(
        (
            await db.execute(
                select(func.count()).select_from(StrategicDeal).where(
                    StrategicDeal.tenant_id == user.tenant_id,
                    StrategicDeal.status == DealStatus.DUE_DILIGENCE.value,
                )
            )
        ).scalar()
        or 0
    )
    pending_exec_reviews = int(
        (
            await db.execute(
                select(func.count()).select_from(ApprovalRequest).where(
                    ApprovalRequest.tenant_id == user.tenant_id,
                    ApprovalRequest.status == "pending",
                )
            )
        ).scalar()
        or 0
    )
    policy_alerts_total = pending_exec_reviews + degraded_connectors

    return SovereignSnapshot(
        demo_mode=False,
        pending_approvals=pending_approvals,
        domain_events_24h=domain_events_24h,
        audit_events_24h=audit_events_24h,
        connectors_total=len(connectors),
        connectors_healthy=healthy_connectors,
        company_profiles_total=profiles_total,
        strategic_deals_total=deals_total,
        active_matches_total=matches_total,
        dd_rooms_live=dd_rooms_live,
        policy_alerts_total=policy_alerts_total,
        note_ar="السطح التنفيذي موصول الآن بموافقات التشغيل، التدقيق، الموصلات، والصفقات الاستراتيجية.",
    )


def _room_catalog(snapshot: SovereignSnapshot, model_routes: List[ModelRoute]) -> List[RoomDefinition]:
    configured_providers = sum(1 for item in model_routes if item.configured)
    return [
        RoomDefinition(
            id="executive-room",
            plane_id="decision",
            name_ar="Executive Room",
            name_en="Executive Room",
            status="live",
            outcome_ar="عرض القرار والأثر والمخاطر وبدائل التنفيذ.",
            approval_class="C",
            reversibility_class="R3",
            sensitivity_class="S2",
            evidence_source="domain_events + audit_logs + strategic_deals",
            primary_surface="/dashboard → Dealix Sovereign OS",
            metric=SovereignMetric(label_ar="صفقات استراتيجية", value=str(snapshot.strategic_deals_total)),
        ),
        RoomDefinition(
            id="approval-center",
            plane_id="trust",
            name_ar="Approval Center",
            name_en="Approval Center",
            status="live",
            outcome_ar="تجميع القرارات الحساسة قبل أي التزام خارجي أو غير قابل للعكس.",
            approval_class="B/C",
            reversibility_class="R2/R3",
            sensitivity_class="S2/S3",
            evidence_source="approval_requests + escalation + audit_logs",
            primary_surface="/api/v1/operations/approvals",
            metric=SovereignMetric(label_ar="طلبات معلّقة", value=str(snapshot.pending_approvals)),
        ),
        RoomDefinition(
            id="evidence-pack-viewer",
            plane_id="trust",
            name_ar="Evidence Pack Viewer",
            name_en="Evidence Pack Viewer",
            status="live",
            outcome_ar="تجميع الأثر والأحداث والسجل لكل قرار أو تصعيد.",
            approval_class="A/B",
            reversibility_class="R1/R2",
            sensitivity_class="S2",
            evidence_source="tool_receipts + tool_verification + audit_logs",
            primary_surface="/api/v1/operations/audit-logs",
            metric=SovereignMetric(label_ar="أحداث تدقيق 24س", value=str(snapshot.audit_events_24h)),
        ),
        RoomDefinition(
            id="partner-room",
            plane_id="execution",
            name_ar="Partner Room",
            name_en="Partner Room",
            status="live",
            outcome_ar="إدارة اكتشاف الشركاء، المطابقة، والتفعيل التشغيلي.",
            approval_class="B",
            reversibility_class="R2",
            sensitivity_class="S2",
            evidence_source="deal_matches + strategic_deals + company_profiles",
            primary_surface="/api/v1/strategic-deals",
            metric=SovereignMetric(label_ar="مطابقات نشطة", value=str(snapshot.active_matches_total)),
        ),
        RoomDefinition(
            id="dd-room",
            plane_id="execution",
            name_ar="DD Room",
            name_en="DD Room",
            status="live",
            outcome_ar="التحكم في تدفقات العناية الواجبة ومسارات المتابعة طويلة العمر.",
            approval_class="C",
            reversibility_class="R3",
            sensitivity_class="S3",
            evidence_source="strategic_deals(status=due_diligence) + audit_logs",
            primary_surface="/api/v1/strategic-deals",
            metric=SovereignMetric(label_ar="غرف DD حيّة", value=str(snapshot.dd_rooms_live)),
        ),
        RoomDefinition(
            id="risk-board",
            plane_id="trust",
            name_ar="Risk Board",
            name_en="Risk Board",
            status="partial",
            outcome_ar="تجميع إنذارات التنفيذ والموصلات والموافقات المتأخرة في لوحة واحدة.",
            approval_class="B/C",
            reversibility_class="R2/R3",
            sensitivity_class="S2/S3",
            evidence_source="operations_snapshot + observability + escalation",
            primary_surface="/api/v1/operations/snapshot",
            metric=SovereignMetric(label_ar="تنبيهات سياسة", value=str(snapshot.policy_alerts_total)),
        ),
        RoomDefinition(
            id="policy-violations-board",
            plane_id="trust",
            name_ar="Policy Violations Board",
            name_en="Policy Violations Board",
            status="partial",
            outcome_ar="رصد الانحرافات عن Approval / Reversibility / Sensitivity classes.",
            approval_class="B/C",
            reversibility_class="R2/R3",
            sensitivity_class="S3",
            evidence_source="security_gate + outbound_governance + channel_compliance",
            primary_surface="/api/v1/operations/snapshot",
        ),
        RoomDefinition(
            id="actual-vs-forecast",
            plane_id="decision",
            name_ar="Actual vs Forecast Dashboard",
            name_en="Actual vs Forecast Dashboard",
            status="partial",
            outcome_ar="ربط الواقع التشغيلي بالمسار والفرص المتوقع إغلاقها.",
            approval_class="A",
            reversibility_class="R1",
            sensitivity_class="S1",
            evidence_source="sales_os + executive_roi + forecasting",
            primary_surface="/api/v1/autonomous-foundation/dashboard/executive-roi",
        ),
        RoomDefinition(
            id="revenue-funnel-control-center",
            plane_id="execution",
            name_ar="Revenue Funnel Control Center",
            name_en="Revenue Funnel Control Center",
            status="live",
            outcome_ar="تشغيل funnel من capture إلى close ضمن سياسات واضحة.",
            approval_class="A/B",
            reversibility_class="R1/R2",
            sensitivity_class="S1/S2",
            evidence_source="sales_os + pipeline + leads",
            primary_surface="/api/v1/sales-os/overview",
            metric=SovereignMetric(label_ar="ملفات شركات", value=str(snapshot.company_profiles_total)),
        ),
        RoomDefinition(
            id="partnership-scorecards",
            plane_id="decision",
            name_ar="Partnership Scorecards",
            name_en="Partnership Scorecards",
            status="partial",
            outcome_ar="ترجمة fit والاقتصاديات والاعتمادات إلى scorecard تشغيلية.",
            approval_class="B",
            reversibility_class="R2",
            sensitivity_class="S2",
            evidence_source="deal_matcher + roi_engine + strategic_simulator",
            primary_surface="/api/v1/strategic-deals/matches",
        ),
        RoomDefinition(
            id="mna-pipeline-board",
            plane_id="decision",
            name_ar="M&A Pipeline Board",
            name_en="M&A Pipeline Board",
            status="partial",
            outcome_ar="عرض targets، fit، DD، وخطوات العرض غير القابلة للعكس.",
            approval_class="C",
            reversibility_class="R3",
            sensitivity_class="S3",
            evidence_source="acquisition_scouting + strategic_deals + dd_room",
            primary_surface="/api/v1/strategic-deals",
        ),
        RoomDefinition(
            id="expansion-launch-console",
            plane_id="execution",
            name_ar="Expansion Launch Console",
            name_en="Expansion Launch Console",
            status="planned",
            outcome_ar="إطلاق سوق جديد مع canary و stop-loss و partner-assisted entry.",
            approval_class="C",
            reversibility_class="R3",
            sensitivity_class="S3",
            evidence_source="launch_checklists + canary_context + release gates",
            primary_surface="memory/runbooks/launch-checklist",
        ),
        RoomDefinition(
            id="pmi-engine",
            plane_id="execution",
            name_ar="PMI 30/60/90 Engine",
            name_en="PMI 30/60/90 Engine",
            status="planned",
            outcome_ar="تشغيل Day-1 وخطط 30/60/90 مع ملاك واعتماد وتصعيد.",
            approval_class="C",
            reversibility_class="R3",
            sensitivity_class="S2",
            evidence_source="durable_execution + audit trail + owners",
            primary_surface="memory/runbooks/operations-schedule",
        ),
        RoomDefinition(
            id="tool-verification-ledger",
            plane_id="trust",
            name_ar="Tool Verification Ledger",
            name_en="Tool Verification Ledger",
            status="live",
            outcome_ar="ربط claim بالفعل الفعلي والدليل والحكم النهائي.",
            approval_class="A/B",
            reversibility_class="R1/R2",
            sensitivity_class="S2",
            evidence_source="tool_verification + tool_receipts",
            primary_surface="app/services/tool_verification.py",
        ),
        RoomDefinition(
            id="connector-health-board",
            plane_id="data",
            name_ar="Connector Health Board",
            name_en="Connector Health Board",
            status="live",
            outcome_ar="قياس سلامة التكاملات والإعادة والمحاولات وآثار الأعطال.",
            approval_class="A/B",
            reversibility_class="R1/R2",
            sensitivity_class="S2",
            evidence_source="integration_sync_states + operations_snapshot",
            primary_surface="/api/v1/operations/snapshot",
            metric=SovereignMetric(
                label_ar="موصلات سليمة",
                value=f"{snapshot.connectors_healthy}/{snapshot.connectors_total}",
            ),
        ),
        RoomDefinition(
            id="release-gate-dashboard",
            plane_id="operating",
            name_ar="Release Gate Dashboard",
            name_en="Release Gate Dashboard",
            status="partial",
            outcome_ar="ربط بيئة التشغيل، الكناري، الاعتمادات، وقابلية التتبع قبل الدمج.",
            approval_class="C",
            reversibility_class="R3",
            sensitivity_class="S3",
            evidence_source="openclaw_canary + operations_snapshot + CI policy",
            primary_surface="/api/v1/operations/snapshot",
        ),
        RoomDefinition(
            id="saudi-compliance-matrix",
            plane_id="trust",
            name_ar="Saudi Compliance Matrix",
            name_en="Saudi Compliance Matrix",
            status="partial",
            outcome_ar="ربط الضوابط الحساسة بوعي PDPL/NCA/NIST/OWASP.",
            approval_class="B/C",
            reversibility_class="R2/R3",
            sensitivity_class="S3",
            evidence_source="pdpl + consent_manager + security_gate",
            primary_surface="memory/security/pdpl-checklist.md",
        ),
        RoomDefinition(
            id="model-routing-dashboard",
            plane_id="decision",
            name_ar="Model Routing Dashboard",
            name_en="Model Routing Dashboard",
            status="live",
            outcome_ar="إظهار fabric التوجيه حسب نوع المهمة والمزوّد المهيأ.",
            approval_class="A",
            reversibility_class="R1",
            sensitivity_class="S1",
            evidence_source="services/model_router.py",
            primary_surface="/api/v1/sovereign-os/control-center",
            metric=SovereignMetric(label_ar="مزودات مهيأة", value=str(configured_providers)),
        ),
    ]


def _planes(rooms: List[RoomDefinition]) -> List[PlaneDefinition]:
    plane_meta = {
        "decision": {
            "name_ar": "Decision Plane",
            "name_en": "Decision Plane",
            "mission_ar": "قرار structured + evidence-backed + approval-aware.",
            "operating_model_ar": "Responses / tools / routing / executive synthesis.",
            "trace_ar": "كل قرار يجب أن يخرج مع دليل، بدائل، ودرجة حساسية.",
        },
        "execution": {
            "name_ar": "Execution Plane",
            "name_en": "Execution Plane",
            "mission_ar": "تنفيذ durable للالتزامات والتسليمات الطويلة والعابرة للأنظمة.",
            "operating_model_ar": "workflow state + approvals + resumability + owners.",
            "trace_ar": "التنفيذ يعيش في workflow وليس في chat transcript.",
        },
        "trust": {
            "name_ar": "Trust Plane",
            "name_en": "Trust Plane",
            "mission_ar": "سياسات واعتمادات وتفويض وتتبع وأدلة قابلة للمراجعة.",
            "operating_model_ar": "Approval classes + sensitivity + evidence + audit trail.",
            "trace_ar": "كل فعل حساس قابل للتبرير والمراجعة لاحقًا.",
        },
        "data": {
            "name_ar": "Data Plane",
            "name_en": "Data Plane",
            "mission_ar": "حقيقة تشغيلية موحدة للكيانات والعقود والأحداث والذاكرة.",
            "operating_model_ar": "operational truth + connector health + governed ingestion.",
            "trace_ar": "البيانات القريبة من القرار يجب أن تبقى versioned وقابلة للتتبع.",
        },
        "operating": {
            "name_ar": "Operating Plane",
            "name_en": "Operating Plane",
            "mission_ar": "حوكمة المستودع والإطلاقات والبيئات والكناري وإثبات المصدر.",
            "operating_model_ar": "release gates + canary + CI/CD + provenance.",
            "trace_ar": "المنتج نفسه جزء من الحوكمة المؤسسية وليس أداة منفصلة عنها.",
        },
    }

    order: List[PlaneId] = ["decision", "execution", "trust", "data", "operating"]
    plane_rooms: Dict[PlaneId, List[RoomDefinition]] = {pid: [] for pid in order}
    for room in rooms:
        plane_rooms[room.plane_id].append(room)

    output: List[PlaneDefinition] = []
    for pid in order:
        statuses = {room.status for room in plane_rooms[pid]}
        plane_status: Status = "live"
        if "planned" in statuses and "live" not in statuses and "partial" not in statuses:
            plane_status = "planned"
        elif "partial" in statuses or "planned" in statuses:
            plane_status = "partial"
        meta = plane_meta[pid]
        output.append(
            PlaneDefinition(
                id=pid,
                name_ar=meta["name_ar"],
                name_en=meta["name_en"],
                mission_ar=meta["mission_ar"],
                operating_model_ar=meta["operating_model_ar"],
                status=plane_status,
                trace_ar=meta["trace_ar"],
                rooms=plane_rooms[pid],
            )
        )
    return output


def _automation_matrix() -> List[AutomationLane]:
    return [
        AutomationLane(
            title_ar="مؤتمت بالكامل بلا اعتماد",
            policy_ar="مسموح لأن الفعل قابل للعكس أو منخفض المخاطر ولا يصنع التزامًا خارجيًا نهائيًا.",
            examples=[
                "lead capture + enrichment + routing",
                "follow-ups + reminders + memo drafting",
                "evidence pack assembly + DD checklist orchestration",
                "connector syncs + dashboard updates + anomaly alerts",
            ],
        ),
        AutomationLane(
            title_ar="مؤتمت مع اعتماد قبل الالتزام",
            policy_ar="يمر عبر gate لأن الفعل يغيّر التزامًا تجاريًا أو قانونيًا أو تشغيليًا عالي الحساسية.",
            examples=[
                "term sheet / offer / discount outside policy",
                "external signature request / strategic partner activation",
                "market launch / prod rollout / data sharing high sensitivity",
                "closing approvals / external capital commitments",
            ],
        ),
    ]


def _compliance_matrix() -> List[ComplianceControl]:
    return [
        ComplianceControl(
            framework="PDPL",
            control_ar="فحص consent والهدف والقناة قبل أي outbound حساس.",
            status="live",
            mapped_surface="consents + pdpl consent manager + outbound governance",
        ),
        ComplianceControl(
            framework="NCA ECC",
            control_ar="حوكمة تشغيلية قابلة للتدقيق للأسرار، الوصول، والتتبع.",
            status="partial",
            mapped_surface="security_gate + audit logs + vault-ready operating model",
        ),
        ComplianceControl(
            framework="NIST AI RMF",
            control_ar="تمييز القرارات الحساسة، evidence-native outputs، وإيقاف HITL للالتزامات.",
            status="partial",
            mapped_surface="approval center + tool verification + executive room",
        ),
        ComplianceControl(
            framework="OWASP LLM",
            control_ar="تقليل المخاطر عبر tool verification، approval classes، وفصل القرار عن التنفيذ.",
            status="partial",
            mapped_surface="tool verification ledger + model routing + security gate",
        ),
    ]


@router.get("/control-center", response_model=SovereignControlCenter)
async def sovereign_control_center(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    snapshot = await _live_snapshot(db, user)
    model_routes = _model_routes()
    rooms = _room_catalog(snapshot, model_routes)
    planes = _planes(rooms)

    return SovereignControlCenter(
        product_name="Dealix Sovereign Growth, Execution & Governance OS",
        product_tagline_ar="نظام تشغيل مؤسسي حي للقرار والتنفيذ والحوكمة، عربي أولًا ومهيأ للسعودية.",
        executive_thesis_ar=(
            "النسخة الجاهزة للشركات ليست CRM ولا مجموعة agents؛ بل سطح تنفيذي يربط القرار "
            "بالدليل، والتنفيذ بالموافقة، والعمليات بالتتبع والامتثال."
        ),
        snapshot=snapshot,
        planes=planes,
        automation_matrix=_automation_matrix(),
        compliance_matrix=_compliance_matrix(),
        model_routing=model_routes,
    )

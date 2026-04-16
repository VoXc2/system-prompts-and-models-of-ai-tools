"""Assembles the Sovereign Growth OS snapshot from operational tables."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.activity import Activity
from app.models.compliance import Complaint, ComplaintStatus
from app.models.deal import Deal
from app.models.dispute import Dispute, DisputeStatus
from app.models.lead import Lead
from app.models.message import Message
from app.models.proposal import Proposal
from app.models.strategic_deal import DealStatus, DealType, StrategicDeal
from app.schemas.sovereign_os import (
    ComplianceMatrixRow,
    ModelRouteRow,
    PipelineBoard,
    PlaneHealth,
    ReleaseGateStatus,
    RiskHeatmap,
    SalesOsSignals,
    SovereignOsSnapshot,
    ToolVerificationEntry,
)
from app.services.model_router import ModelRouter


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def build_sovereign_os_snapshot(
    db: AsyncSession,
    *,
    tenant_id: Any,
    correlation_id: str | None = None,
) -> SovereignOsSnapshot:
    settings = get_settings()
    tid = tenant_id
    today_start = _now().replace(hour=0, minute=0, second=0, microsecond=0)
    horizon = _now() + timedelta(days=7)

    total_leads = (await db.execute(select(func.count()).where(Lead.tenant_id == tid))).scalar() or 0
    new_today = (
        await db.execute(select(func.count()).where(Lead.tenant_id == tid, Lead.created_at >= today_start))
    ).scalar() or 0
    total_deals = (await db.execute(select(func.count()).where(Deal.tenant_id == tid))).scalar() or 0

    open_value = (
        await db.execute(
            select(func.coalesce(func.sum(Deal.value), 0)).where(
                Deal.tenant_id == tid,
                Deal.stage.notin_(["closed_won", "closed_lost"]),
            )
        )
    ).scalar() or Decimal("0")

    won_value = (
        await db.execute(
            select(func.coalesce(func.sum(Deal.value), 0)).where(Deal.tenant_id == tid, Deal.stage == "closed_won")
        )
    ).scalar() or Decimal("0")

    won_count = (await db.execute(select(func.count()).where(Deal.tenant_id == tid, Deal.stage == "closed_won"))).scalar() or 0

    msgs_today = (
        await db.execute(
            select(func.count()).where(
                Message.tenant_id == tid,
                Message.created_at >= today_start,
                Message.direction == "outbound",
            )
        )
    ).scalar() or 0

    conversion = (won_count / total_leads * 100) if total_leads > 0 else 0.0

    meetings_7d = (
        await db.execute(
            select(func.count()).where(
                Activity.tenant_id == tid,
                Activity.type == "meeting",
                Activity.scheduled_at.isnot(None),
                Activity.scheduled_at >= _now(),
                Activity.scheduled_at <= horizon,
            )
        )
    ).scalar() or 0

    proposals_draft = (
        await db.execute(select(func.count()).where(Proposal.tenant_id == tid, Proposal.status == "draft"))
    ).scalar() or 0

    proposals_pending = (
        await db.execute(select(func.count()).where(Proposal.tenant_id == tid, Proposal.status.in_(["draft", "sent"])))
    ).scalar() or 0

    sales_os = SalesOsSignals(
        total_leads=int(total_leads),
        new_leads_today=int(new_today),
        total_deals=int(total_deals),
        open_deals_value_sar=Decimal(str(open_value)),
        closed_won_value_sar=Decimal(str(won_value)),
        closed_won_count=int(won_count),
        messages_sent_today=int(msgs_today),
        conversion_rate_pct=round(float(conversion), 2),
        active_workflows=0,
        upcoming_meetings_7d=int(meetings_7d),
        proposals_draft=int(proposals_draft),
        proposals_pending_send=int(proposals_pending),
    )

    async def strategic_slice(
        title: str,
        title_ar: str,
        type_filters: tuple[str, ...],
        limit: int = 8,
    ) -> PipelineBoard:
        q = select(StrategicDeal).where(StrategicDeal.tenant_id == tid, StrategicDeal.deal_type.in_(type_filters))
        rows = (await db.execute(q.order_by(StrategicDeal.updated_at.desc()).limit(limit))).scalars().all()
        by_stage: dict[str, int] = {}
        stage_rows = await db.execute(
            select(StrategicDeal.status, func.count())
            .where(StrategicDeal.tenant_id == tid, StrategicDeal.deal_type.in_(type_filters))
            .group_by(StrategicDeal.status)
        )
        for status, cnt in stage_rows.all():
            by_stage[str(status)] = int(cnt)
        items: list[dict[str, Any]] = []
        for d in rows:
            items.append(
                {
                    "id": str(d.id),
                    "title": d.deal_title,
                    "title_ar": d.deal_title_ar,
                    "stage": d.status,
                    "deal_type": d.deal_type,
                    "estimated_value_sar": float(d.estimated_value_sar) if d.estimated_value_sar is not None else None,
                }
            )
        total = sum(by_stage.values())
        return PipelineBoard(title=title, title_ar=title_ar, total=total, by_stage=by_stage, items=items)

    partnership = await strategic_slice(
        "Partnership OS",
        "نظام الشراكات",
        (
            DealType.PARTNERSHIP.value,
            DealType.REFERRAL.value,
            DealType.JOINT_VENTURE.value,
        ),
    )
    ma_board = await strategic_slice(
        "M&A / Corporate Development",
        "الاستحواذ والتطوير المؤسسي",
        (DealType.ACQUISITION.value,),
    )
    expansion = await strategic_slice(
        "Expansion OS",
        "نظام التوسع",
        (DealType.DISTRIBUTION.value, DealType.FRANCHISE.value),
    )

    pmi_rows = (
        await db.execute(
            select(StrategicDeal)
            .where(
                StrategicDeal.tenant_id == tid,
                StrategicDeal.status == DealStatus.CLOSED_WON.value,
            )
            .order_by(StrategicDeal.closed_at.desc(), StrategicDeal.updated_at.desc())
            .limit(8)
        )
    ).scalars().all()
    pmi_by_stage = {"integration": len(pmi_rows)} if pmi_rows else {}
    pmi_items = [
        {
            "id": str(d.id),
            "title": d.deal_title,
            "title_ar": d.deal_title_ar,
            "stage": "post_close_integration",
            "deal_type": d.deal_type,
        }
        for d in pmi_rows
    ]
    pmi_board = PipelineBoard(
        title="PMI / Strategic PMO",
        title_ar="التكامل وإدارة المشاريع الاستراتيجية",
        total=len(pmi_rows),
        by_stage=pmi_by_stage,
        items=pmi_items,
    )

    complaints_open = (
        await db.execute(
            select(func.count()).where(
                Complaint.tenant_id == tid,
                Complaint.status.in_([ComplaintStatus.RECEIVED, ComplaintStatus.INVESTIGATING, ComplaintStatus.ESCALATED]),
            )
        )
    ).scalar() or 0

    disputes_open = (
        await db.execute(
            select(func.count()).where(
                Dispute.tenant_id == tid,
                Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.INVESTIGATING, DisputeStatus.ESCALATED]),
            )
        )
    ).scalar() or 0

    policy_violations = int(complaints_open) + int(disputes_open)
    risk_score = min(100, int(complaints_open) * 12 + int(disputes_open) * 18)
    risk_drivers: list[str] = []
    if complaints_open:
        risk_drivers.append(f"{int(complaints_open)} شكاوى/بلاغات مفتوحة")
    if disputes_open:
        risk_drivers.append(f"{int(disputes_open)} نزاعات مفتوحة")

    strategic_commitment_pending = (
        await db.execute(
            select(func.count()).where(
                StrategicDeal.tenant_id == tid,
                StrategicDeal.status.in_(
                    [DealStatus.TERM_SHEET.value, DealStatus.DUE_DILIGENCE.value],
                ),
            )
        )
    ).scalar() or 0
    approvals_pending = int(proposals_pending) + int(strategic_commitment_pending)

    router = ModelRouter()
    model_fabric = [
        ModelRouteRow(task_type=k, model_slot=v) for k, v in sorted(ModelRouter.ROUTING_TABLE.items())
    ]

    ledger = [
        ToolVerificationEntry(
            tool_id="crm_core",
            last_verified_at=_now(),
            status="verified",
            connector_version="dealix-1",
        ),
        ToolVerificationEntry(
            tool_id="whatsapp_channel",
            last_verified_at=None,
            status="pending",
            connector_version=None,
        ),
    ]

    compliance_matrix = [
        ComplianceMatrixRow(
            control_id="PDPL-OUTBOUND-CONSENT",
            domain="pdpl",
            status="partial",
            evidence_hint="Consent checks must gate outbound messaging",
            evidence_hint_ar="يجب ربط الموافقات قبل أي رسالة صادرة",
        ),
        ComplianceMatrixRow(
            control_id="NCA-ECC-CRYPTO-BASELINE",
            domain="nca_ecc",
            status="partial",
            evidence_hint="Document TLS and key management for regulated workloads",
            evidence_hint_ar="وثّق التشفير وإدارة المفاتيح للأعباء الخاضعة للتنظيم",
        ),
        ComplianceMatrixRow(
            control_id="AI-RMF-GENAI",
            domain="ai_governance",
            status="partial",
            evidence_hint="Map agent actions to NIST AI RMF + OWASP LLM controls",
            evidence_hint_ar="اربط أفعال الوكلاء بضوابط NIST AI RMF وOWASP LLM",
        ),
    ]

    planes = [
        PlaneHealth(plane="decision", status="healthy", signals=["Structured snapshot", "Policy classes A/B/C"]),
        PlaneHealth(
            plane="execution",
            status="healthy" if int(meetings_7d) or int(total_deals) else "degraded",
            signals=["Celery/LangGraph short-horizon", "Temporal target for durable commitments"],
        ),
        PlaneHealth(plane="trust", status="healthy", signals=["RBAC", "Audit-oriented ledger rows"]),
        PlaneHealth(plane="data", status="healthy", signals=["Postgres operational truth", "Tenant isolation"]),
        PlaneHealth(
            plane="operating",
            status="healthy" if settings.ENVIRONMENT == "production" else "degraded",
            signals=["GitHub rulesets + OIDC recommended in prod"],
        ),
    ]

    executive = {
        "headline": "Dealix Sovereign Growth, Execution & Governance OS",
        "headline_ar": "ديلكس — نظام النمو والتنفيذ والحوكمة السيادي",
        "next_best_actions": [
            {
                "id": "nba-1",
                "title": "Clear approval queue for term sheets and non-standard CPQ",
                "title_ar": "إخلاء طابور الموافقات لورقة الشروط والعروض غير القياسية",
                "priority": "high",
            },
            {
                "id": "nba-2",
                "title": "Attach evidence packs to board-ready memos before IC review",
                "title_ar": "إرفاق حزم الأدلة بالمذكرات قبل لجنة الاستثمار",
                "priority": "medium",
            },
        ],
        "actual_vs_forecast": {
            "currency": "SAR",
            "actual_closed_won_sar": float(won_value),
            "forecast_hint": "Wire forecast model to analytics service",
        },
        "escalations_open_hint": int(disputes_open) + int(complaints_open),
    }

    return SovereignOsSnapshot(
        generated_at=_now(),
        tenant_id=str(tid),
        correlation_id=correlation_id,
        planes=planes,
        sales_os=sales_os,
        partnership=partnership,
        ma_corp_dev=ma_board,
        expansion=expansion,
        pmi_pmo=pmi_board,
        executive=executive,
        approvals_pending=approvals_pending,
        policy_violations_open=policy_violations,
        risk=RiskHeatmap(score_0_100=risk_score, drivers=risk_drivers),
        compliance_matrix=compliance_matrix,
        model_routing_fabric=model_fabric,
        tool_verification_ledger=ledger,
        release_gate=ReleaseGateStatus(
            environment=settings.ENVIRONMENT,
            rulesets_required=True,
            oidc_preferred=True,
            last_gate_check_at=_now(),
        ),
    )


def new_correlation_id() -> str:
    return str(uuid.uuid4())

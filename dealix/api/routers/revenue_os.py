"""
Revenue OS Router — single integration point for the v3 Autonomous layers.

Endpoints under /api/v1/revenue-os/:
  Memory:      /events  /timeline/{account_id}  /replay/{customer_id}
  Agents:      /workflows/run  /tasks  /tasks/{id}/approve  /tasks/{id}/reject
  Market:      /market-radar/signals  /market-radar/sectors  /market-radar/cities
               /market-radar/opportunities
  Copilot:     /copilot/ask  /copilot/intents  /copilot/actions/{id}
  Forecast:    /forecast  /attribution  /impact  /churn  /expansion
  Compliance:  /contactability  /campaign-risk  /ropa  /dsr  /dsr/{id}/process
               /vendors
  Verticals:   /verticals  /verticals/{id}  /verticals/{id}/templates
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

# Compliance OS
from auto_client_acquisition.compliance_os.consent_ledger import (
    LawfulBasis,
    record_consent,
    record_opt_out,
)
from auto_client_acquisition.compliance_os.contactability import check_contactability
from auto_client_acquisition.compliance_os.data_subject_requests import (
    DSR_TYPES,
    DSRStatus,
    dsr_dashboard,
    open_dsr,
    process_dsr,
)
from auto_client_acquisition.compliance_os.risk_engine import score_campaign_risk
from auto_client_acquisition.compliance_os.ropa import build_ropa
from auto_client_acquisition.compliance_os.vendor_registry import (
    DEFAULT_VENDORS,
    vendors_summary,
)

# Copilot
from auto_client_acquisition.copilot import ask
from auto_client_acquisition.copilot.intent_router import list_intents
from auto_client_acquisition.copilot.safe_actions import SAFE_ACTIONS, get_action

# Market Intelligence
from auto_client_acquisition.market_intelligence.opportunity_feed import (
    build_opportunity_feed,
)
from auto_client_acquisition.market_intelligence.sector_pulse import build_sector_pulse
from auto_client_acquisition.market_intelligence.signal_detectors import (
    SIGNAL_TYPES,
    SignalDetection,
    detect_ads_signal,
    detect_funding_signal,
    detect_hiring_signal,
    detect_tender_signal,
    detect_website_change,
)

# Orchestrator
from auto_client_acquisition.orchestrator.policies import (
    AutonomyMode,
    default_policy,
)
from auto_client_acquisition.orchestrator.queue import TaskQueue, TaskStatus
from auto_client_acquisition.orchestrator.runtime import DAILY_GROWTH_RUN, Orchestrator
from auto_client_acquisition.orchestrator.tools import default_executors

# Revenue Memory
from auto_client_acquisition.revenue_memory.event_store import (
    InMemoryEventStore,
    get_default_store,
)
from auto_client_acquisition.revenue_memory.events import (
    EVENT_TYPES,
    event_to_dict,
    make_event,
)
from auto_client_acquisition.revenue_memory.replay import (
    replay_for_account,
    replay_for_customer,
)
from auto_client_acquisition.revenue_memory.retention import retention_summary

# Revenue Science
from auto_client_acquisition.revenue_science.attribution import (
    compute_first_touch,
    compute_last_touch,
    compute_linear,
    compute_time_decay,
)
from auto_client_acquisition.revenue_science.causal_impact import simulate_impact
from auto_client_acquisition.revenue_science.churn_model import predict_churn
from auto_client_acquisition.revenue_science.expansion_model import predict_expansion
from auto_client_acquisition.revenue_science.forecast import compute_forecast

# Vertical OS
from auto_client_acquisition.vertical_os import (
    ALL_VERTICALS,
    get_vertical,
    list_vertical_summaries,
)

# Why-Now (used by opportunity_feed)
from auto_client_acquisition.revenue_graph.why_now import (
    WhyNowSignal,
    explain_why_now,
)

router = APIRouter(prefix="/api/v1/revenue-os", tags=["revenue-os"])
log = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Module-level singletons (in-memory adapters; production replaces) ─
_QUEUE = TaskQueue()
_ORCHESTRATOR_FACTORY = None


def _get_orchestrator(customer_id: str) -> Orchestrator:
    """Build an orchestrator with the default in-memory store + policy."""
    store = get_default_store()

    def policy_resolver(c):
        return default_policy(c)

    return Orchestrator(
        queue=_QUEUE,
        event_store=store,
        policy_resolver=policy_resolver,
        executor_registry=default_executors(),
    )


# ─────────────────────────────────────────────────────────────────
# 1. REVENUE MEMORY ENDPOINTS
# ─────────────────────────────────────────────────────────────────
@router.get("/events/types")
async def list_event_types() -> dict[str, Any]:
    """50 event types Dealix records."""
    return {"count": len(EVENT_TYPES), "event_types": list(EVENT_TYPES)}


@router.post("/events")
async def append_event(
    event_type: str = Body(..., embed=True),
    customer_id: str = Body(..., embed=True),
    subject_type: str = Body(..., embed=True),
    subject_id: str = Body(..., embed=True),
    payload: dict[str, Any] = Body(default_factory=dict, embed=True),
    actor: str = Body(default="system", embed=True),
) -> dict[str, Any]:
    """Append a new event to the customer's stream."""
    try:
        e = make_event(
            event_type=event_type,
            customer_id=customer_id,
            subject_type=subject_type,
            subject_id=subject_id,
            payload=payload,
            actor=actor,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    get_default_store().append(e)
    return {"event_id": e.event_id, "event_type": e.event_type}


@router.get("/timeline/{account_id}")
async def get_timeline(account_id: str, customer_id: str = Query(...)) -> dict[str, Any]:
    """Replay account timeline from the event stream."""
    timeline = replay_for_account(customer_id=customer_id, account_id=account_id)
    return timeline.to_dict()


@router.get("/replay/{customer_id}")
async def replay_customer_roi(
    customer_id: str,
    period_days: int = Query(default=30, ge=1, le=365),
) -> dict[str, Any]:
    """Compute ROI projection for the customer over the period."""
    period_start = _now() - timedelta(days=period_days)
    proj = replay_for_customer(customer_id=customer_id, period_start=period_start)
    return {
        "customer_id": proj.customer_id,
        "period_days": period_days,
        "n_leads": proj.n_leads,
        "n_meetings": proj.n_meetings,
        "n_proposals": proj.n_proposals,
        "n_deals_won": proj.n_deals_won,
        "revenue_won_sar": proj.revenue_won_sar,
        "pipeline_added_sar": proj.pipeline_added_sar,
    }


@router.get("/retention-summary")
async def get_retention_summary(customer_id: str = Query(...)) -> dict[str, Any]:
    """How many events per retention tier — for Trust Center display."""
    events = list(get_default_store().read_for_customer(customer_id))
    return retention_summary(events)


# ─────────────────────────────────────────────────────────────────
# 2. AGENT ORCHESTRATOR ENDPOINTS
# ─────────────────────────────────────────────────────────────────
@router.post("/workflows/run")
async def run_workflow(
    workflow_id: str = Body(default="daily_growth_run", embed=True),
    customer_id: str = Body(..., embed=True),
    autonomy_mode: str = Body(default=AutonomyMode.DRAFT_APPROVE, embed=True),
) -> dict[str, Any]:
    """Trigger a workflow — Daily Growth Run by default."""
    if workflow_id != "daily_growth_run":
        raise HTTPException(status_code=404, detail=f"unknown workflow: {workflow_id}")

    store = get_default_store()

    def resolver(c):
        p = default_policy(c)
        p.autonomy_mode = autonomy_mode
        return p

    orch = Orchestrator(
        queue=_QUEUE,
        event_store=store,
        policy_resolver=resolver,
        executor_registry=default_executors(),
    )
    summary = orch.run_workflow(workflow=DAILY_GROWTH_RUN, customer_id=customer_id)
    return summary


@router.get("/tasks")
async def list_tasks(
    customer_id: str = Query(...),
    status: str | None = Query(default=None),
) -> dict[str, Any]:
    if status:
        tasks = [t for t in _QUEUE.for_customer(customer_id) if t.status == status]
    else:
        tasks = _QUEUE.for_customer(customer_id)
    return {
        "summary": _QUEUE.summary(customer_id),
        "tasks": [
            {
                "task_id": t.task_id,
                "agent_id": t.agent_id,
                "action_type": t.action_type,
                "status": t.status,
                "requires_approval": t.requires_approval,
                "approval_reason": t.approval_reason,
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ],
    }


@router.post("/tasks/{task_id}/approve")
async def approve_task(task_id: str, approved_by: str = Body(..., embed=True)) -> dict[str, Any]:
    orch = _get_orchestrator("any")
    try:
        task = orch.approve_and_execute(task_id=task_id, approved_by=approved_by)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"task_id": task.task_id, "status": task.status}


@router.post("/tasks/{task_id}/reject")
async def reject_task(
    task_id: str,
    rejected_by: str = Body(..., embed=True),
    reason: str = Body(default="", embed=True),
) -> dict[str, Any]:
    orch = _get_orchestrator("any")
    try:
        task = orch.reject_task(task_id=task_id, rejected_by=rejected_by, reason=reason)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"task_id": task.task_id, "status": task.status}


# ─────────────────────────────────────────────────────────────────
# 3. MARKET RADAR ENDPOINTS
# ─────────────────────────────────────────────────────────────────
@router.get("/market-radar/signal-types")
async def list_signal_types() -> dict[str, Any]:
    return {"count": len(SIGNAL_TYPES), "signal_types": list(SIGNAL_TYPES)}


@router.post("/market-radar/detect/hiring")
async def detect_hiring(
    company_id: str = Body(..., embed=True),
    job_postings: list[dict[str, Any]] = Body(default_factory=list, embed=True),
) -> dict[str, Any]:
    # Convert ISO strings to datetimes
    parsed = []
    for jp in job_postings:
        posted = jp.get("posted_at")
        if isinstance(posted, str):
            try:
                jp["posted_at"] = datetime.fromisoformat(posted.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                continue
        parsed.append(jp)
    sigs = detect_hiring_signal(company_id=company_id, job_postings=parsed)
    return {"signals": [_signal_to_dict(s) for s in sigs]}


@router.post("/market-radar/sectors/{sector}/pulse")
async def sector_pulse(
    sector: str,
    signals_this_week: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    signals_prior_week: list[dict[str, Any]] = Body(default_factory=list, embed=True),
) -> dict[str, Any]:
    this_w = [_signal_from_dict(s) for s in signals_this_week]
    prior_w = [_signal_from_dict(s) for s in signals_prior_week]
    pulse = build_sector_pulse(
        sector=sector, signals_this_week=this_w, signals_prior_week=prior_w
    )
    return pulse.to_dict()


@router.post("/market-radar/opportunities")
async def opportunities(
    signals: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    company_metadata: dict[str, dict[str, Any]] = Body(default_factory=dict, embed=True),
    sector_trends: dict[str, str] = Body(default_factory=dict, embed=True),
    top_n: int = Body(default=20, embed=True),
) -> dict[str, Any]:
    parsed_signals = [_signal_from_dict(s) for s in signals]

    def explainer(*, company_id, signals, sector, sector_pulse_trend):
        wn = [
            WhyNowSignal(
                signal_type=s.signal_type,
                detected_at=s.detected_at,
                source=s.source,
                evidence_url=s.evidence_url,
                payload=s.payload,
            )
            for s in signals
        ]
        return explain_why_now(
            company_id=company_id,
            signals=wn,
            sector=sector,
            sector_pulse_trend=sector_pulse_trend,
        )

    feed = build_opportunity_feed(
        signals=parsed_signals,
        company_metadata=company_metadata,
        why_now_explainer=explainer,
        sector_trends=sector_trends,
        top_n=top_n,
    )
    return {"count": len(feed), "opportunities": [o.to_dict() for o in feed]}


# ─────────────────────────────────────────────────────────────────
# 4. COPILOT ENDPOINTS
# ─────────────────────────────────────────────────────────────────
@router.post("/copilot/ask")
async def copilot_ask(
    question_ar: str = Body(..., embed=True),
    customer_id: str = Body(..., embed=True),
    context: dict[str, Any] = Body(default_factory=dict, embed=True),
) -> dict[str, Any]:
    return ask(question_ar=question_ar, customer_id=customer_id, context=context)


@router.get("/copilot/intents")
async def copilot_intents() -> dict[str, Any]:
    return {"intents": list_intents()}


@router.get("/copilot/actions")
async def copilot_actions() -> dict[str, Any]:
    return {"actions": [a.to_dict() for a in SAFE_ACTIONS]}


@router.get("/copilot/actions/{action_id}")
async def copilot_action_detail(action_id: str) -> dict[str, Any]:
    a = get_action(action_id)
    if a is None:
        raise HTTPException(status_code=404, detail=f"unknown action: {action_id}")
    return a.to_dict()


# ─────────────────────────────────────────────────────────────────
# 5. REVENUE SCIENCE ENDPOINTS
# ─────────────────────────────────────────────────────────────────
@router.post("/forecast")
async def forecast_endpoint(
    customer_id: str = Body(..., embed=True),
    open_deals: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    horizon_days: int = Body(default=30, embed=True),
) -> dict[str, Any]:
    f = compute_forecast(customer_id=customer_id, open_deals=open_deals, horizon_days=horizon_days)
    return {
        "customer_id": f.customer_id,
        "horizon_days": f.horizon_days,
        "period_label": f.period_label,
        "best": f.best.__dict__,
        "likely": f.likely.__dict__,
        "worst": f.worst.__dict__,
        "deals_breakdown": f.deals_breakdown,
        "risks_ar": f.risks_ar,
        "decisions_required_ar": f.decisions_required_ar,
    }


@router.post("/attribution")
async def attribution_endpoint(
    deals: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    model: str = Body(default="time_decay", embed=True),
) -> dict[str, Any]:
    if model == "first_touch":
        r = compute_first_touch(deals=deals)
    elif model == "last_touch":
        r = compute_last_touch(deals=deals)
    elif model == "linear":
        r = compute_linear(deals=deals)
    else:
        r = compute_time_decay(deals=deals)
    return {"model": r.model, "by_channel": r.by_channel, "total_revenue_sar": r.total_revenue_sar}


@router.post("/impact")
async def impact_endpoint(
    current_baseline_revenue_sar: float = Body(..., embed=True),
    response_time_reduction_hours: float = Body(default=0, embed=True),
    extra_followup_touches: int = Body(default=0, embed=True),
    shift_to_whatsapp_pct: float = Body(default=0, embed=True),
    drop_n_sectors: int = Body(default=0, embed=True),
) -> dict[str, Any]:
    out = simulate_impact(
        current_baseline_revenue_sar=current_baseline_revenue_sar,
        response_time_reduction_hours=response_time_reduction_hours,
        extra_followup_touches=extra_followup_touches,
        shift_to_whatsapp_pct=shift_to_whatsapp_pct,
        drop_n_sectors=drop_n_sectors,
    )
    return out.__dict__


@router.post("/churn")
async def churn_endpoint(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    p = predict_churn(
        customer_id=payload.get("customer_id", "unknown"),
        days_since_last_login=int(payload.get("days_since_last_login", 0)),
        monthly_engagement_drop_pct=float(payload.get("monthly_engagement_drop_pct", 0)),
        support_tickets_open=int(payload.get("support_tickets_open", 0)),
        billing_failures_last_90d=int(payload.get("billing_failures_last_90d", 0)),
        nps=payload.get("nps"),
        pipeline_added_drop_pct=float(payload.get("pipeline_added_drop_pct", 0)),
        months_as_customer=int(payload.get("months_as_customer", 6)),
    )
    return p.__dict__


@router.post("/expansion")
async def expansion_endpoint(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    s = predict_expansion(
        customer_id=payload.get("customer_id", "unknown"),
        current_plan=payload.get("current_plan", "Growth"),
        health_score=float(payload.get("health_score", 0)),
        monthly_engagement_growth_pct=float(payload.get("monthly_engagement_growth_pct", 0)),
        sectors_targeted=int(payload.get("sectors_targeted", 1)),
        pct_of_quota_used=float(payload.get("pct_of_quota_used", 0)),
        nps=payload.get("nps"),
        pipeline_added_growth_pct=float(payload.get("pipeline_added_growth_pct", 0)),
    )
    return s.__dict__


# ─────────────────────────────────────────────────────────────────
# 6. COMPLIANCE OS ENDPOINTS
# ─────────────────────────────────────────────────────────────────
@router.post("/compliance/contactability")
async def contactability_endpoint(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Check if a contact can be reached now. Records is a list of consent dicts."""
    contact_id = payload["contact_id"]
    records_dicts = payload.get("consent_records", [])
    # Convert to ConsentRecord (lightweight inline)
    from auto_client_acquisition.compliance_os.consent_ledger import ConsentRecord

    records = []
    for r in records_dicts:
        oa = r.get("occurred_at")
        if isinstance(oa, str):
            try:
                oa = datetime.fromisoformat(oa.replace("Z", "+00:00")).replace(tzinfo=None)
            except Exception:
                oa = _now()
        records.append(ConsentRecord(
            record_id=r.get("record_id", "x"),
            customer_id=r.get("customer_id", ""),
            contact_id=contact_id,
            record_type=r.get("record_type", "consent_granted"),
            lawful_basis=r.get("lawful_basis"),
            purpose=r.get("purpose", ""),
            channel=r.get("channel"),
            source=r.get("source", "api"),
            occurred_at=oa,
        ))
    s = check_contactability(
        contact_id=contact_id,
        consent_records=records,
        messages_sent_this_week=int(payload.get("messages_sent_this_week", 0)),
        weekly_cap=int(payload.get("weekly_cap", 2)),
        current_riyadh_hour=int(payload.get("current_riyadh_hour", 12)),
    )
    return s.to_dict()


@router.post("/compliance/campaign-risk")
async def campaign_risk_endpoint(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    r = score_campaign_risk(
        target_count=int(payload.get("target_count", 0)),
        contacts_with_consent=int(payload.get("contacts_with_consent", 0)),
        contacts_opted_out=int(payload.get("contacts_opted_out", 0)),
        contacts_no_lawful_basis=int(payload.get("contacts_no_lawful_basis", 0)),
        template_body=payload.get("template_body", ""),
        template_subject=payload.get("template_subject", ""),
        channel=payload.get("channel", "email"),
        has_unsubscribe_link=bool(payload.get("has_unsubscribe_link", True)),
        in_quiet_hours=bool(payload.get("in_quiet_hours", False)),
    )
    return {
        "risk_score": r.risk_score,
        "risk_band": r.risk_band,
        "issues": r.issues,
        "blockers": r.blockers,
        "contacts_safe": r.contacts_safe,
        "contacts_blocked": r.contacts_blocked,
        "contacts_needing_review": r.contacts_needing_review,
        "recommended_fixes_ar": r.recommended_fixes_ar,
    }


@router.get("/compliance/ropa")
async def get_ropa(
    customer_id: str = Query(...),
    customer_name: str = Query(default="Customer"),
    dpo_email: str | None = Query(default=None),
) -> dict[str, Any]:
    r = build_ropa(customer_id=customer_id, customer_name=customer_name, dpo_email=dpo_email)
    return r.to_json()


@router.post("/compliance/dsr")
async def open_dsr_endpoint(
    customer_id: str = Body(..., embed=True),
    data_subject_id: str = Body(..., embed=True),
    request_type: str = Body(..., embed=True),
) -> dict[str, Any]:
    if request_type not in DSR_TYPES:
        raise HTTPException(status_code=400, detail=f"unknown DSR type: {request_type}")
    r = open_dsr(customer_id=customer_id, data_subject_id=data_subject_id, request_type=request_type)
    return {
        "request_id": r.request_id,
        "request_type": r.request_type,
        "status": r.status,
        "received_at": r.received_at.isoformat(),
        "sla_due_at": r.sla_due_at.isoformat(),
    }


@router.get("/compliance/vendors")
async def list_vendors() -> dict[str, Any]:
    return {
        "summary": vendors_summary(),
        "vendors": [
            {
                "vendor_id": v.vendor_id, "name": v.name, "purpose_ar": v.purpose_ar,
                "data_accessed": v.data_accessed, "region": v.region,
                "has_dpa_signed": v.has_dpa_signed, "iso27001": v.iso27001,
                "soc2": v.soc2, "risk_tier": v.risk_tier, "status": v.status,
            }
            for v in DEFAULT_VENDORS
        ],
    }


# ─────────────────────────────────────────────────────────────────
# 7. VERTICAL OS ENDPOINTS
# ─────────────────────────────────────────────────────────────────
@router.get("/verticals")
async def list_verticals() -> dict[str, Any]:
    return {"summaries": list_vertical_summaries()}


@router.get("/verticals/{vertical_id}")
async def get_vertical_detail(vertical_id: str) -> dict[str, Any]:
    v = get_vertical(vertical_id)
    if v is None:
        raise HTTPException(status_code=404, detail=f"unknown vertical: {vertical_id}")
    return {
        "vertical_id": v.vertical_id,
        "sector_ar": v.sector_ar,
        "sector_en": v.sector_en,
        "icp_company_size": list(v.icp_company_size),
        "icp_cities": list(v.icp_cities),
        "icp_keywords": list(v.icp_keywords),
        "pain_points_ar": list(v.pain_points_ar),
        "top_objection_ids": list(v.top_objection_ids),
        "priority_signals": list(v.priority_signals),
        "dashboard_kpis": [
            {"metric_id": k.metric_id, "name_ar": k.name_ar, "description_ar": k.description_ar,
             "unit": k.unit, "higher_is_better": k.higher_is_better,
             "target_p50": k.target_p50, "target_p90": k.target_p90}
            for k in v.dashboard_kpis
        ],
        "n_message_templates": len(v.message_templates),
        "avg_deal_value_sar": v.avg_deal_value_sar,
        "avg_cycle_days": v.avg_cycle_days,
        "benchmark_reply_rate": v.benchmark_reply_rate,
        "benchmark_meeting_rate": v.benchmark_meeting_rate,
        "benchmark_win_rate": v.benchmark_win_rate,
        "compliance_notes_ar": list(v.compliance_notes_ar),
        "recommended_channel_mix": v.recommended_channel_mix,
    }


@router.get("/verticals/{vertical_id}/templates")
async def get_vertical_templates(vertical_id: str) -> dict[str, Any]:
    v = get_vertical(vertical_id)
    if v is None:
        raise HTTPException(status_code=404, detail=f"unknown vertical: {vertical_id}")
    return {
        "vertical_id": vertical_id,
        "templates": [
            {
                "template_id": t.template_id,
                "channel": t.channel,
                "purpose": t.purpose,
                "subject_ar": t.subject_ar,
                "body_ar": t.body_ar,
                "variables": list(t.variables),
                "expected_reply_rate": t.expected_reply_rate,
            }
            for t in v.message_templates
        ],
        "proposal_template_ar": v.proposal_template_ar,
        "qbr_section_template_ar": v.qbr_section_template_ar,
    }


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────
def _signal_to_dict(s: SignalDetection) -> dict[str, Any]:
    return {
        "company_id": s.company_id,
        "signal_type": s.signal_type,
        "detected_at": s.detected_at.isoformat(),
        "source": s.source,
        "confidence": s.confidence,
        "evidence_url": s.evidence_url,
        "payload": s.payload,
    }


def _signal_from_dict(d: dict[str, Any]) -> SignalDetection:
    detected = d.get("detected_at")
    if isinstance(detected, str):
        try:
            detected = datetime.fromisoformat(detected.replace("Z", "+00:00")).replace(tzinfo=None)
        except Exception:
            detected = _now()
    return SignalDetection(
        company_id=d["company_id"],
        signal_type=d["signal_type"],
        detected_at=detected or _now(),
        source=d.get("source", "api"),
        confidence=float(d.get("confidence", 0.5)),
        evidence_url=d.get("evidence_url"),
        payload=d.get("payload", {}),
    )

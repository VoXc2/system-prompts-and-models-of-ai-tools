"""
Minimal Dealix v3 FastAPI app — Python 3.10 compatible.

Demonstrates the v3 Autonomous Revenue Platform end-to-end without
pulling in the legacy `core/` package (which uses Python 3.11+ features).

Run:
    uvicorn v3_app:app --reload --port 8000

Then visit:
    http://localhost:8000/docs       — OpenAPI explorer
    http://localhost:8000/health     — health check
    http://localhost:8000/v3-status  — full v3 inventory
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# v3 modules (pure-Python, no Python 3.11+ dependencies)
from auto_client_acquisition.compliance_os.consent_ledger import (
    LawfulBasis, record_consent, record_opt_out, latest_state,
)
from auto_client_acquisition.compliance_os.contactability import check_contactability
from auto_client_acquisition.compliance_os.risk_engine import score_campaign_risk
from auto_client_acquisition.compliance_os.ropa import build_ropa
from auto_client_acquisition.compliance_os.vendor_registry import vendors_summary
from auto_client_acquisition.copilot import ask, classify_intent, list_intents
from auto_client_acquisition.market_intelligence.signal_detectors import (
    SIGNAL_TYPES, detect_hiring_signal, detect_funding_signal,
)
from auto_client_acquisition.market_intelligence.sector_pulse import build_sector_pulse
from auto_client_acquisition.orchestrator.policies import AutonomyMode, default_policy
from auto_client_acquisition.orchestrator.queue import TaskQueue
from auto_client_acquisition.orchestrator.runtime import (
    DAILY_GROWTH_RUN, Orchestrator,
)
from auto_client_acquisition.orchestrator.tools import default_executors
from auto_client_acquisition.revenue_memory.event_store import (
    InMemoryEventStore, get_default_store,
)
from auto_client_acquisition.revenue_memory.events import EVENT_TYPES, make_event
from auto_client_acquisition.revenue_memory.replay import replay_for_account
from auto_client_acquisition.revenue_science.churn_model import predict_churn
from auto_client_acquisition.revenue_science.expansion_model import predict_expansion
from auto_client_acquisition.revenue_science.forecast import compute_forecast
from auto_client_acquisition.revenue_science.causal_impact import simulate_impact
from auto_client_acquisition.vertical_os import (
    list_vertical_summaries, get_vertical,
)
import auto_client_acquisition.vertical_os.clinics  # noqa: F401  (registers)
import auto_client_acquisition.vertical_os.real_estate  # noqa: F401
import auto_client_acquisition.vertical_os.logistics  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Dealix v3 — Saudi Autonomous Revenue Platform — starting")
    yield
    print("Dealix v3 — shutting down")


app = FastAPI(
    title="Dealix v3 — Saudi Autonomous Revenue Platform",
    version="3.0.0",
    description=(
        "Event-sourced Revenue Memory + 11 AI Agent Orchestrator + "
        "Saudi Market Radar + Copilot + Revenue Science + PDPL Compliance OS + "
        "Vertical OS for 8 Saudi sectors."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# Shared in-memory infrastructure for the demo
_QUEUE = TaskQueue()


# ── Health & status ──────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "version": "3.0.0", "ts": datetime.now(timezone.utc).isoformat()}


@app.get("/v3-status")
def v3_status():
    return {
        "platform": "Dealix v3 — Saudi Autonomous Revenue Platform",
        "modules": {
            "revenue_memory": {"event_types": len(EVENT_TYPES)},
            "orchestrator": {
                "autonomy_modes": ["manual", "suggest_only", "draft_and_approve",
                                    "safe_autopilot", "full_autopilot"],
                "default_workflow": DAILY_GROWTH_RUN.name,
                "n_steps": len(DAILY_GROWTH_RUN.steps),
            },
            "market_radar": {"signal_types": len(SIGNAL_TYPES)},
            "copilot": {"intents": len(list_intents())},
            "compliance_os": {"vendors": vendors_summary()["total"]},
            "vertical_os": {"sectors": len(list_vertical_summaries())},
        },
        "uptime": "live",
    }


# ── Revenue Memory ───────────────────────────────────────────────
@app.get("/api/v1/revenue-os/events/types")
def list_events():
    return {"count": len(EVENT_TYPES), "event_types": list(EVENT_TYPES)}


@app.post("/api/v1/revenue-os/events")
def create_event(payload: dict[str, Any]):
    e = make_event(
        event_type=payload["event_type"],
        customer_id=payload["customer_id"],
        subject_type=payload["subject_type"],
        subject_id=payload["subject_id"],
        payload=payload.get("payload", {}),
    )
    get_default_store().append(e)
    return {"event_id": e.event_id, "occurred_at": e.occurred_at.isoformat()}


@app.get("/api/v1/revenue-os/timeline/{account_id}")
def timeline(account_id: str, customer_id: str):
    t = replay_for_account(customer_id=customer_id, account_id=account_id)
    return t.to_dict()


# ── Orchestrator ─────────────────────────────────────────────────
@app.post("/api/v1/revenue-os/workflows/run")
def run_workflow(payload: dict[str, Any]):
    customer_id = payload["customer_id"]
    autonomy = payload.get("autonomy_mode", AutonomyMode.DRAFT_APPROVE)

    def resolver(c):
        p = default_policy(c)
        p.autonomy_mode = autonomy
        return p

    orch = Orchestrator(
        queue=_QUEUE, event_store=get_default_store(),
        policy_resolver=resolver, executor_registry=default_executors(),
    )
    return orch.run_workflow(workflow=DAILY_GROWTH_RUN, customer_id=customer_id)


@app.get("/api/v1/revenue-os/tasks")
def list_tasks(customer_id: str):
    return {
        "summary": _QUEUE.summary(customer_id),
        "tasks": [
            {"task_id": t.task_id, "agent_id": t.agent_id, "action_type": t.action_type,
             "status": t.status, "requires_approval": t.requires_approval}
            for t in _QUEUE.for_customer(customer_id)
        ],
    }


# ── Copilot ──────────────────────────────────────────────────────
@app.post("/api/v1/revenue-os/copilot/ask")
def copilot_ask(payload: dict[str, Any]):
    return ask(
        question_ar=payload["question_ar"],
        customer_id=payload.get("customer_id", "demo"),
        context=payload.get("context", {}),
    )


@app.get("/api/v1/revenue-os/copilot/intents")
def copilot_intents():
    return {"intents": list_intents()}


# ── Revenue Science ──────────────────────────────────────────────
@app.post("/api/v1/revenue-os/forecast")
def forecast(payload: dict[str, Any]):
    f = compute_forecast(
        customer_id=payload["customer_id"],
        open_deals=payload.get("open_deals", []),
        horizon_days=int(payload.get("horizon_days", 30)),
    )
    return {
        "best": f.best.__dict__, "likely": f.likely.__dict__, "worst": f.worst.__dict__,
        "deals_breakdown": f.deals_breakdown, "risks_ar": f.risks_ar,
        "decisions_required_ar": f.decisions_required_ar,
    }


@app.post("/api/v1/revenue-os/impact")
def impact(payload: dict[str, Any]):
    out = simulate_impact(
        current_baseline_revenue_sar=float(payload["current_baseline_revenue_sar"]),
        response_time_reduction_hours=float(payload.get("response_time_reduction_hours", 0)),
        extra_followup_touches=int(payload.get("extra_followup_touches", 0)),
        shift_to_whatsapp_pct=float(payload.get("shift_to_whatsapp_pct", 0)),
        drop_n_sectors=int(payload.get("drop_n_sectors", 0)),
    )
    return out.__dict__


@app.post("/api/v1/revenue-os/churn")
def churn(payload: dict[str, Any]):
    p = predict_churn(
        customer_id=payload["customer_id"],
        days_since_last_login=int(payload.get("days_since_last_login", 0)),
        nps=payload.get("nps"),
    )
    return p.__dict__


# ── Compliance OS ────────────────────────────────────────────────
@app.post("/api/v1/revenue-os/compliance/campaign-risk")
def campaign_risk(payload: dict[str, Any]):
    r = score_campaign_risk(
        target_count=int(payload.get("target_count", 0)),
        contacts_with_consent=int(payload.get("contacts_with_consent", 0)),
        contacts_opted_out=int(payload.get("contacts_opted_out", 0)),
        contacts_no_lawful_basis=int(payload.get("contacts_no_lawful_basis", 0)),
        template_body=payload.get("template_body", ""),
        channel=payload.get("channel", "email"),
        has_unsubscribe_link=bool(payload.get("has_unsubscribe_link", True)),
    )
    return {
        "risk_score": r.risk_score, "risk_band": r.risk_band,
        "issues": r.issues, "blockers": r.blockers,
        "contacts_safe": r.contacts_safe, "contacts_blocked": r.contacts_blocked,
        "recommended_fixes_ar": r.recommended_fixes_ar,
    }


@app.get("/api/v1/revenue-os/compliance/ropa")
def ropa(customer_id: str = "demo", customer_name: str = "Demo Customer"):
    return build_ropa(customer_id=customer_id, customer_name=customer_name).to_json()


@app.get("/api/v1/revenue-os/compliance/vendors")
def vendors():
    return vendors_summary()


# ── Market Radar ─────────────────────────────────────────────────
@app.get("/api/v1/revenue-os/market-radar/signal-types")
def signal_types():
    return {"count": len(SIGNAL_TYPES), "signal_types": list(SIGNAL_TYPES)}


# ── Vertical OS ──────────────────────────────────────────────────
@app.get("/api/v1/revenue-os/verticals")
def verticals():
    return {"summaries": list_vertical_summaries()}


@app.get("/api/v1/revenue-os/verticals/{vertical_id}")
def vertical(vertical_id: str):
    v = get_vertical(vertical_id)
    if v is None:
        return {"error": "unknown vertical"}, 404
    return {
        "vertical_id": v.vertical_id,
        "sector_ar": v.sector_ar,
        "pain_points_ar": list(v.pain_points_ar),
        "n_message_templates": len(v.message_templates),
        "avg_deal_value_sar": v.avg_deal_value_sar,
        "benchmark_reply_rate": v.benchmark_reply_rate,
    }


# ── Root ─────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name": "Dealix v3 — Saudi Autonomous Revenue Platform",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "/v3-status",
    }

"""Dealix v3 Autonomous Revenue OS endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.v3.agents import AgentName, AgentTask, SafeAgentRuntime, agent_catalog
from auto_client_acquisition.v3.compliance_os import ContactPolicyInput, assess_contactability, campaign_risk_report, ropa_stub
from auto_client_acquisition.v3.market_radar import demo_signals, rank_opportunities, sector_heatmap, signal_catalog
from auto_client_acquisition.v3.memory import EventType, RevenueEvent, demo_memory
from auto_client_acquisition.v3.revenue_science import FunnelInputs, churn_risk_score, demo_forecast, forecast_revenue, impact_simulation

router = APIRouter(prefix="/api/v1/v3", tags=["v3-autonomous-revenue-os"])
_runtime = SafeAgentRuntime()
_memory = demo_memory()


@router.get("/stack")
async def stack() -> dict[str, Any]:
    return {
        "name": "Dealix v3 Autonomous Saudi Revenue OS",
        "layers": [
            "Revenue Memory",
            "Safe Agent Runtime",
            "Saudi Market Radar",
            "PDPL Compliance OS",
            "Revenue Science",
            "Command Center Copilot",
            "Vertical OS",
            "Ecosystem Integrations",
        ],
        "recommended_tools": {
            "agent_workflows": ["LangGraph", "OpenAI Agents SDK", "Pydantic AI"],
            "rag": ["LlamaIndex", "Qdrant or pgvector"],
            "observability": ["Langfuse", "OpenTelemetry", "Sentry"],
            "automation": ["n8n", "MCP connectors"],
            "frontend": ["Next.js", "Tailwind", "shadcn/ui", "Recharts", "TanStack Query"],
        },
    }


@router.get("/agents")
async def agents() -> dict[str, Any]:
    return {"count": len(agent_catalog()), "items": agent_catalog()}


@router.post("/agents/tasks")
async def create_agent_task(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    task = AgentTask(
        agent=AgentName(body.get("agent", "prospecting")),
        objective=str(body.get("objective", "")) or "Find next best revenue action",
        customer_id=str(body.get("customer_id", "demo")),
        context=dict(body.get("context") or {}),
        requires_approval=bool(body.get("requires_approval", True)),
        risk_level=str(body.get("risk_level", "medium")),
    )
    return _runtime.create_task(task).to_dict()


@router.post("/agents/tasks/{task_id}/approve")
async def approve_task(task_id: str) -> dict[str, Any]:
    return _runtime.approve(task_id).to_dict()


@router.post("/agents/tasks/{task_id}/execute")
async def execute_task(task_id: str) -> dict[str, Any]:
    return _runtime.execute(task_id)


@router.get("/market-radar")
async def market_radar() -> dict[str, Any]:
    signals = demo_signals()
    return {
        "opportunities": rank_opportunities(signals),
        "sector_heatmap": sector_heatmap(signals),
    }


@router.get("/market-radar/signal-catalog")
async def market_radar_signal_catalog() -> dict[str, Any]:
    return {"count": len(signal_catalog()), "items": signal_catalog()}


@router.post("/compliance/contactability")
async def contactability(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    item = ContactPolicyInput(**body)
    return assess_contactability(item)


@router.post("/compliance/campaign-risk")
async def campaign_risk(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    contacts = [ContactPolicyInput(**item) for item in body.get("contacts", [])]
    return campaign_risk_report(contacts)


@router.get("/compliance/ropa")
async def ropa(process_name: str = "Outbound Revenue Operations", purpose: str = "B2B sales follow-up") -> dict[str, Any]:
    return ropa_stub(process_name, purpose)


@router.get("/memory/{aggregate_id}")
async def memory_projection(aggregate_id: str) -> dict[str, Any]:
    return {"projection": _memory.projection(aggregate_id), "timeline": _memory.timeline(aggregate_id)}


@router.post("/memory/events")
async def append_event(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    event = RevenueEvent(
        event_type=EventType(body.get("event_type", "signal.detected")),
        customer_id=str(body.get("customer_id", "demo")),
        aggregate_id=str(body.get("aggregate_id", "demo_account")),
        payload=dict(body.get("payload") or {}),
        actor=str(body.get("actor", "api")),
    )
    _memory.append(event)
    return event.to_dict()


@router.post("/revenue-science/forecast")
async def forecast(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return forecast_revenue(FunnelInputs(**body))


@router.post("/revenue-science/impact")
async def impact(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return impact_simulation(FunnelInputs(**body["base"]), FunnelInputs(**body["improved"]))


@router.get("/revenue-science/demo")
async def revenue_demo() -> dict[str, Any]:
    return demo_forecast()


@router.post("/revenue-science/churn-risk")
async def churn(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return churn_risk_score(
        usage_days_30=int(body.get("usage_days_30", 0)),
        outcomes_seen=int(body.get("outcomes_seen", 0)),
        support_sentiment=float(body.get("support_sentiment", 0.5)),
    )


@router.get("/command-center/snapshot")
async def command_center_snapshot() -> dict[str, Any]:
    signals = demo_signals()
    return {
        "today_decisions": [
            "Approve 12 safe WhatsApp follow-ups from warm inbound replies.",
            "Pause cold WhatsApp campaign: compliance risk blocked.",
            "Focus this week on clinics in Riyadh and real estate in Jeddah.",
        ],
        "agents": agent_catalog(),
        "market_radar": rank_opportunities(signals, limit=3),
        "forecast": demo_forecast(),
        "compliance": assess_contactability(ContactPolicyInput(channel="email", has_prior_relationship=True)),
        "memory": _memory.projection("clinic_riyadh_01"),
    }

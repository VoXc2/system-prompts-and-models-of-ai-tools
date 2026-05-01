"""
Default executors — testable stubs that emit deterministic results.

In production these are replaced by real LLM calls / WhatsApp providers.
The orchestrator doesn't care: any callable matching ExecutorFunc works.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from auto_client_acquisition.orchestrator.queue import AgentTask


def _stub_discover(task: AgentTask) -> dict[str, Any]:
    """Returns a deterministic list of synthetic leads for testing/demo."""
    return {
        "leads_discovered": 200,
        "lead_ids": [f"lead_{task.task_id[-6:]}_{i}" for i in range(200)],
    }


def _stub_signal(task: AgentTask) -> dict[str, Any]:
    return {
        "filtered_leads": 40,
        "lead_ids": [f"lead_{task.task_id[-6:]}_{i}" for i in range(40)],
    }


def _stub_enrich(task: AgentTask) -> dict[str, Any]:
    return {"enriched_count": 40, "fields_resolved": 6}


def _stub_compliance(task: AgentTask) -> dict[str, Any]:
    return {"approved_for_send": 38, "blocked": 2, "reasons": ["opt_out", "no_consent"]}


def _stub_personalize(task: AgentTask) -> dict[str, Any]:
    return {"drafts_created": 38, "tone": "warm", "language": "ar"}


def _stub_send(task: AgentTask) -> dict[str, Any]:
    return {"sent": 38, "channels": {"whatsapp": 25, "email": 10, "linkedin": 3}}


def _stub_classify(task: AgentTask) -> dict[str, Any]:
    return {"replies_classified": 6, "positive": 3, "negative": 1, "needs_more_info": 2}


def _stub_brief(task: AgentTask) -> dict[str, Any]:
    return {
        "brief_generated": True,
        "headline": "اليوم: 38 رسالة، 6 ردود، 3 إيجابية، 1 اجتماع محجوز",
        "decisions_required": 1,
    }


def default_executors() -> dict[str, Any]:
    """Return a mapping suitable to feed Orchestrator(executor_registry=...).

    Each action_type maps to a stub. Replace any of them with real LLM /
    provider calls by overriding the dict before constructing the runtime.
    """
    return {
        "discover_leads": _stub_discover,
        "enrich_lead": _stub_enrich,
        "draft_message": _stub_personalize,
        "send_message": _stub_send,
        "classify_reply": _stub_classify,
        "book_meeting": lambda t: {"booked": True, "calendly_url": "https://cal.dealix.sa/demo"},
        "generate_proposal": lambda t: {"proposal_pdf": "stub.pdf"},
        "score_deal": lambda t: {"score": 0.78},
        "compute_health": lambda t: {"overall": 78, "bucket": "stable"},
        "generate_qbr": _stub_brief,
        "publish_pulse": lambda t: {"pulse_url": "/pulse.html"},
    }

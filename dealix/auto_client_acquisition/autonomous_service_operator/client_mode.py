"""Client Mode — dashboard for the customer (Growth Manager) view."""

from __future__ import annotations

from typing import Any


def build_client_dashboard(
    *,
    customer_id: str = "",
    company_name: str = "",
    active_services: list[str] | None = None,
    open_actions: int = 0,
    proof_pack_due: bool = False,
) -> dict[str, Any]:
    """Build the client-facing dashboard."""
    active_services = active_services or []
    return {
        "mode": "client",
        "customer_id": customer_id,
        "company_name": company_name,
        "active_services": list(active_services),
        "open_actions": open_actions,
        "proof_pack_due": proof_pack_due,
        "today_panels_ar": [
            "Command Feed — قرارات اليوم",
            "Approvals Center — رسائل تنتظر اعتمادك",
            "Pipeline Tracker — مرحلة كل عميل",
            "Proof Pack — آخر تقرير + الـ ROI",
        ],
        "buttons_ar": ["اعرض القرارات", "اعتمد جماعي", "افتح Proof Pack"],
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_client_session_summary(
    *,
    session_id: str,
    customer_id: str = "",
    last_intent: str = "",
    last_recommended_service: str = "",
) -> dict[str, Any]:
    """Build a session summary for the client view."""
    return {
        "mode": "client",
        "session_id": session_id,
        "customer_id": customer_id,
        "last_intent": last_intent,
        "last_recommended_service": last_recommended_service,
        "next_step_ar": (
            "أكمل الـ intake للحصول على workflow الخدمة + أول Proof Pack."
        ),
        "approval_required": True,
    }

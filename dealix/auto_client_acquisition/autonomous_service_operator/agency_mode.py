"""Agency Mode — manage multiple clients + co-branded Proof Pack + revenue share."""

from __future__ import annotations

from typing import Any


def add_agency_client(
    *,
    agency_id: str,
    client_company_name: str,
    sector: str = "",
    monthly_subscription_sar: int = 0,
    revenue_share_pct: int = 20,
    clients: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Add a new client to an agency's roster + return the entry."""
    entry: dict[str, Any] = {
        "agency_id": agency_id,
        "client_company_name": client_company_name,
        "sector": sector,
        "monthly_subscription_sar": int(monthly_subscription_sar),
        "revenue_share_pct": int(revenue_share_pct),
        "status": "onboarding",
        "co_branded_proof_pack": True,
        "approval_required": True,
    }
    if clients is not None:
        clients.append(entry)
    return entry


def build_agency_dashboard(
    *,
    agency_id: str,
    agency_name: str = "",
    clients: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the agency's dashboard summary."""
    clients = clients or []
    total_clients = len(clients)
    active = sum(1 for c in clients if c.get("status") in ("active", "onboarding"))
    monthly_revenue_total = sum(
        float(c.get("monthly_subscription_sar", 0) or 0) for c in clients
    )
    avg_share_pct = (
        round(
            sum(int(c.get("revenue_share_pct", 0) or 0) for c in clients)
            / max(1, total_clients),
            1,
        )
        if total_clients else 0.0
    )

    return {
        "mode": "agency",
        "agency_id": agency_id,
        "agency_name": agency_name,
        "metrics": {
            "total_clients": total_clients,
            "active_clients": active,
            "monthly_revenue_sar": round(monthly_revenue_total, 2),
            "avg_revenue_share_pct": avg_share_pct,
        },
        "summary_ar": [
            f"عملاء الوكالة: {total_clients} (نشط: {active}).",
            f"الإيراد الشهري الكلي: {monthly_revenue_total:.0f} ريال.",
            f"متوسط revenue share: {avg_share_pct}%.",
        ],
        "panels_ar": [
            "Add Client — إضافة عميل جديد",
            "Run Diagnostic — تشخيص لعميل",
            "Co-Branded Proof Pack — Proof بعلامة الوكالة",
            "Referral Tracking — متابعة الإحالات",
            "Partner Scorecard — تقييم الأداء",
        ],
        "approval_required": True,
        "live_send_allowed": False,
    }


def list_agency_revenue_share(
    *, clients: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Compute revenue share owed to an agency for the current month."""
    clients = clients or []
    line_items: list[dict[str, Any]] = []
    total_share_sar = 0.0
    for c in clients:
        sub = float(c.get("monthly_subscription_sar", 0) or 0)
        pct = int(c.get("revenue_share_pct", 0) or 0)
        share = round(sub * pct / 100.0, 2)
        total_share_sar += share
        line_items.append({
            "client_company_name": c.get("client_company_name"),
            "monthly_subscription_sar": sub,
            "revenue_share_pct": pct,
            "agency_share_sar": share,
        })
    return {
        "line_items": line_items,
        "total_share_sar": round(total_share_sar, 2),
        "currency": "SAR",
    }


def build_co_branded_proof_pack(
    *,
    agency_name: str,
    client_company_name: str,
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a co-branded Proof Pack envelope for an agency client."""
    metrics = metrics or {}
    return {
        "title_ar": (
            f"Proof Pack — {client_company_name} (تنفيذ: {agency_name})"
        ),
        "co_branded": True,
        "agency_name": agency_name,
        "client_company_name": client_company_name,
        "sections_ar": [
            "ملخص تنفيذي للعميل",
            "ما عملته الوكالة + Dealix",
            "النتائج بالأرقام",
            "Action Ledger",
            "المخاطر التي منعتها الوكالة",
            "التوصية بالخطوة التالية",
        ],
        "metrics": dict(metrics),
        "approval_required": True,
        "live_send_allowed": False,
    }

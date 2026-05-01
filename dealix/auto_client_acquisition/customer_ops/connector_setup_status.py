"""Connector setup status — per-customer readiness across all integrations."""

from __future__ import annotations

from typing import Any

# 11 connectors Dealix supports during onboarding.
SUPPORTED_CONNECTORS: tuple[dict[str, Any], ...] = (
    {"key": "gmail", "label_ar": "Gmail", "default_mode": "draft_only",
     "blocking": False, "phase": "phase_1"},
    {"key": "google_calendar", "label_ar": "Google Calendar",
     "default_mode": "draft_only", "blocking": False, "phase": "phase_1"},
    {"key": "google_sheets", "label_ar": "Google Sheets",
     "default_mode": "approved_execute", "blocking": False, "phase": "phase_1"},
    {"key": "moyasar", "label_ar": "Moyasar (manual invoice)",
     "default_mode": "manual", "blocking": False, "phase": "phase_1"},
    {"key": "whatsapp_cloud", "label_ar": "WhatsApp Business",
     "default_mode": "draft_only", "blocking": True, "phase": "phase_1"},
    {"key": "website_forms", "label_ar": "Website Forms",
     "default_mode": "approved_execute", "blocking": False, "phase": "phase_1"},
    {"key": "linkedin_lead_forms", "label_ar": "LinkedIn Lead Gen Forms",
     "default_mode": "ingest_only", "blocking": False, "phase": "phase_2"},
    {"key": "google_business_profile", "label_ar": "Google Business Profile",
     "default_mode": "draft_only", "blocking": False, "phase": "phase_2"},
    {"key": "crm_generic", "label_ar": "CRM (HubSpot/Salesforce/Zoho/Close)",
     "default_mode": "draft_only", "blocking": False, "phase": "phase_2"},
    {"key": "google_meet", "label_ar": "Google Meet (transcripts)",
     "default_mode": "ingest_only", "blocking": False, "phase": "phase_2"},
    {"key": "instagram_graph", "label_ar": "Instagram (comments/DMs)",
     "default_mode": "ingest_only", "blocking": False, "phase": "phase_3"},
)


def get_connector_status(connector_key: str) -> dict[str, Any]:
    """Return the static description of a connector."""
    c = next((dict(c) for c in SUPPORTED_CONNECTORS if c["key"] == connector_key), None)
    if c is None:
        return {"error": f"unknown connector: {connector_key}"}
    return c


def update_connector_status(
    statuses: dict[str, dict[str, Any]],
    *,
    connector_key: str,
    state: str,
    notes: str = "",
) -> dict[str, dict[str, Any]]:
    """Update the live status of a connector for a customer."""
    if state not in {"not_started", "configuring", "connected_draft_only",
                     "connected_approved_execute", "failed", "skipped"}:
        raise ValueError(f"Unknown connector state: {state}")
    statuses[connector_key] = {
        "state": state,
        "notes": notes[:200],
    }
    return statuses


def build_connector_setup_summary(
    *,
    customer_id: str = "",
    statuses: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a connector setup summary for a customer."""
    statuses = statuses or {}
    connected = 0
    blocking_missing: list[str] = []
    by_state: dict[str, int] = {}

    items: list[dict[str, Any]] = []
    for c in SUPPORTED_CONNECTORS:
        live = statuses.get(c["key"], {})
        state = live.get("state", "not_started")
        by_state[state] = by_state.get(state, 0) + 1
        if state in ("connected_draft_only", "connected_approved_execute"):
            connected += 1
        if c["blocking"] and state not in (
            "connected_draft_only", "connected_approved_execute",
        ):
            blocking_missing.append(c["key"])
        items.append({**c, "state": state, "notes": live.get("notes", "")})

    total = len(SUPPORTED_CONNECTORS)
    pct = round(100 * connected / total, 1) if total else 0.0

    return {
        "customer_id": customer_id,
        "total_connectors": total,
        "connected_count": connected,
        "connected_pct": pct,
        "blocking_missing": blocking_missing,
        "by_state": by_state,
        "items": items,
        "ready_for_first_service": (
            len(blocking_missing) == 0 and connected >= 1
        ),
    }

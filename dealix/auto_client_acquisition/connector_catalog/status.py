"""Demo connector-status snapshot (deterministic; production reads env state)."""

from __future__ import annotations

from .catalog import ALL_CONNECTORS


def connector_status() -> dict[str, object]:
    """
    Return current status for each catalogued connector.

    During private beta everything is `not_connected` — connecting flips to
    `connected_draft_only` first, then `connected_live_with_approval` after a
    full safety review.
    """
    statuses: list[dict[str, object]] = []
    for c in ALL_CONNECTORS:
        if c.beta_status == "live":
            mode = "connected_draft_only"
        elif c.beta_status == "beta":
            mode = "connected_draft_only"
        else:
            mode = "not_connected"
        statuses.append({
            "key": c.key,
            "label_ar": c.label_ar,
            "beta_status": c.beta_status,
            "launch_phase": c.launch_phase,
            "mode": mode,
            "risk_level": c.risk_level,
        })
    return {"total": len(ALL_CONNECTORS), "statuses": statuses}

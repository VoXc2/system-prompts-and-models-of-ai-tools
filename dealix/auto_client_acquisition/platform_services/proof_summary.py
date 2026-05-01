"""Summarize innovation demo proof ledger — single source for demo numbers."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.innovation.proof_ledger import build_demo_proof_ledger


def build_proof_summary() -> dict[str, Any]:
    demo = build_demo_proof_ledger()
    events = demo.get("events") if isinstance(demo.get("events"), list) else []
    total_rev = 0.0
    types: dict[str, int] = {}
    for ev in events:
        if not isinstance(ev, dict):
            continue
        et = str(ev.get("event_type") or "unknown")
        types[et] = types.get(et, 0) + 1
        try:
            total_rev += float(ev.get("revenue_influenced_sar_estimate") or 0)
        except (TypeError, ValueError):
            pass
    return {
        "demo": True,
        "source": "innovation.proof_ledger.build_demo_proof_ledger",
        "event_count": len(events),
        "event_types": types,
        "revenue_influenced_sar_estimate_sum": total_rev,
    }

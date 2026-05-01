"""Proof Pack summary for a service — deterministic metrics."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def build_proof_pack(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id) or {}
    metrics = list(svc.get("proof_metrics") or ["drafts_created", "approvals_logged"])
    return {
        "service_id": service_id,
        "title_ar": f"Proof Pack — {svc.get('name_ar', service_id)}",
        "metrics": metrics,
        "sample_counts": {m: 0 for m in metrics},
        "notes_ar": "أرقام تجريبية حتى ربط عميل حقيقي ودفتر أحداث.",
        "demo": True,
    }

"""Deterministic action graph: signal → policy → approval → outcome → proof (demo)."""

from __future__ import annotations

from typing import Any


def build_action_graph_trace(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Returns nodes/edges for UI or docs — no execution.
    """
    p = payload or {}
    signal = str(p.get("signal_type") or "lead_received")
    nodes = [
        {"id": "n1", "kind": "signal", "label_ar": f"إشارة: {signal}"},
        {"id": "n2", "kind": "context", "label_ar": "بناء سياق (شركة، قناة، مصدر)"},
        {"id": "n3", "kind": "policy", "label_ar": "تقييم سياسة القناة"},
        {"id": "n4", "kind": "approval", "label_ar": "موافقة بشرية"},
        {"id": "n5", "kind": "draft_or_block", "label_ar": "مسودة أو منع"},
        {"id": "n6", "kind": "proof", "label_ar": "تسجيل في Proof Ledger"},
    ]
    edges = [
        {"from": "n1", "to": "n2", "label": "enrich"},
        {"from": "n2", "to": "n3", "label": "evaluate"},
        {"from": "n3", "to": "n4", "label": "if_external"},
        {"from": "n4", "to": "n5", "label": "on_approve"},
        {"from": "n5", "to": "n6", "label": "record"},
    ]
    return {
        "signal_type": signal,
        "nodes": nodes,
        "edges": edges,
        "note_ar": "عرض منطقي فقط — لا ينفّذ أدوات خارجية.",
        "demo": True,
    }

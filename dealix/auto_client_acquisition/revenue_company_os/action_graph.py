"""Signal → context → action graph (demo JSON for UI / intelligence)."""

from __future__ import annotations

from typing import Any


def demo_action_graph() -> dict[str, Any]:
    return {
        "nodes": [
            {"id": "signal", "label_ar": "إشارة"},
            {"id": "context", "label_ar": "سياق"},
            {"id": "service", "label_ar": "خدمة"},
            {"id": "risk", "label_ar": "مخاطرة"},
            {"id": "draft", "label_ar": "مسودة"},
            {"id": "approval", "label_ar": "موافقة"},
            {"id": "proof", "label_ar": "Proof"},
        ],
        "edges": [
            {"from": "signal", "to": "context"},
            {"from": "context", "to": "service"},
            {"from": "service", "to": "risk"},
            {"from": "risk", "to": "draft"},
            {"from": "draft", "to": "approval"},
            {"from": "approval", "to": "proof"},
        ],
        "demo": True,
    }

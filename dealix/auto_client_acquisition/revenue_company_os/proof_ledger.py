"""Proof ledger lines for Company OS (demo, in-process)."""

from __future__ import annotations

from typing import Any


def demo_proof_ledger() -> dict[str, Any]:
    return {
        "entries": [
            {"metric": "drafts_created", "delta": 3, "notes_ar": "بعد موافقة تجريبية"},
            {"metric": "risks_blocked", "delta": 1, "notes_ar": "منع إرسال جماعي مقترح"},
            {"metric": "approvals_logged", "delta": 2, "notes_ar": "سجل قرار داخلي"},
        ],
        "demo": True,
    }

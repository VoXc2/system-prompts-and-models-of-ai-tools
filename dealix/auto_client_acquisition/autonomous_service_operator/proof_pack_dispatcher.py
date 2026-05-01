"""Proof Pack dispatcher — generates + delivers Proof Packs per service."""

from __future__ import annotations

from typing import Any


def proof_pack_for_service(
    service_id: str, *, metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a Proof Pack template for any service."""
    metrics = metrics or {}
    return {
        "service_id": service_id,
        "title_ar": f"Proof Pack — {service_id}",
        "sections_ar": [
            "ملخص تنفيذي (5 أسطر)",
            "ما عمله Dealix",
            "النتائج (الأرقام)",
            "أبرز الردود/الاعتراضات",
            "المخاطر التي تم منعها",
            "Action Ledger مختصر",
            "التوصية بالخطوة التالية",
        ],
        "metrics_captured": dict(metrics),
        "metrics_required": [
            "opportunities_generated",
            "drafts_approved",
            "positive_replies",
            "meetings_drafted",
            "pipeline_influenced_sar",
            "risks_blocked",
            "time_saved_hours",
        ],
        "delivery_format": ["pdf", "json", "whatsapp_summary"],
        "approval_required": True,
        "live_send_allowed": False,
    }


def dispatch_proof_pack(
    *,
    service_id: str,
    customer_id: str | None = None,
    channel: str = "email",
    metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Dispatch a Proof Pack to a customer.

    Returns a draft envelope — never sends. The actual delivery requires
    customer/admin approval through the Approval Center.
    """
    template = proof_pack_for_service(service_id, metrics=metrics)
    return {
        "service_id": service_id,
        "customer_id": customer_id,
        "channel": channel,
        "envelope": {
            "subject_ar": template["title_ar"],
            "body_ar": (
                "مرفق Proof Pack الخاص بـ Pilot. "
                "يحتوي على ملخص تنفيذي + النتائج + المخاطر التي تم منعها + "
                "التوصية بالخطوة التالية."
            ),
            "attachments": ["proof_pack.pdf", "proof_pack.json"],
        },
        "template": template,
        "status": "draft",
        "approval_required": True,
        "live_send_allowed": False,
    }

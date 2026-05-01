"""Contract outlines — not legal advice; human + legal review required."""

from __future__ import annotations

from typing import Any


def _meta() -> dict[str, Any]:
    return {"legal_review_required": True, "approval_required": True, "not_legal_advice": True, "demo": True}


def draft_pilot_agreement_outline() -> dict[str, Any]:
    return {
        "title": "Pilot Agreement Outline",
        "sections": ["Scope", "Duration", "Fees", "Data processing", "Termination", "Liability cap"],
        **_meta(),
    }


def draft_dpa_outline() -> dict[str, Any]:
    return {"title": "DPA Outline", "sections": ["Roles", "Subprocessors", "Retention", "Security", "Subject rights"], **_meta()}


def draft_referral_agreement_outline() -> dict[str, Any]:
    return {"title": "Referral Agreement Outline", "sections": ["Commission", "Attribution", "Payment terms"], **_meta()}


def draft_agency_partner_outline() -> dict[str, Any]:
    return {"title": "Agency Partner Outline", "sections": ["White-label options", "Support", "Revenue share"], **_meta()}


def draft_scope_of_work() -> dict[str, Any]:
    return {"title": "SOW Outline", "sections": ["Deliverables", "Timeline", "Acceptance criteria"], **_meta()}


def list_contract_templates() -> dict[str, Any]:
    return {
        "templates": [
            draft_pilot_agreement_outline(),
            draft_dpa_outline(),
            draft_referral_agreement_outline(),
            draft_agency_partner_outline(),
            draft_scope_of_work(),
        ],
        "demo": True,
    }

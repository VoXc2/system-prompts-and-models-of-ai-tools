"""PDPL-first Compliance OS for Dealix v3."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Contactability(StrEnum):
    SAFE = "safe"
    NEEDS_REVIEW = "needs_review"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ContactPolicyInput:
    channel: str
    has_opt_in: bool = False
    has_prior_relationship: bool = False
    is_cold_whatsapp: bool = False
    has_unsubscribed: bool = False
    includes_unsubscribe: bool = True
    contains_sensitive_data: bool = False
    high_value_enterprise: bool = False


def assess_contactability(item: ContactPolicyInput) -> dict[str, Any]:
    reasons: list[str] = []
    status = Contactability.SAFE

    if item.has_unsubscribed:
        return {"status": Contactability.BLOCKED.value, "score": 0, "reasons": ["Contact previously opted out."]}
    if item.contains_sensitive_data:
        status = Contactability.BLOCKED
        reasons.append("Sensitive personal data detected; manual legal review required.")
    if item.is_cold_whatsapp or (item.channel.lower() == "whatsapp" and not item.has_opt_in and not item.has_prior_relationship):
        status = Contactability.BLOCKED
        reasons.append("Cold WhatsApp is blocked by Dealix safety policy.")
    if item.channel.lower() == "email" and not item.includes_unsubscribe:
        status = Contactability.NEEDS_REVIEW
        reasons.append("Outbound email needs unsubscribe footer and suppression handling.")
    if item.high_value_enterprise and status != Contactability.BLOCKED:
        status = Contactability.NEEDS_REVIEW
        reasons.append("High-value enterprise account requires human approval.")
    if not reasons:
        reasons.append("Low-risk contact path; proceed with audit logging.")

    score = {Contactability.SAFE: 90, Contactability.NEEDS_REVIEW: 55, Contactability.BLOCKED: 0}[status]
    return {"status": status.value, "score": score, "reasons": reasons}


def campaign_risk_report(contacts: list[ContactPolicyInput]) -> dict[str, Any]:
    results = [assess_contactability(contact) for contact in contacts]
    return {
        "total": len(results),
        "safe": sum(1 for result in results if result["status"] == Contactability.SAFE.value),
        "needs_review": sum(1 for result in results if result["status"] == Contactability.NEEDS_REVIEW.value),
        "blocked": sum(1 for result in results if result["status"] == Contactability.BLOCKED.value),
        "items": results,
    }


def ropa_stub(process_name: str, purpose: str, retention_days: int = 365) -> dict[str, Any]:
    return {
        "process_name": process_name,
        "purpose": purpose,
        "data_categories": ["business contact", "company profile", "conversation metadata"],
        "lawful_basis_note": "Record and review per PDPL operating policy before production outreach.",
        "retention_days": retention_days,
        "security_controls": ["audit_log", "role_based_access", "suppression_list", "data_minimization"],
    }

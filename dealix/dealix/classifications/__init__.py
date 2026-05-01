"""
Mandatory action classifications.

Every decision, event, and action in Dealix MUST carry all three:
    * ApprovalClass
    * ReversibilityClass
    * SensitivityClass

These drive policy evaluation, approval routing, and audit handling.
"""

from __future__ import annotations

from enum import Enum, StrEnum


class ApprovalClass(StrEnum):
    """Who must approve before this action executes.

    A0 — no approval (routine, reversible, non-sensitive)
    A1 — team / manager
    A2 — department head + legal/finance
    A3 — executive / board
    """

    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"

    @property
    def requires_approval(self) -> bool:
        return self != ApprovalClass.A0

    @property
    def minimum_approvers(self) -> int:
        return {
            ApprovalClass.A0: 0,
            ApprovalClass.A1: 1,
            ApprovalClass.A2: 2,
            ApprovalClass.A3: 2,
        }[self]


class ReversibilityClass(StrEnum):
    """How hard it is to undo this action.

    R0 — auto-reversible (draft email, internal note)
    R1 — reversible with limited ops (CRM field update)
    R2 — costly to reverse (a sent proposal, an outbound call)
    R3 — irreversible / external commitment (signed NDA, price sent to regulator)
    """

    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"

    @property
    def blocks_auto_execution(self) -> bool:
        """R3 can never auto-execute — must go through approval workflow."""
        return self == ReversibilityClass.R3


class SensitivityClass(StrEnum):
    """Data / impact sensitivity of this action.

    S0 — public
    S1 — internal
    S2 — confidential / commercial
    S3 — regulated / board / personal data
    """

    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"

    @property
    def is_pdpl_scope(self) -> bool:
        """S3 actions fall under PDPL scope (personal data)."""
        return self == SensitivityClass.S3


# ─────────────────────────────────────────────────────────────
# Pre-defined combinations for common action types
# ─────────────────────────────────────────────────────────────
ACTION_CLASSIFICATIONS: dict[str, tuple[ApprovalClass, ReversibilityClass, SensitivityClass]] = {
    # Phase 8 — acquisition
    "lead_intake": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S2),
    "icp_match": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S1),
    "pain_extract": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S1),
    "qualification_questions": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S1),
    "booking_schedule": (ApprovalClass.A1, ReversibilityClass.R1, SensitivityClass.S2),
    "crm_contact_upsert": (ApprovalClass.A0, ReversibilityClass.R1, SensitivityClass.S2),
    "crm_deal_create": (ApprovalClass.A1, ReversibilityClass.R1, SensitivityClass.S2),
    "proposal_generate_draft": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S2),
    "proposal_send": (ApprovalClass.A2, ReversibilityClass.R2, SensitivityClass.S2),
    "outreach_send": (ApprovalClass.A1, ReversibilityClass.R2, SensitivityClass.S2),
    "followup_send": (ApprovalClass.A1, ReversibilityClass.R2, SensitivityClass.S2),
    # Phase 9 — growth
    "sector_intel_query": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S1),
    "content_generate_draft": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S1),
    "content_publish": (ApprovalClass.A2, ReversibilityClass.R2, SensitivityClass.S1),
    "enrichment_query": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S2),
    "competitor_analyze": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S1),
    "market_research_query": (ApprovalClass.A0, ReversibilityClass.R0, SensitivityClass.S1),
    # High-risk / never-auto
    "pricing_offer_commit": (ApprovalClass.A3, ReversibilityClass.R3, SensitivityClass.S3),
    "contract_change": (ApprovalClass.A3, ReversibilityClass.R3, SensitivityClass.S3),
    "nda_send": (ApprovalClass.A3, ReversibilityClass.R3, SensitivityClass.S3),
    "payment_terms_change": (ApprovalClass.A3, ReversibilityClass.R3, SensitivityClass.S3),
    "regulator_communication": (ApprovalClass.A3, ReversibilityClass.R3, SensitivityClass.S3),
    "dataroom_access_grant": (ApprovalClass.A2, ReversibilityClass.R2, SensitivityClass.S3),
    "sensitive_data_export": (ApprovalClass.A3, ReversibilityClass.R3, SensitivityClass.S3),
}


def classify(action_type: str) -> tuple[ApprovalClass, ReversibilityClass, SensitivityClass]:
    """Return the canonical (A, R, S) classification for an action type.

    Falls back to the safest defaults (A2, R2, S2) for unknown actions
    so that unclassified work is conservatively gated rather than auto-executed.
    """
    return ACTION_CLASSIFICATIONS.get(
        action_type,
        (ApprovalClass.A2, ReversibilityClass.R2, SensitivityClass.S2),
    )


NEVER_AUTO_EXECUTE: frozenset[str] = frozenset(
    {
        "pricing_offer_commit",
        "contract_change",
        "nda_send",
        "payment_terms_change",
        "regulator_communication",
        "sensitive_data_export",
        "market_facing_statement",
    }
)

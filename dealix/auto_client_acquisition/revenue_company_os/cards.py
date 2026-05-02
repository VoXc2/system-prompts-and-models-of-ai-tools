"""Role-Based Revenue Command Cards — schema, validation, safety constants.

No live send, no scraping, no cold WhatsApp. Cards are decision units (max 3 buttons).
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, TypedDict

MAX_CARD_BUTTONS = 3
MAX_CARDS_VISIBLE = 7

RiskLevel = Literal["low", "medium", "high"]
ActionMode = Literal["approval_required", "draft_only", "suggest_only", "blocked"]


class UserRole(str, Enum):
    """Operational personas (one interface, role-scoped feeds)."""

    CEO = "ceo"
    SALES_MANAGER = "sales_manager"
    GROWTH_MANAGER = "growth_manager"
    AGENCY_PARTNER = "agency_partner"
    SUPPORT = "support"
    SERVICE_DELIVERY = "service_delivery"


class CardType(str, Enum):
    OPPORTUNITY = "opportunity"
    PARTNER = "partner"
    DEAL_FOLLOWUP = "deal_followup"
    NEGOTIATION = "negotiation"
    CLOSE = "close"
    PROOF = "proof"
    SUPPORT = "support"
    CEO_BRIEF = "ceo_brief"
    GROWTH_PLAN = "growth_plan"
    RISK = "risk"
    DELIVERY = "delivery"


class ForbiddenPattern(str, Enum):
    """Substrings that must not appear in actions or button machine keys."""

    LINKEDIN_SCRAPE = "linkedin_scrape"
    COLD_WHATSAPP = "cold_whatsapp"
    WHATSAPP_BLAST = "whatsapp_blast"
    LIVE_GMAIL_SEND = "live_gmail_send"
    MOYASAR_CHARGE = "moyasar_charge"


FORBIDDEN_SUBSTRINGS: tuple[str, ...] = tuple(p.value for p in ForbiddenPattern)


class CardButton(TypedDict, total=False):
    label_ar: str
    action: str


def _buttons_payload(buttons: list[CardButton]) -> list[CardButton]:
    if len(buttons) > MAX_CARD_BUTTONS:
        return buttons[:MAX_CARD_BUTTONS]
    return buttons


def assert_safe_card_copy(card: dict[str, Any]) -> None:
    """Raise ValueError if copy suggests blocked automation (tests + CI guard)."""
    blob = " ".join(
        str(x).lower()
        for x in (
            card.get("recommended_action_ar"),
            card.get("why_now_ar"),
            card.get("title_ar"),
            " ".join(b.get("action", "") + " " + b.get("label_ar", "") for b in card.get("buttons") or []),
        )
        if x
    )
    for bad in FORBIDDEN_SUBSTRINGS:
        if bad in blob:
            raise ValueError(f"unsafe card copy references forbidden pattern: {bad}")


def normalize_card(card: dict[str, Any]) -> dict[str, Any]:
    """Clamp buttons, ensure lists for proof_impact, run safety assert."""
    out = dict(card)
    buttons = list(out.get("buttons") or [])
    out["buttons"] = _buttons_payload(buttons)  # type: ignore[arg-type]
    pi = out.get("proof_impact")
    if pi is None:
        out["proof_impact"] = []
    elif isinstance(pi, str):
        out["proof_impact"] = [pi]
    elif isinstance(pi, list):
        out["proof_impact"] = [str(x) for x in pi]
    else:
        out["proof_impact"] = []
    assert_safe_card_copy(out)
    return out


def normalize_role_param(role: str | None) -> str:
    r = (role or "").strip().lower().replace("-", "_")
    aliases = {"agency": "agency_partner", "delivery": "service_delivery", "cs": "support"}
    return aliases.get(r, r)


def is_known_role(role: str) -> bool:
    return role in {e.value for e in UserRole}

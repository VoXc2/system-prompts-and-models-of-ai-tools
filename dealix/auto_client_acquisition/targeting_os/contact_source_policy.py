"""Contact source policy — كل contact له مصدر، غرض، ومستوى مخاطرة."""

from __future__ import annotations

# All recognized contact sources, ordered roughly safest → riskiest.
ALL_SOURCES: tuple[str, ...] = (
    "crm_customer",
    "inbound_lead",
    "website_form",
    "linkedin_lead_form",
    "event_lead",
    "referral",
    "partner_intro",
    "manual_research",
    "uploaded_list",
    "unknown_source",
    "cold_list",
    "opt_out",
)

# Risk score per source (0..100; higher = riskier).
_SOURCE_RISK: dict[str, int] = {
    "crm_customer": 5,
    "inbound_lead": 5,
    "website_form": 10,
    "linkedin_lead_form": 10,
    "event_lead": 20,
    "referral": 25,
    "partner_intro": 25,
    "manual_research": 50,
    "uploaded_list": 60,
    "unknown_source": 80,
    "cold_list": 95,
    "opt_out": 100,
}


def classify_source(source: str) -> dict[str, object]:
    """Classify a single source string. Unknown maps to `unknown_source`."""
    s = (source or "").lower().strip()
    if s not in ALL_SOURCES:
        s = "unknown_source"
    return {"source": s, "risk_score": _SOURCE_RISK[s]}


def allowed_channels_for_source(
    source: str, *, opt_in_status: str = "unknown",
) -> dict[str, object]:
    """
    Return which channels Dealix may attempt for this source/opt-in combo.

    Each channel is "safe" / "needs_review" / "blocked".
    """
    s = classify_source(source)["source"]
    opt = (opt_in_status or "unknown").lower()

    if s == "opt_out":
        return {
            "source": s,
            "channels": {ch: "blocked" for ch in
                         ("whatsapp", "email", "linkedin", "phone", "social_dm")},
            "notes_ar": "العميل سحب موافقته — كل القنوات محظورة.",
        }

    safe_inbound = s in ("crm_customer", "inbound_lead", "website_form",
                        "linkedin_lead_form", "referral", "partner_intro")
    is_unknown = s in ("unknown_source", "manual_research", "uploaded_list",
                       "cold_list")

    out: dict[str, str] = {}
    # WhatsApp — strict
    if opt == "yes" and not s == "cold_list":
        out["whatsapp"] = "safe"
    elif s == "inbound_lead" or s == "crm_customer":
        out["whatsapp"] = "needs_review"
    else:
        out["whatsapp"] = "blocked"

    # Email — looser when business context exists
    if safe_inbound:
        out["email"] = "safe"
    elif is_unknown:
        out["email"] = "needs_review"
    else:
        out["email"] = "needs_review"

    # LinkedIn — only via lead forms / manual approved
    if s == "linkedin_lead_form":
        out["linkedin"] = "safe"
    else:
        out["linkedin"] = "needs_review"

    # Phone — heavy review
    out["phone"] = "blocked" if s in ("cold_list", "unknown_source") else "needs_review"

    # Social DM — only with explicit context
    out["social_dm"] = "blocked" if s in ("cold_list", "unknown_source") else "needs_review"

    return {
        "source": s,
        "opt_in_status": opt,
        "channels": out,
        "notes_ar": (
            "البريد افضل قناة في الغالب لمصادر العمل المعروفة. "
            "واتساب يحتاج opt-in واضح. لينكدإن عبر Lead Forms فقط."
        ),
    }


def required_review_level(source: str) -> str:
    """Returns: 'auto_safe' | 'human_review' | 'block'."""
    s = classify_source(source)["source"]
    if s == "opt_out":
        return "block"
    if s in ("crm_customer", "inbound_lead", "website_form",
             "linkedin_lead_form"):
        return "auto_safe"
    if s in ("event_lead", "referral", "partner_intro"):
        return "human_review"
    return "human_review"


def retention_recommendation(source: str) -> dict[str, object]:
    """Return PDPL-shaped retention guidance per source."""
    s = classify_source(source)["source"]
    if s == "crm_customer":
        days = 365 * 3  # 3 years
    elif s in ("inbound_lead", "website_form", "linkedin_lead_form",
               "event_lead", "referral", "partner_intro"):
        days = 365 * 2
    else:
        days = 180
    return {
        "source": s,
        "retention_days": days,
        "lawful_basis_ar": (
            "علاقة قائمة" if s == "crm_customer"
            else "موافقة" if s in ("website_form", "linkedin_lead_form",
                                   "inbound_lead", "event_lead")
            else "مصلحة مشروعة محدودة"
        ),
        "notes_ar": "حذف تلقائي عند تجاوز المدة أو طلب opt-out.",
    }


def source_risk_score(source: str) -> int:
    """Return the integer risk score for the source."""
    return int(classify_source(source)["risk_score"])

"""Tool action planner — plan + review actions before they hit Tool Gateway."""

from __future__ import annotations

from typing import Any

# Tools that REQUIRE explicit human approval, no exceptions.
_HIGH_RISK_TOOLS: frozenset[str] = frozenset({
    "whatsapp.send_message",
    "gmail.send",
    "calendar.insert_event",
    "moyasar.charge",
    "google_business.publish_review_reply",
    "social.publish_dm",
    "social.publish_post",
})

# Tools that are safe in draft mode (still approval-required, never live-by-default).
_DRAFT_SAFE_TOOLS: frozenset[str] = frozenset({
    "whatsapp.draft_message",
    "gmail.create_draft",
    "calendar.draft_event",
    "moyasar.create_invoice_draft",
    "moyasar.create_payment_link_draft",
    "google_business.draft_review_reply",
    "social.draft_post",
})

# Tools never to plan, period.
_FORBIDDEN_TOOLS: frozenset[str] = frozenset({
    "linkedin.scrape_profile",
    "linkedin.auto_dm",
    "linkedin.auto_connect",
    "social.scrape_followers",
    "phone.cold_call_unscripted",
})


def plan_tool_action(
    *,
    tool: str,
    payload: dict[str, Any] | None = None,
    customer_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Plan a tool action — does NOT execute. Returns the plan + safety verdict.

    Verdicts:
        - "blocked"          (tool is forbidden or unsafe)
        - "draft_only"       (tool may run as draft, requires approval)
        - "approval_required"(tool requires human approval before execution)
        - "ready_for_gateway"(tool is safe internal — pass to Tool Gateway)
    """
    payload = payload or {}
    context = context or {}
    tool_lc = (tool or "").strip().lower()

    if tool_lc in _FORBIDDEN_TOOLS:
        return {
            "tool": tool, "verdict": "blocked",
            "reason_ar": "أداة محظورة (LinkedIn scraping/auto-DM/scraping social).",
            "live_send_allowed": False,
        }

    if tool_lc in _HIGH_RISK_TOOLS:
        return {
            "tool": tool, "verdict": "approval_required",
            "reason_ar": (
                "أداة عالية المخاطرة — تحتاج اعتماد بشري + env flag مفعّل."
            ),
            "live_send_allowed": False,
        }

    if tool_lc in _DRAFT_SAFE_TOOLS:
        return {
            "tool": tool, "verdict": "draft_only",
            "reason_ar": "draft فقط — أرسل للمراجعة قبل الاعتماد.",
            "live_send_allowed": False,
        }

    # Unknown tool — default to safest verdict.
    return {
        "tool": tool, "verdict": "approval_required",
        "reason_ar": "أداة غير مصنّفة — تحتاج مراجعة قبل التنفيذ.",
        "live_send_allowed": False,
    }


def review_planned_action(plan: dict[str, Any]) -> dict[str, Any]:
    """
    Quick safety review on an already-planned action. Returns updated plan.

    Strips any 'live_send_allowed=True' and forces it back to False.
    """
    out = dict(plan)
    out["live_send_allowed"] = False
    out["safety_reviewed"] = True
    if out.get("verdict") == "ready_for_gateway":
        # Even safe tools must be audited — promote to approval_required.
        out["verdict"] = "approval_required"
    return out

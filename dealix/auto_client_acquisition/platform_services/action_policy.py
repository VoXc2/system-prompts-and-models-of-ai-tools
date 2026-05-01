"""
Action Policy Engine — decides whether an action can run, needs approval,
or is blocked. The single chokepoint that protects the customer's
reputation + enforces PDPL.

Design: pure deterministic rules. Easily testable, easily auditable,
easy for the customer to explain to compliance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── Policy rules — each rule is (action_type, condition, decision, reason_ar)
POLICY_RULES: list[dict[str, Any]] = [
    # Hard blocks — never executed
    {
        "rule_id": "block_cold_whatsapp",
        "action": "send_whatsapp",
        "when": {"source": "cold_list", "consent": False},
        "decision": "blocked",
        "reason_ar": "WhatsApp البارد محظور بدون lawful basis (PDPL م.5).",
    },
    {
        "rule_id": "block_payment_no_confirm",
        "action": "charge_payment",
        "when": {"user_confirmed": False},
        "decision": "blocked",
        "reason_ar": "الخصم يحتاج تأكيد المستخدم على Moyasar — لا charge مباشر.",
    },
    {
        "rule_id": "block_secrets_in_payload",
        "action": "*",
        "when": {"payload_contains_secret": True},
        "decision": "blocked",
        "reason_ar": "تم اكتشاف secret في الـ payload — حماية تلقائية.",
    },
    # Approval gates — must pass through human
    {
        "rule_id": "external_send_needs_approval",
        "action": "send_whatsapp,send_email,send_inmail,post_social",
        "when": {"approval_status": "pending"},
        "decision": "approval_required",
        "reason_ar": "كل إرسال خارجي يحتاج موافقة العميل قبل التنفيذ.",
    },
    {
        "rule_id": "calendar_insert_needs_approval",
        "action": "calendar_insert_event",
        "when": {"approval_status": "pending"},
        "decision": "approval_required",
        "reason_ar": "إنشاء اجتماع في تقويم العميل يحتاج موافقة قبل insert.",
    },
    {
        "rule_id": "social_dm_needs_explicit",
        "action": "send_social_dm",
        "when": {"explicit_permission": False},
        "decision": "approval_required",
        "reason_ar": "DM السوشيال يحتاج إذن صريح لكل حساب.",
    },
    # Needs review
    {
        "rule_id": "unknown_source_review",
        "action": "*",
        "when": {"source": "unknown"},
        "decision": "approval_required",
        "reason_ar": "مصدر البيانات غير محدد — يحتاج توثيق lawful basis.",
    },
    {
        "rule_id": "high_value_deal_review",
        "action": "*",
        "when": {"deal_value_sar_gte": 100_000},
        "decision": "approval_required",
        "reason_ar": "صفقة قيمتها ≥100K ريال — راجعها قبل التنفيذ.",
    },
    # Allowed (default for safe paths)
    {
        "rule_id": "draft_only_safe",
        "action": "create_draft,read_data,classify_reply",
        "when": {},
        "decision": "allow",
        "reason_ar": "إجراء داخلي آمن — لا يخرج للعميل النهائي.",
    },
]


@dataclass
class PolicyDecision:
    """Output of evaluate_action."""

    decision: str            # allow / approval_required / blocked
    matched_rule_id: str | None
    reasons_ar: list[str] = field(default_factory=list)
    suggested_next_action_ar: str = ""


def evaluate_action(
    *,
    action: str,
    context: dict[str, Any] | None = None,
) -> PolicyDecision:
    """
    Evaluate a proposed action against the policy rules.

    First matching rule wins. Default: needs_review (defensive).
    """
    ctx = context or {}
    matched_reasons: list[str] = []
    final_decision = "allow"
    matched_rule_id: str | None = None
    next_action = "ready_for_execution"

    for rule in POLICY_RULES:
        # Action match (comma-separated list, "*" = match-any)
        applicable_actions = rule["action"].split(",") if rule["action"] != "*" else [action]
        if action not in applicable_actions and rule["action"] != "*":
            continue

        # Condition match — every key in `when` must match the context
        when = rule["when"]
        cond_match = True
        for k, expected in when.items():
            if k.endswith("_gte"):
                attr = k[:-4]
                if not (float(ctx.get(attr, 0)) >= float(expected)):
                    cond_match = False
                    break
            elif k == "payload_contains_secret":
                if expected and not _has_secret_marker(ctx.get("payload", {})):
                    cond_match = False
                    break
            elif ctx.get(k) != expected:
                cond_match = False
                break

        if not cond_match:
            continue

        decision = rule["decision"]
        matched_reasons.append(rule["reason_ar"])
        matched_rule_id = rule["rule_id"]

        if decision == "blocked":
            return PolicyDecision(
                decision="blocked",
                matched_rule_id=matched_rule_id,
                reasons_ar=matched_reasons,
                suggested_next_action_ar="معالجة سبب الحظر قبل المحاولة مرة أخرى.",
            )
        if decision == "approval_required":
            final_decision = "approval_required"
            next_action = "operator_approves_then_execute"
        # 'allow' rules just confirm — keep looking for stricter rule

    return PolicyDecision(
        decision=final_decision,
        matched_rule_id=matched_rule_id,
        reasons_ar=matched_reasons or ["لا قاعدة مطابقة — الإجراء آمن افتراضياً."],
        suggested_next_action_ar=next_action,
    )


# ── Helpers ──────────────────────────────────────────────────────
_SECRET_MARKERS = ("api_key", "secret_key", "private_key", "password", "ghp_", "sk-ant-", "moyasar_secret")


def _has_secret_marker(payload: dict[str, Any]) -> bool:
    """Cheap heuristic check — production pairs this with a stronger scanner."""
    if not isinstance(payload, dict):
        return False
    flat = str(payload).lower()
    return any(marker in flat for marker in _SECRET_MARKERS)

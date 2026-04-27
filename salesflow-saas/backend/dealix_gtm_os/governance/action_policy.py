"""Action policy — decides what requires approval vs auto-allowed."""
POLICY = {
    "email_send": "semi_auto",
    "linkedin_dm": "manual_required",
    "linkedin_connect": "manual_required",
    "whatsapp_warm": "manual_required",
    "whatsapp_cold": "prohibited",
    "instagram_dm": "manual_required",
    "x_post": "auto_allowed",
    "x_reply": "manual_required",
    "payment_link": "manual_required",
    "partner_terms": "manual_required",
    "claim_result": "manual_required",
    "use_customer_name": "manual_required",
}

def check_action(action: str) -> dict:
    level = POLICY.get(action, "manual_required")
    return {"action": action, "level": level, "requires_approval": level in ("manual_required",), "prohibited": level == "prohibited", "reason": f"Policy: {action} is {level}"}

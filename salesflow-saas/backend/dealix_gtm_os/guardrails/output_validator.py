"""Output validator — blocks fake claims, prohibited actions, and hallucinations."""
import re

FORBIDDEN_CLAIMS = [
    "مضمون", "guaranteed", "100%", "أفضل في السوق", "بدون منافس",
    "SOC 2", "ISO 27001", "bank-grade", "military-grade", "zero risk",
    "أمان مطلق", "نتائج مضمونة", "ربح مضمون", "دخل مضمون",
]

PROHIBITED_ACTIONS = [
    "linkedin_scraping", "linkedin_auto_dm", "whatsapp_cold_blast",
    "instagram_mass_dm", "x_auto_mention", "fake_account",
    "buy_lead_list", "tiktok_dm_scraping",
]

def validate_output(text: str, context: str = "") -> dict:
    """Validates LLM output for forbidden claims and unsafe content."""
    issues = []
    
    for claim in FORBIDDEN_CLAIMS:
        if claim.lower() in text.lower():
            issues.append({"type": "forbidden_claim", "claim": claim, "severity": "high"})
    
    for action in PROHIBITED_ACTIONS:
        if action.lower().replace("_", " ") in text.lower() or action in text.lower():
            issues.append({"type": "prohibited_action", "action": action, "severity": "critical"})
    
    if not re.search(r'إيقاف|stop|opt.?out|unsubscribe', text, re.IGNORECASE) and len(text) > 200:
        if any(w in context.lower() for w in ["outreach", "message", "email", "رسالة"]):
            issues.append({"type": "missing_optout", "severity": "medium"})
    
    return {
        "valid": len([i for i in issues if i["severity"] in ("high", "critical")]) == 0,
        "issues": issues,
        "issue_count": len(issues),
    }

def validate_channel_action(channel: str, action: str) -> dict:
    """Validates that a channel+action combination is safe."""
    prohibited = {
        ("linkedin", "scraping"), ("linkedin", "auto_dm"), ("linkedin", "auto_connect"),
        ("whatsapp", "cold_blast"), ("whatsapp", "mass_send"),
        ("instagram", "mass_dm"), ("instagram", "scraping"),
        ("x", "auto_mention"), ("x", "auto_reply_mass"),
        ("tiktok", "dm_scraping"), ("tiktok", "mass_dm"),
    }
    channel_key = channel.split("_")[0].lower()
    if (channel_key, action) in prohibited:
        return {"allowed": False, "reason": f"{action} on {channel} is PROHIBITED by platform policy"}
    return {"allowed": True, "reason": "Action is within safe boundaries"}

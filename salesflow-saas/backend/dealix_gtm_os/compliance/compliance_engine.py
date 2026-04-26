"""Compliance engine — decides what's allowed per channel."""
import yaml
from pathlib import Path
from dealix_gtm_os.models.message import AutomationLevel

RULES_PATH = Path(__file__).parent.parent / "config" / "compliance_rules.yaml"

_rules = {}
if RULES_PATH.exists():
    with open(RULES_PATH) as f:
        _rules = yaml.safe_load(f) or {}

def check_compliance(channel: str, action: str = "send_message") -> dict:
    channel_key = channel.split("_")[0]
    if channel_key == "x":
        channel_key = "x_twitter"
    rules = _rules.get(channel_key, {})
    if any(rules.get(k) == "prohibited" for k in [action, "scraping", "auto_dm", "auto_connect", "mass_dm", "cold_blast"]):
        if action in rules and rules[action] == "prohibited":
            return {"allowed": False, "level": AutomationLevel.PROHIBITED, "reason": f"{action} on {channel} is prohibited"}
    manual_channels = {"linkedin_manual", "whatsapp_warm", "phone", "partner_intro"}
    if channel in manual_channels:
        return {"allowed": True, "level": AutomationLevel.MANUAL_REQUIRED, "reason": f"{channel} requires Sami approval"}
    return {"allowed": True, "level": AutomationLevel.SEMI_AUTOMATED, "reason": f"{channel} is safe with opt-out"}

def get_daily_limit(channel: str) -> int:
    limits = {"email": 10, "linkedin_manual": 5, "whatsapp_warm": 5, "instagram_inbound": 3, "x_post": 3, "x_reply": 5, "phone": 3, "partner_intro": 2}
    return limits.get(channel, 5)

STOP_WORDS = ["إيقاف", "stop", "لا", "لا شكراً", "ما يناسبني"]

def should_stop(reply_text: str) -> bool:
    return any(w in reply_text for w in STOP_WORDS)

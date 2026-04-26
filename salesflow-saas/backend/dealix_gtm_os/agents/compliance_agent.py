import yaml
from pathlib import Path
from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.models.message import AutomationLevel

RULES_PATH = Path(__file__).parent.parent / "config" / "compliance_rules.yaml"

class ComplianceAgent(BaseAgent):
    name = "compliance"
    description = "Enforces platform safety rules"

    def __init__(self):
        if RULES_PATH.exists():
            with open(RULES_PATH) as f:
                self.rules = yaml.safe_load(f)
        else:
            self.rules = {}

    async def run(self, input_data: dict) -> dict:
        channel = input_data.get("channel", "email")
        action = input_data.get("action", "send_message")
        channel_key = channel.replace("_manual", "").replace("_warm", "").replace("_inbound", "").replace("_post", "").replace("_reply", "")
        if channel_key == "linkedin":
            channel_key = "linkedin"
        elif channel_key in ("x", "twitter"):
            channel_key = "x_twitter"
        rules = self.rules.get(channel_key, {})
        if rules.get(action) == "prohibited" or rules.get("scraping") == "prohibited" and action == "scraping":
            return {"allowed": False, "level": AutomationLevel.PROHIBITED.value, "reason": f"{action} on {channel} is prohibited by platform policy"}
        if channel in ("linkedin_manual", "whatsapp_warm", "phone"):
            return {"allowed": True, "level": AutomationLevel.MANUAL_REQUIRED.value, "reason": f"{channel} requires manual human approval"}
        return {"allowed": True, "level": AutomationLevel.SEMI_AUTOMATED.value, "reason": f"{channel} is safe with opt-out"}

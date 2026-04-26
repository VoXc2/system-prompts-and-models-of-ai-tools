from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.models.message import ChannelType, AutomationLevel

SECTOR_CHANNELS = {
    "agency": (ChannelType.EMAIL, ChannelType.LINKEDIN_MANUAL),
    "real_estate": (ChannelType.EMAIL, ChannelType.WHATSAPP_WARM),
    "clinic": (ChannelType.WHATSAPP_WARM, ChannelType.EMAIL),
    "saas": (ChannelType.EMAIL, ChannelType.LINKEDIN_MANUAL),
    "ecommerce": (ChannelType.EMAIL, ChannelType.INSTAGRAM_INBOUND),
    "construction": (ChannelType.EMAIL, ChannelType.PHONE),
    "training": (ChannelType.EMAIL, ChannelType.WHATSAPP_WARM),
    "consulting": (ChannelType.LINKEDIN_MANUAL, ChannelType.EMAIL),
    "website_agency": (ChannelType.LINKEDIN_MANUAL, ChannelType.EMAIL),
}

class ChannelStrategyAgent(BaseAgent):
    name = "channel_strategy"
    description = "Selects best outreach channel per target"

    async def run(self, input_data: dict) -> dict:
        sector = input_data.get("sector", "").lower().replace(" ", "_")
        channels = SECTOR_CHANNELS.get(sector, (ChannelType.EMAIL, ChannelType.LINKEDIN_MANUAL))
        primary, secondary = channels
        manual_channels = {ChannelType.LINKEDIN_MANUAL, ChannelType.WHATSAPP_WARM, ChannelType.PHONE}
        level = AutomationLevel.MANUAL_REQUIRED if primary in manual_channels else AutomationLevel.SEMI_AUTOMATED
        return {
            "primary_channel": primary.value,
            "secondary_channel": secondary.value,
            "automation_level": level.value,
            "reason": f"Sector {sector} best reached via {primary.value}",
            "risk_flags": ["manual_approval_required"] if level == AutomationLevel.MANUAL_REQUIRED else [],
        }

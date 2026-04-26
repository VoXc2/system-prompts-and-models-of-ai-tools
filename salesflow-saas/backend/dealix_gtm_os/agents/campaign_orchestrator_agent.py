"""Campaign Orchestrator Agent — builds multi-step outreach sequences."""
from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.models.message import AutomationLevel


class CampaignOrchestratorAgent(BaseAgent):
    name = "campaign_orchestrator"
    description = "Creates safe multi-step outreach sequences"

    async def run(self, input_data: dict) -> dict:
        company = input_data.get("name", "Unknown")
        primary_channel = input_data.get("primary_channel", "email")
        secondary_channel = input_data.get("secondary_channel", "linkedin_manual")

        manual_channels = {"linkedin_manual", "whatsapp_warm", "phone", "partner_intro"}

        sequence = [
            {
                "day": 0,
                "action": "send_first_message",
                "channel": primary_channel,
                "automation": AutomationLevel.MANUAL_REQUIRED.value if primary_channel in manual_channels else AutomationLevel.SEMI_AUTOMATED.value,
                "approval_required": True,
                "description": f"أول رسالة لـ {company} عبر {primary_channel}",
            },
            {
                "day": 2,
                "action": "follow_up_1",
                "channel": primary_channel,
                "automation": AutomationLevel.MANUAL_REQUIRED.value,
                "approval_required": True,
                "description": "متابعة سريعة — هل شفتوا رسالتي؟",
            },
            {
                "day": 5,
                "action": "follow_up_2_or_switch",
                "channel": secondary_channel,
                "automation": AutomationLevel.MANUAL_REQUIRED.value,
                "approval_required": True,
                "description": f"آخر متابعة أو تجربة {secondary_channel}",
            },
            {
                "day": 7,
                "action": "classify_and_decide",
                "channel": "internal",
                "automation": AutomationLevel.FULLY_AUTOMATED.value,
                "approval_required": False,
                "description": "صنّف الرد: مهتم/لاحقاً/لا → next action",
            },
        ]

        return {
            "company": company,
            "sequence": sequence,
            "total_steps": len(sequence),
            "total_days": 7,
            "stop_conditions": [
                "العميل رد 'إيقاف' أو 'لا' أو 'stop'",
                "مرت 7 أيام بدون أي رد بعد follow-up 2",
                "العميل طلب عدم التواصل",
            ],
            "max_touches": 3,
        }

"""
Dealix Auto-Outreach System - Autonomous outreach campaigns.
Sends personalized messages to discovered leads via WhatsApp, Email, SMS.
"""
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.config import get_settings
from app.services.ai_brain import ai_brain
from app.services.smart_sales import SmartSalesAgent
from app.integrations.whatsapp import send_whatsapp_message, send_whatsapp_template

settings = get_settings()


class AutoOutreachEngine:
    """Manages automated outreach campaigns."""

    def __init__(self, tenant_id: str, industry: str = "general"):
        self.tenant_id = tenant_id
        self.industry = industry
        self.sales_agent = SmartSalesAgent(tenant_id, industry)

    async def launch_campaign(
        self, leads: list, campaign_type: str = "cold_outreach",
        channel: str = "whatsapp", sequence_length: int = 5
    ) -> dict:
        """Launch an automated outreach campaign to a list of leads."""
        results = {
            "campaign_id": f"camp_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "total_leads": len(leads),
            "messages_sent": 0,
            "messages_failed": 0,
            "sequences_created": 0,
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        for lead in leads:
            try:
                if campaign_type == "cold_outreach":
                    result = await self._cold_outreach(lead, channel)
                elif campaign_type == "warm_followup":
                    result = await self._warm_followup(lead, channel)
                elif campaign_type == "reactivation":
                    result = await self._reactivation(lead, channel)
                else:
                    result = await self._cold_outreach(lead, channel)

                if result.get("success"):
                    results["messages_sent"] += 1
                else:
                    results["messages_failed"] += 1

                # Create follow-up sequence
                if sequence_length > 1:
                    sequence = await self.sales_agent.create_sales_sequence(
                        lead, num_messages=sequence_length
                    )
                    results["sequences_created"] += 1

            except Exception:
                results["messages_failed"] += 1

        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        return results

    async def _cold_outreach(self, lead: dict, channel: str) -> dict:
        """Send first-time outreach to a new lead."""
        # Generate personalized message
        message = await self.sales_agent.generate_outreach_message(
            lead, message_type="أول تواصل"
        )

        # Send via selected channel
        if channel == "whatsapp" and lead.get("phone"):
            # First try template (required for first message on WhatsApp)
            result = await send_whatsapp_template(
                phone=lead["phone"],
                template_name="dealix_welcome",
                language="ar",
                components=[{
                    "type": "body",
                    "parameters": [{"type": "text", "text": lead.get("name", "")}],
                }],
            )
            return {"success": result.get("status") == "success", "channel": "whatsapp", "result": result}

        return {"success": False, "reason": "no_phone"}

    async def _warm_followup(self, lead: dict, channel: str) -> dict:
        """Follow up with a lead who has shown interest."""
        message = await self.sales_agent.generate_followup_message(lead, days_since_last=3)

        if channel == "whatsapp" and lead.get("phone"):
            result = await send_whatsapp_message(lead["phone"], message)
            return {"success": result.get("status") == "success", "channel": "whatsapp", "result": result}

        return {"success": False, "reason": "no_phone"}

    async def _reactivation(self, lead: dict, channel: str) -> dict:
        """Re-engage a cold lead with a special offer."""
        message = await self.sales_agent.generate_outreach_message(
            lead, message_type="عرض خاص"
        )

        if channel == "whatsapp" and lead.get("phone"):
            result = await send_whatsapp_template(
                phone=lead["phone"],
                template_name="dealix_offer",
                language="ar",
                components=[{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": lead.get("name", "")},
                        {"type": "text", "text": "خصم 20% لمدة محدودة"},
                        {"type": "text", "text": "نهاية الشهر"},
                    ],
                }],
            )
            return {"success": result.get("status") == "success", "channel": "whatsapp", "result": result}

        return {"success": False, "reason": "no_phone"}

    async def smart_reply(self, incoming_message: str, lead_data: dict, history: list = None) -> dict:
        """Process incoming message and auto-reply intelligently."""
        result = await self.sales_agent.handle_incoming_message(
            message=incoming_message,
            lead_data=lead_data,
            conversation_history=history,
        )

        # Auto-send response if not escalated
        if not result["should_escalate"] and lead_data.get("phone"):
            send_result = await send_whatsapp_message(
                lead_data["phone"], result["response"]
            )
            result["sent"] = "error" not in str(send_result).lower()
            result["send_result"] = send_result
        elif result["should_escalate"]:
            result["sent"] = False
            result["escalation_note"] = "يحتاج تدخل بشري - " + (result.get("escalation_reason") or "عميل مهم")

        return result


class OutreachScheduler:
    """Schedules and manages outreach timing."""

    # Best times to send messages in Saudi Arabia
    BEST_HOURS_WEEKDAY = [9, 10, 11, 14, 15, 16, 20, 21]  # Work hours + evening
    BEST_HOURS_WEEKEND = [10, 11, 16, 17, 20, 21]  # Friday/Saturday relaxed hours

    @staticmethod
    def get_next_send_time(preferred_hour: int = None) -> datetime:
        """Get the optimal next send time in Saudi timezone."""
        now = datetime.now(timezone.utc) + timedelta(hours=3)  # UTC+3 Riyadh
        current_hour = now.hour
        current_weekday = now.weekday()

        # Friday (4) and Saturday (5) are weekend in Saudi
        is_weekend = current_weekday in (4, 5)
        best_hours = OutreachScheduler.BEST_HOURS_WEEKEND if is_weekend else OutreachScheduler.BEST_HOURS_WEEKDAY

        if preferred_hour and preferred_hour in best_hours:
            target_hour = preferred_hour
        else:
            # Find next best hour
            future_hours = [h for h in best_hours if h > current_hour]
            if future_hours:
                target_hour = future_hours[0]
            else:
                # Next day
                target_hour = best_hours[0]
                now += timedelta(days=1)

        return now.replace(hour=target_hour, minute=0, second=0, microsecond=0)

    @staticmethod
    def should_send_now() -> bool:
        """Check if now is a good time to send messages."""
        now = datetime.now(timezone.utc) + timedelta(hours=3)
        current_hour = now.hour
        is_weekend = now.weekday() in (4, 5)
        best_hours = OutreachScheduler.BEST_HOURS_WEEKEND if is_weekend else OutreachScheduler.BEST_HOURS_WEEKDAY
        return current_hour in best_hours

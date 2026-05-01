"""
Outreach Agent — generates personalized cold outreach messages.
وكيل الوصول — يُنشئ رسائل وصول باردة مخصصة.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from auto_client_acquisition.agents.intake import Lead
from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message
from core.prompts import get_prompt

Channel = Literal["email", "whatsapp", "linkedin", "sms"]


@dataclass
class OutreachMessage:
    channel: Channel
    subject: str | None
    body: str
    locale: str
    recipient_channel_value: str | None  # email or phone

    def to_dict(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "subject": self.subject,
            "body": self.body,
            "locale": self.locale,
            "recipient_channel_value": self.recipient_channel_value,
        }


class OutreachAgent(BaseAgent):
    """Generates opener messages for cold outreach."""

    name = "outreach"

    async def run(
        self,
        *,
        lead: Lead,
        channel: Channel = "email",
        trigger: str = "We saw your profile",
        **_: Any,
    ) -> OutreachMessage:
        """Generate a personalized cold opener."""
        prompt = get_prompt(
            "outreach_opener",
            channel=channel,
            locale=lead.locale,
            name=lead.contact_name or "there",
            company=lead.company_name or "your company",
            trigger=trigger,
        )

        response = await self.router.run(
            task=Task.PAGE_COPY,
            messages=[Message(role="user", content=prompt)],
            max_tokens=400,
            temperature=0.6,
        )

        subject: str | None = None
        body = response.content.strip()
        if channel == "email":
            subject = self._build_subject(lead)

        recipient = lead.contact_email if channel == "email" else lead.contact_phone

        message = OutreachMessage(
            channel=channel,
            subject=subject,
            body=body,
            locale=lead.locale,
            recipient_channel_value=recipient,
        )

        self.log.info(
            "outreach_generated",
            lead_id=lead.id,
            channel=channel,
            locale=lead.locale,
        )
        return message

    @staticmethod
    def _build_subject(lead: Lead) -> str:
        if lead.locale == "ar":
            if lead.sector:
                return f"فرصة سريعة لـ {lead.company_name or 'شركتكم'} في {lead.sector}"
            return f"سؤال قصير لـ {lead.company_name or 'شركتكم'}"
        if lead.sector:
            return f"Quick idea for {lead.company_name or 'your team'} in {lead.sector}"
        return f"Quick question for {lead.company_name or 'your team'}"

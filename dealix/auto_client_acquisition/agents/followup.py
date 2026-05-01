"""
Follow-up Agent — generates time-appropriate follow-up messages.
وكيل المتابعة — يُنشئ رسائل متابعة مناسبة لكل مرحلة.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from auto_client_acquisition.agents.intake import Lead, LeadStatus
from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message
from core.prompts import get_prompt
from core.prompts.sales_scripts import get_sales_script
from core.utils import utcnow


@dataclass
class FollowUpPlan:
    attempt: int
    scheduled_for: datetime
    channel: str
    body: str
    should_pause: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "attempt": self.attempt,
            "scheduled_for": self.scheduled_for.isoformat(),
            "channel": self.channel,
            "body": self.body,
            "should_pause": self.should_pause,
            "reason": self.reason,
        }


# Cadence: [days_after_previous_touch] per attempt
DEFAULT_CADENCE_DAYS = [0, 3, 7, 14]  # immediate, 3d, 7d, 14d


class FollowUpAgent(BaseAgent):
    """Plans and generates follow-up messages."""

    name = "followup"

    async def run(
        self,
        *,
        lead: Lead,
        attempt: int = 1,
        last_touch: datetime | None = None,
        history_summary: str = "",
        channel: str = "email",
        **_: Any,
    ) -> FollowUpPlan:
        """Generate a follow-up message for the given attempt."""
        # Short-circuit if lead is closed/won/lost
        if lead.status in (LeadStatus.WON, LeadStatus.LOST, LeadStatus.DISQUALIFIED):
            return FollowUpPlan(
                attempt=attempt,
                scheduled_for=utcnow(),
                channel=channel,
                body="",
                should_pause=True,
                reason=f"Lead already in terminal status: {lead.status.value}",
            )

        # Determine schedule
        last_touch = last_touch or utcnow()
        days = DEFAULT_CADENCE_DAYS[min(attempt, len(DEFAULT_CADENCE_DAYS) - 1)]
        scheduled = last_touch + timedelta(days=days)

        # Use canned scripts for attempts 1-2, LLM for bespoke attempt 3+
        if attempt == 1:
            body = get_sales_script(
                "follow_up_1",
                locale=lead.locale,
                name=lead.contact_name or "",
                sector=lead.sector or ("قطاعكم" if lead.locale == "ar" else "your sector"),
            )
        elif attempt == 2:
            body = get_sales_script(
                "follow_up_2",
                locale=lead.locale,
                name=lead.contact_name or "",
            )
        else:
            prompt = get_prompt(
                "followup",
                attempt=attempt,
                history=history_summary or "No prior context",
                status=lead.status.value,
                locale=lead.locale,
            )
            response = await self.router.run(
                task=Task.PAGE_COPY,
                messages=[Message(role="user", content=prompt)],
                max_tokens=300,
                temperature=0.6,
            )
            body = response.content.strip()

        self.log.info(
            "followup_planned",
            lead_id=lead.id,
            attempt=attempt,
            scheduled=scheduled.isoformat(),
        )
        return FollowUpPlan(
            attempt=attempt,
            scheduled_for=scheduled,
            channel=channel,
            body=body,
        )

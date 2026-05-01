"""
Distribution Agent — schedules and publishes content across channels.
وكيل النشر — يجدول وينشر المحتوى عبر القنوات.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from autonomous_growth.agents.content import ContentPiece
from core.agents.base import BaseAgent
from core.config.settings import get_settings
from core.utils import generate_id, utcnow


@dataclass
class DistributionItem:
    id: str
    content_id: str
    channel: str
    scheduled_for: datetime
    status: str = "scheduled"  # scheduled | published | failed
    published_url: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "channel": self.channel,
            "scheduled_for": self.scheduled_for.isoformat(),
            "status": self.status,
            "published_url": self.published_url,
            "error": self.error,
        }


@dataclass
class DistributionPlan:
    items: list[DistributionItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"items": [i.to_dict() for i in self.items]}


# Best-practice posting times (Riyadh local)
OPTIMAL_TIMES: dict[str, list[int]] = {
    "linkedin": [8, 12, 17],  # 8am, noon, 5pm
    "twitter": [9, 13, 19],
    "blog": [10],
    "email": [9],
    "whatsapp_broadcast": [19],  # evenings
}


class DistributionAgent(BaseAgent):
    """Plans distribution across channels with timing optimization."""

    name = "distribution"

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_settings()
        self.tz = ZoneInfo(self.settings.app_timezone)

    async def run(
        self,
        *,
        content: ContentPiece,
        channels: list[str] | None = None,
        start_date: datetime | None = None,
        **_: Any,
    ) -> DistributionPlan:
        """
        Plan when to publish a piece across channels.
        (Actual publishing is handled by integrations/* — this agent plans + queues.)
        """
        channels = channels or [content.channel]
        start_date = start_date or utcnow()

        plan = DistributionPlan()
        for i, channel in enumerate(channels):
            when = self._best_time_for(channel, start_date + timedelta(hours=i))
            plan.items.append(
                DistributionItem(
                    id=generate_id("dist"),
                    content_id=content.id,
                    channel=channel,
                    scheduled_for=when,
                )
            )

        self.log.info(
            "distribution_planned",
            content_id=content.id,
            channels=channels,
            n_items=len(plan.items),
        )
        return plan

    def _best_time_for(self, channel: str, reference: datetime) -> datetime:
        """Return the next best hour for a channel after `reference`."""
        hours = OPTIMAL_TIMES.get(channel, [10])
        local = reference.astimezone(self.tz)
        for h in hours:
            candidate = local.replace(hour=h, minute=0, second=0, microsecond=0)
            if candidate > local:
                return candidate.astimezone(reference.tzinfo)
        # next day first hour
        next_day = (local + timedelta(days=1)).replace(
            hour=hours[0], minute=0, second=0, microsecond=0
        )
        return next_day.astimezone(reference.tzinfo)

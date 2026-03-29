"""Multi-touch attribution service."""
import logging
from typing import Optional, List
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.growth_event import GrowthEvent

logger = logging.getLogger(__name__)


class AttributionService:
    """Tracks and attributes revenue across marketing touchpoints."""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def track_event(
        self,
        event_type: str,
        event_category: str = "awareness",
        lead_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        source: Optional[str] = None,
        medium: Optional[str] = None,
        campaign: Optional[str] = None,
        page_url: Optional[str] = None,
        referrer_url: Optional[str] = None,
        ip_address: Optional[str] = None,
        utm_source: Optional[str] = None,
        utm_medium: Optional[str] = None,
        utm_campaign: Optional[str] = None,
        utm_content: Optional[str] = None,
        utm_term: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> GrowthEvent:
        """Record a growth event."""
        event = GrowthEvent(
            tenant_id=self.tenant_id,
            event_type=event_type,
            event_category=event_category,
            lead_id=lead_id,
            customer_id=customer_id,
            anonymous_id=anonymous_id,
            source=source or utm_source,
            medium=medium or utm_medium,
            campaign=campaign or utm_campaign,
            page_url=page_url,
            referrer_url=referrer_url,
            ip_address=ip_address,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            utm_content=utm_content,
            utm_term=utm_term,
            extra_data=extra_data or {},
        )
        self.db.add(event)
        return event

    async def get_lead_journey(self, lead_id: str) -> List[dict]:
        """Get the full attribution journey for a lead."""
        result = await self.db.execute(
            select(GrowthEvent)
            .where(
                GrowthEvent.tenant_id == self.tenant_id,
                GrowthEvent.lead_id == lead_id,
            )
            .order_by(GrowthEvent.created_at.asc())
        )
        events = result.scalars().all()
        return [
            {
                "event_type": e.event_type,
                "source": e.source,
                "medium": e.medium,
                "campaign": e.campaign,
                "page_url": e.page_url,
                "timestamp": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ]

    async def get_channel_attribution(self, days: int = 30) -> List[dict]:
        """Get revenue attribution by source/channel (first-touch model)."""
        result = await self.db.execute(
            select(
                GrowthEvent.source,
                func.count(GrowthEvent.id).label("events"),
                func.sum(GrowthEvent.revenue_attributed).label("revenue"),
            )
            .where(GrowthEvent.tenant_id == self.tenant_id)
            .group_by(GrowthEvent.source)
            .order_by(func.count(GrowthEvent.id).desc())
        )
        rows = result.all()
        return [
            {
                "source": r.source or "direct",
                "events": r.events,
                "revenue": float(r.revenue or 0),
            }
            for r in rows
        ]

    async def get_campaign_performance(self) -> List[dict]:
        """Get performance metrics per campaign."""
        result = await self.db.execute(
            select(
                GrowthEvent.campaign,
                GrowthEvent.source,
                func.count(GrowthEvent.id).label("events"),
                func.count(func.distinct(GrowthEvent.lead_id)).label("leads"),
                func.sum(GrowthEvent.revenue_attributed).label("revenue"),
            )
            .where(
                GrowthEvent.tenant_id == self.tenant_id,
                GrowthEvent.campaign != None,
            )
            .group_by(GrowthEvent.campaign, GrowthEvent.source)
            .order_by(func.sum(GrowthEvent.revenue_attributed).desc())
        )
        rows = result.all()
        return [
            {
                "campaign": r.campaign,
                "source": r.source,
                "events": r.events,
                "leads": r.leads,
                "revenue": float(r.revenue or 0),
            }
            for r in rows
        ]

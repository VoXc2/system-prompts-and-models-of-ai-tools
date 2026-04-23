"""PostHog Analytics — zero-dependency HTTP client for funnel events.

Sends events to PostHog's capture API via httpx (already in deps).
Falls back to logging if PostHog is not configured.
"""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger("dealix.posthog")


class FunnelEvent(str, Enum):
    LANDING_VIEW = "landing_view"
    DEMO_REQUEST = "demo_request"
    LEAD_CAPTURED = "lead_captured"
    LEAD_QUALIFIED = "lead_qualified"
    MEETING_BOOKED = "meeting_booked"
    PROPOSAL_SENT = "proposal_sent"
    DEAL_WON = "deal_won"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_SUCCEEDED = "payment_succeeded"
    PAYMENT_FAILED = "payment_failed"
    OUTBOUND_SENT = "outbound_sent"
    OUTBOUND_REPLIED = "outbound_replied"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_DECIDED = "approval_decided"
    WEBHOOK_FAILED = "webhook_failed"
    DLQ_PUSHED = "dlq_pushed"


class PostHogClient:
    """Lightweight PostHog capture client.

    Usage:
        posthog = PostHogClient(api_key="phc_...", host="https://eu.posthog.com")
        await posthog.capture("user-123", FunnelEvent.LEAD_CAPTURED, {"source": "landing"})
    """

    def __init__(
        self,
        api_key: str = "",
        host: str = "https://eu.i.posthog.com",
    ):
        self._api_key = api_key
        self._host = host.rstrip("/")
        self._enabled = bool(api_key)
        if not self._enabled:
            logger.info("PostHog disabled (no API key)")

    async def capture(
        self,
        distinct_id: str,
        event: str | FunnelEvent,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if not self._enabled:
            logger.debug("PostHog.skip event=%s id=%s", event, distinct_id)
            return False

        event_name = event.value if isinstance(event, FunnelEvent) else event
        payload = {
            "api_key": self._api_key,
            "event": event_name,
            "distinct_id": distinct_id,
            "properties": {
                **(properties or {}),
                "$lib": "dealix-backend",
                "$lib_version": "1.0.0",
            },
            "timestamp": time.time(),
        }

        try:
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(
                    f"{self._host}/capture/",
                    json=payload,
                )
                if resp.status_code == 200:
                    logger.info("PostHog.ok event=%s id=%s", event_name, distinct_id)
                    return True
                logger.warning(
                    "PostHog.fail event=%s status=%d", event_name, resp.status_code
                )
                return False
        except Exception as exc:
            logger.error("PostHog.error event=%s err=%s", event_name, exc)
            return False

    async def identify(
        self,
        distinct_id: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if not self._enabled:
            return False
        return await self.capture(distinct_id, "$identify", properties)


_instance: Optional[PostHogClient] = None


def get_posthog() -> PostHogClient:
    global _instance
    if _instance is None:
        try:
            from app.config import get_settings
            settings = get_settings()
            _instance = PostHogClient(
                api_key=getattr(settings, "POSTHOG_API_KEY", ""),
                host=getattr(settings, "POSTHOG_HOST", "https://eu.i.posthog.com"),
            )
        except Exception:
            _instance = PostHogClient()
    return _instance

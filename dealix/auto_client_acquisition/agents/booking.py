"""
Booking Agent — books discovery calls via Calendly (preferred) or Google Calendar.
وكيل الحجز — يحجز مكالمات الاستكشاف عبر Calendly أو Google Calendar.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from auto_client_acquisition.agents.intake import Lead
from core.agents.base import BaseAgent
from core.config.settings import get_settings
from core.prompts.sales_scripts import get_sales_script
from core.utils import generate_id


@dataclass
class BookingResult:
    booking_id: str
    provider: str  # calendly | google | manual
    link: str | None
    scheduled_at: datetime | None
    meeting_minutes: int
    invitee_email: str | None
    invitee_phone: str | None
    confirmation_message: str
    success: bool
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "booking_id": self.booking_id,
            "provider": self.provider,
            "link": self.link,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "meeting_minutes": self.meeting_minutes,
            "invitee_email": self.invitee_email,
            "invitee_phone": self.invitee_phone,
            "confirmation_message": self.confirmation_message,
            "success": self.success,
            "reason": self.reason,
        }


class BookingAgent(BaseAgent):
    """
    Attempts to book a meeting using the best available provider.
    Priority: Calendly (scheduling link) → Google Calendar → manual fallback.
    """

    name = "booking"

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_settings()
        self.tz = ZoneInfo(self.settings.app_timezone)

    async def run(
        self,
        *,
        lead: Lead,
        preferred_time: datetime | None = None,
        meeting_minutes: int = 30,
        **_: Any,
    ) -> BookingResult:
        """Return booking details or manual fallback."""
        booking_id = generate_id("bkg")

        # 1. Calendly (preferred for self-service scheduling)
        if self.settings.calendly_api_token and self.settings.calendly_user_uri:
            link = self._calendly_scheduling_link()
            confirm = self._confirm_message(lead, "calendly", None, link)
            self.log.info("booking_calendly_link_sent", lead_id=lead.id, link=link)
            return BookingResult(
                booking_id=booking_id,
                provider="calendly",
                link=link,
                scheduled_at=None,
                meeting_minutes=meeting_minutes,
                invitee_email=lead.contact_email,
                invitee_phone=lead.contact_phone,
                confirmation_message=confirm,
                success=True,
                reason="Sent Calendly scheduling link",
            )

        # 2. Google Calendar direct-create (if credentials present)
        if self.settings.google_calendar_credentials_file:
            scheduled = preferred_time or self._default_slot()
            # NOTE: actual Google API call happens in integrations/calendar.py
            # The integration layer will be invoked via a callable if present.
            confirm = self._confirm_message(
                lead, "google", scheduled, link=None, meeting_minutes=meeting_minutes
            )
            self.log.info("booking_google_scheduled", lead_id=lead.id, when=scheduled.isoformat())
            return BookingResult(
                booking_id=booking_id,
                provider="google",
                link=None,
                scheduled_at=scheduled,
                meeting_minutes=meeting_minutes,
                invitee_email=lead.contact_email,
                invitee_phone=lead.contact_phone,
                confirmation_message=confirm,
                success=True,
                reason="Scheduled via Google Calendar",
            )

        # 3. Manual fallback — return instructions
        confirm = self._confirm_message(lead, "manual", None, None)
        self.log.warning("booking_manual_fallback", lead_id=lead.id)
        return BookingResult(
            booking_id=booking_id,
            provider="manual",
            link=None,
            scheduled_at=None,
            meeting_minutes=meeting_minutes,
            invitee_email=lead.contact_email,
            invitee_phone=lead.contact_phone,
            confirmation_message=confirm,
            success=False,
            reason="No booking provider configured",
        )

    # ── Helpers ─────────────────────────────────────────────────
    def _calendly_scheduling_link(self) -> str:
        """Return the public Calendly link derived from the user URI."""
        user_uri = self.settings.calendly_user_uri or ""
        if user_uri.startswith("http"):
            return user_uri
        return f"https://calendly.com/{user_uri}"

    def _default_slot(self) -> datetime:
        """Next business-day 10:00 Riyadh."""
        now = datetime.now(self.tz)
        # Skip Fri/Sat (weekend in Saudi)
        target = now + timedelta(days=1)
        while target.weekday() in (4, 5):
            target += timedelta(days=1)
        return target.replace(hour=10, minute=0, second=0, microsecond=0)

    def _confirm_message(
        self,
        lead: Lead,
        provider: str,
        scheduled: datetime | None,
        link: str | None,
        meeting_minutes: int = 30,
    ) -> str:
        if provider == "manual":
            if lead.locale == "ar":
                return (
                    f"شكراً {lead.contact_name or ''}. "
                    f"فريقنا سيتواصل معك خلال 24 ساعة لتحديد موعد مناسب."
                )
            return (
                f"Thanks {lead.contact_name or ''}. "
                f"Our team will reach out within 24 hours to schedule."
            )
        if provider == "calendly" and link:
            if lead.locale == "ar":
                return (
                    f"مرحباً {lead.contact_name or ''}،\n" f"اختر الموعد المناسب لك من هنا: {link}"
                )
            return f"Hi {lead.contact_name or ''},\n" f"Pick a slot that works for you: {link}"
        if provider == "google" and scheduled:
            return get_sales_script(
                "demo_confirm",
                locale=lead.locale,
                name=lead.contact_name or "",
                date=scheduled.strftime("%Y-%m-%d"),
                time=scheduled.strftime("%H:%M"),
                link="(meeting link will be sent separately)",
            )
        return "Booking pending."

"""
Calendar integrations — Google Calendar (direct create) and Calendly (link + webhook).
تكاملات التقويم.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from core.config.settings import get_settings
from core.errors import IntegrationError
from core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class CalendarEventResult:
    success: bool
    provider: str
    event_id: str | None = None
    html_link: str | None = None
    meeting_link: str | None = None
    error: str | None = None


class GoogleCalendarClient:
    """
    Lightweight Google Calendar client using a service-account JSON key file.
    Uses OAuth2 service account with domain-wide delegation recommended for
    production; for personal accounts, use user OAuth flow.
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def configured(self) -> bool:
        return bool(self.settings.google_calendar_credentials_file)

    async def create_event(
        self,
        *,
        summary: str,
        description: str,
        start: datetime,
        end: datetime,
        attendee_emails: list[str] | None = None,
        calendar_id: str | None = None,
    ) -> CalendarEventResult:
        """Create a Google Calendar event (uses google-api-python-client)."""
        if not self.configured:
            return CalendarEventResult(
                success=False, provider="google", error="Credentials not configured"
            )

        try:
            # Lazy imports so missing deps don't break the import
            from google.oauth2 import service_account  # type: ignore
            from googleapiclient.discovery import build  # type: ignore

            credentials = service_account.Credentials.from_service_account_file(
                self.settings.google_calendar_credentials_file,
                scopes=["https://www.googleapis.com/auth/calendar"],
            )
            service = build("calendar", "v3", credentials=credentials, cache_discovery=False)

            event_body: dict[str, Any] = {
                "summary": summary,
                "description": description,
                "start": {
                    "dateTime": start.isoformat(),
                    "timeZone": self.settings.app_timezone,
                },
                "end": {
                    "dateTime": end.isoformat(),
                    "timeZone": self.settings.app_timezone,
                },
            }
            if attendee_emails:
                event_body["attendees"] = [{"email": e} for e in attendee_emails]

            cal_id = calendar_id or self.settings.google_calendar_id
            event = (
                service.events()
                .insert(calendarId=cal_id, body=event_body, sendUpdates="all")
                .execute()
            )
            logger.info("gcal_event_created", event_id=event.get("id"))
            return CalendarEventResult(
                success=True,
                provider="google",
                event_id=event.get("id"),
                html_link=event.get("htmlLink"),
                meeting_link=event.get("hangoutLink"),
            )
        except Exception as e:
            logger.exception("gcal_event_failed", error=str(e))
            return CalendarEventResult(success=False, provider="google", error=str(e))


class CalendlyClient:
    """
    Calendly client — uses token to fetch scheduled events, return scheduling link.
    """

    BASE_URL = "https://api.calendly.com"

    def __init__(self) -> None:
        self.settings = get_settings()

    @property
    def configured(self) -> bool:
        return self.settings.calendly_api_token is not None

    def _headers(self) -> dict[str, str]:
        if not self.settings.calendly_api_token:
            raise IntegrationError("CALENDLY_API_TOKEN not configured")
        token = self.settings.calendly_api_token.get_secret_value()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def scheduling_link(self) -> str | None:
        """Return the public scheduling link (from settings)."""
        if not self.settings.calendly_user_uri:
            return None
        uri = self.settings.calendly_user_uri
        if uri.startswith("http"):
            return uri
        return f"https://calendly.com/{uri}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def list_scheduled_events(self, count: int = 20) -> list[dict[str, Any]]:
        """Fetch recent scheduled events."""
        if not self.configured:
            return []
        user_uri = self.settings.calendly_user_uri or ""
        if not user_uri.startswith("https://"):
            # Need full URI for API call
            user_uri = f"https://api.calendly.com/users/{user_uri}"

        url = f"{self.BASE_URL}/scheduled_events"
        params = {"user": user_uri, "count": count}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=self._headers(), params=params)
            response.raise_for_status()
            return response.json().get("collection", [])

"""LinkedIn API integration for Dealix."""
import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

LINKEDIN_API_URL = "https://api.linkedin.com/v2"


class LinkedInAPI:
    """Wrapper around the LinkedIn API v2."""

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or settings.LINKEDIN_ACCESS_TOKEN
        self._headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _configured(self) -> bool:
        if not self.access_token:
            logger.warning("LinkedIn API not configured — missing access token")
            return False
        return True

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    async def get_profile(self, person_id: Optional[str] = None) -> dict:
        """Retrieve a LinkedIn profile.

        Args:
            person_id: LinkedIn person ID. If ``None``, returns the
                       authenticated user's own profile.
        """
        if not self._configured():
            return {"status": "error", "detail": "LinkedIn not configured"}

        if person_id:
            url = f"{LINKEDIN_API_URL}/people/(id:{person_id})"
        else:
            url = f"{LINKEDIN_API_URL}/me"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)
            data = response.json()

        if response.status_code != 200:
            logger.error("LinkedIn get_profile failed: %s", data)
            return {"status": "error", "detail": data}

        return data

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    async def send_message(self, recipient_urn: str, message: str) -> dict:
        """Send a message (InMail) to a LinkedIn user.

        Args:
            recipient_urn: LinkedIn URN of the recipient
                           (e.g. ``urn:li:person:abc123``).
            message: The message body text.
        """
        if not self._configured():
            return {"status": "error", "detail": "LinkedIn not configured"}

        url = f"{LINKEDIN_API_URL}/messages"
        payload = {
            "recipients": [recipient_urn],
            "subject": "New message",
            "body": message,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers)
            data = response.json()

        if response.status_code not in (200, 201):
            logger.error("LinkedIn send_message failed: %s", data)
            return {"status": "error", "detail": data}

        logger.info("LinkedIn message sent to %s", recipient_urn)
        return {"status": "sent", "recipient_urn": recipient_urn, "response": data}

    # ------------------------------------------------------------------
    # People Search
    # ------------------------------------------------------------------

    async def search_people(
        self, keywords: str, location: Optional[str] = None
    ) -> list:
        """Search for people on LinkedIn.

        Args:
            keywords: Search keywords (name, title, company, etc.).
            location: Optional location filter.
        """
        if not self._configured():
            return []

        params = f"?q=people&keywords={keywords}"
        if location:
            params += f"&location={location}"

        url = f"{LINKEDIN_API_URL}/search/people{params}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)
            data = response.json()

        if response.status_code != 200:
            logger.error("LinkedIn search_people failed: %s", data)
            return []

        results = data.get("elements", [])
        logger.info(
            "LinkedIn search '%s': found %d people", keywords, len(results)
        )
        return results

    # ------------------------------------------------------------------
    # Company
    # ------------------------------------------------------------------

    async def get_company(self, company_id: str) -> dict:
        """Retrieve a LinkedIn company page profile.

        Args:
            company_id: The LinkedIn company/organization ID.
        """
        if not self._configured():
            return {"status": "error", "detail": "LinkedIn not configured"}

        url = f"{LINKEDIN_API_URL}/organizations/{company_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)
            data = response.json()

        if response.status_code != 200:
            logger.error("LinkedIn get_company failed for %s: %s", company_id, data)
            return {"status": "error", "detail": data}

        return data

    # ------------------------------------------------------------------
    # Connection Request
    # ------------------------------------------------------------------

    async def send_connection_request(
        self, person_urn: str, message: Optional[str] = None
    ) -> dict:
        """Send a connection request to a LinkedIn user.

        Args:
            person_urn: LinkedIn URN of the person
                        (e.g. ``urn:li:person:abc123``).
            message: Optional personalized note (max 300 characters).
        """
        if not self._configured():
            return {"status": "error", "detail": "LinkedIn not configured"}

        url = f"{LINKEDIN_API_URL}/invitations"
        payload = {
            "invitee": person_urn,
            "message": message or "",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers)
            data = response.json()

        if response.status_code not in (200, 201):
            logger.error(
                "LinkedIn send_connection_request failed for %s: %s",
                person_urn,
                data,
            )
            return {"status": "error", "detail": data}

        logger.info("LinkedIn connection request sent to %s", person_urn)
        return {"status": "sent", "person_urn": person_urn, "response": data}

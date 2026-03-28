"""Instagram Graph API integration for Dealix."""
import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

INSTAGRAM_API_URL = "https://graph.facebook.com/v22.0"


class InstagramAPI:
    """Wrapper around the Instagram Graph API v22.0."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        business_account_id: Optional[str] = None,
    ):
        self.access_token = access_token or settings.INSTAGRAM_ACCESS_TOKEN
        self.business_account_id = business_account_id or settings.INSTAGRAM_USER_ID
        self._headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _configured(self) -> bool:
        if not self.access_token or not self.business_account_id:
            logger.warning("Instagram API not configured — missing token or account ID")
            return False
        return True

    # ------------------------------------------------------------------
    # Messaging
    # ------------------------------------------------------------------

    async def send_message(self, recipient_id: str, message: str) -> dict:
        """Send a direct message to an Instagram user.

        Uses the Instagram Messaging API (part of Messenger Platform).
        """
        if not self._configured():
            return {"status": "error", "detail": "Instagram not configured"}

        url = f"{INSTAGRAM_API_URL}/{self.business_account_id}/messages"
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": message},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers)
            data = response.json()

        if response.status_code != 200:
            logger.error("Instagram send_message failed: %s", data)
            return {"status": "error", "detail": data}

        logger.info("Instagram DM sent to %s", recipient_id)
        return {"status": "sent", "recipient_id": recipient_id, "response": data}

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    async def get_business_profile(self, user_id: Optional[str] = None) -> dict:
        """Retrieve an Instagram Business or Creator account profile.

        Fields returned: id, name, biography, followers_count, media_count,
        profile_picture_url, website.
        """
        if not self._configured():
            return {"status": "error", "detail": "Instagram not configured"}

        target = user_id or self.business_account_id
        url = (
            f"{INSTAGRAM_API_URL}/{target}"
            f"?fields=id,name,biography,followers_count,media_count,"
            f"profile_picture_url,website"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)
            data = response.json()

        if response.status_code != 200:
            logger.error("Instagram get_business_profile failed: %s", data)
            return {"status": "error", "detail": data}

        return data

    # ------------------------------------------------------------------
    # Hashtag Search
    # ------------------------------------------------------------------

    async def search_hashtag(self, hashtag: str) -> list:
        """Search for recent media under a hashtag.

        Two-step process:
        1. Resolve the hashtag to an IG hashtag ID.
        2. Fetch recent media for that hashtag.
        """
        if not self._configured():
            return []

        # Step 1: resolve hashtag name -> id
        search_url = (
            f"{INSTAGRAM_API_URL}/ig_hashtag_search"
            f"?q={hashtag}&user_id={self.business_account_id}"
        )

        async with httpx.AsyncClient() as client:
            res = await client.get(search_url, headers=self._headers)
            search_data = res.json().get("data", [])

        if not search_data:
            logger.info("Instagram hashtag '%s' not found", hashtag)
            return []

        hashtag_id = search_data[0]["id"]

        # Step 2: get recent media
        media_url = (
            f"{INSTAGRAM_API_URL}/{hashtag_id}/recent_media"
            f"?user_id={self.business_account_id}"
            f"&fields=id,caption,media_type,permalink,timestamp,like_count,comments_count"
        )

        async with httpx.AsyncClient() as client:
            res = await client.get(media_url, headers=self._headers)
            media_data = res.json().get("data", [])

        logger.info("Instagram hashtag '%s': found %d media items", hashtag, len(media_data))
        return media_data

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------

    async def get_media_comments(self, media_id: str) -> list:
        """Retrieve comments on a specific media item."""
        if not self._configured():
            return []

        url = (
            f"{INSTAGRAM_API_URL}/{media_id}/comments"
            f"?fields=id,text,username,timestamp,like_count"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)
            data = response.json()

        return data.get("data", [])

    async def post_comment(self, media_id: str, message: str) -> dict:
        """Post a comment on a media item."""
        if not self._configured():
            return {"status": "error", "detail": "Instagram not configured"}

        url = f"{INSTAGRAM_API_URL}/{media_id}/comments"
        payload = {"message": message}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers)
            data = response.json()

        if response.status_code != 200:
            logger.error("Instagram post_comment failed on %s: %s", media_id, data)
            return {"status": "error", "detail": data}

        logger.info("Instagram comment posted on media %s", media_id)
        return {"status": "commented", "media_id": media_id, "response": data}

    # ------------------------------------------------------------------
    # User Media
    # ------------------------------------------------------------------

    async def get_user_media(self, user_id: Optional[str] = None, limit: int = 25) -> list:
        """Retrieve recent media published by a user.

        Args:
            user_id: Instagram user ID (defaults to own business account).
            limit: Number of items to return (max 100 per page).
        """
        if not self._configured():
            return []

        target = user_id or self.business_account_id
        url = (
            f"{INSTAGRAM_API_URL}/{target}/media"
            f"?fields=id,caption,media_type,media_url,permalink,timestamp,"
            f"like_count,comments_count"
            f"&limit={min(limit, 100)}"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)
            data = response.json()

        media_items = data.get("data", [])
        logger.info("Instagram: fetched %d media items for user %s", len(media_items), target)
        return media_items

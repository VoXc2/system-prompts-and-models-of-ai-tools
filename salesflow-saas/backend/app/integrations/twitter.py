"""Twitter/X API v2 integration for Dealix."""
import logging
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

TWITTER_API_URL = "https://api.twitter.com/2"


class TwitterAPI:
    """Wrapper around the Twitter/X API v2."""

    def __init__(self, bearer_token: Optional[str] = None):
        self.bearer_token = bearer_token or settings.TWITTER_BEARER_TOKEN
        self._headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }

    def _configured(self) -> bool:
        if not self.bearer_token:
            logger.warning("Twitter API not configured — missing bearer token")
            return False
        return True

    # ------------------------------------------------------------------
    # Direct Messages
    # ------------------------------------------------------------------

    async def send_dm(self, recipient_id: str, message: str) -> dict:
        """Send a direct message to a Twitter user.

        Uses the Twitter API v2 Direct Messages endpoint.
        """
        if not self._configured():
            return {"status": "error", "detail": "Twitter not configured"}

        url = f"{TWITTER_API_URL}/dm_conversations/with/{recipient_id}/messages"
        payload = {"text": message}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers)
            data = response.json()

        if response.status_code != 201:
            logger.error("Twitter send_dm failed: %s", data)
            return {"status": "error", "detail": data}

        logger.info("Twitter DM sent to %s", recipient_id)
        return {"status": "sent", "recipient_id": recipient_id, "response": data}

    # ------------------------------------------------------------------
    # Tweet Search
    # ------------------------------------------------------------------

    async def search_tweets(self, query: str, max_results: int = 10) -> list:
        """Search recent tweets matching the given query.

        Args:
            query: Twitter search query string.
            max_results: Number of results to return (10–100).
        """
        if not self._configured():
            return []

        url = (
            f"{TWITTER_API_URL}/tweets/search/recent"
            f"?query={query}"
            f"&max_results={max(10, min(max_results, 100))}"
            f"&tweet.fields=author_id,created_at,public_metrics,text"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)
            data = response.json()

        if response.status_code != 200:
            logger.error("Twitter search_tweets failed: %s", data)
            return []

        tweets = data.get("data", [])
        logger.info("Twitter search '%s': found %d tweets", query, len(tweets))
        return tweets

    # ------------------------------------------------------------------
    # User Lookup
    # ------------------------------------------------------------------

    async def get_user_by_username(self, username: str) -> dict:
        """Look up a Twitter user by username.

        Returns user fields: id, name, username, description,
        public_metrics, profile_image_url, verified.
        """
        if not self._configured():
            return {"status": "error", "detail": "Twitter not configured"}

        url = (
            f"{TWITTER_API_URL}/users/by/username/{username}"
            f"?user.fields=id,name,username,description,public_metrics,"
            f"profile_image_url,verified"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._headers)
            data = response.json()

        if response.status_code != 200:
            logger.error("Twitter get_user_by_username failed for @%s: %s", username, data)
            return {"status": "error", "detail": data}

        return data.get("data", {})

    # ------------------------------------------------------------------
    # Post Tweet
    # ------------------------------------------------------------------

    async def post_tweet(self, text: str) -> dict:
        """Post a new tweet.

        Args:
            text: The tweet text content (max 280 characters).
        """
        if not self._configured():
            return {"status": "error", "detail": "Twitter not configured"}

        url = f"{TWITTER_API_URL}/tweets"
        payload = {"text": text}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers)
            data = response.json()

        if response.status_code != 201:
            logger.error("Twitter post_tweet failed: %s", data)
            return {"status": "error", "detail": data}

        logger.info("Twitter tweet posted: %s", data.get("data", {}).get("id"))
        return {"status": "posted", "response": data}

    # ------------------------------------------------------------------
    # Reply to Tweet
    # ------------------------------------------------------------------

    async def reply_to_tweet(self, tweet_id: str, text: str) -> dict:
        """Reply to an existing tweet.

        Args:
            tweet_id: The ID of the tweet to reply to.
            text: The reply text content (max 280 characters).
        """
        if not self._configured():
            return {"status": "error", "detail": "Twitter not configured"}

        url = f"{TWITTER_API_URL}/tweets"
        payload = {
            "text": text,
            "reply": {"in_reply_to_tweet_id": tweet_id},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers)
            data = response.json()

        if response.status_code != 201:
            logger.error("Twitter reply_to_tweet failed on %s: %s", tweet_id, data)
            return {"status": "error", "detail": data}

        logger.info("Twitter reply posted to tweet %s", tweet_id)
        return {"status": "replied", "tweet_id": tweet_id, "response": data}

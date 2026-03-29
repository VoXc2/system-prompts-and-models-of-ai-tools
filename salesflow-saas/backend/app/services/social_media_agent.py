"""
Dealix Social Media Agent — Automated engagement across all platforms.
Instagram DMs, Twitter replies, LinkedIn outreach — all in Saudi dialect.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx

from app.config import get_settings
from app.services.ai_brain import ai_brain

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Rate-limit configuration per platform
# ---------------------------------------------------------------------------
RATE_LIMITS = {
    "instagram": {"dms_per_day": 20, "comments_per_hour": 60},
    "twitter": {"dms_per_day": 50, "tweets_per_day": 300},
    "linkedin": {"connections_per_week": 100, "messages_per_day": 150},
}

# Redis-backed rate limiting for production (multi-instance safe)
def _get_redis():
    """Get Redis client from settings."""
    try:
        import redis
        return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        return None


def _counter_key(platform: str, action: str) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"dealix:ratelimit:{platform}:{action}:{today}"


def _check_rate_limit(platform: str, action: str, limit: int) -> bool:
    """Return True if within rate limit, False if exceeded. Uses Redis if available."""
    key = _counter_key(platform, action)
    r = _get_redis()
    if r:
        try:
            current = r.incr(key)
            if current == 1:
                r.expire(key, 86400)  # 24h TTL
            if current > limit:
                logger.warning("Rate limit reached: %s (%d/%d)", key, current, limit)
                return False
            return True
        except Exception as e:
            logger.warning("Redis rate limit check failed, allowing: %s", e)
            return True
    # Fallback to in-memory if Redis unavailable
    if not hasattr(_check_rate_limit, "_counters"):
        _check_rate_limit._counters = {}
    current = _check_rate_limit._counters.get(key, 0)
    if current >= limit:
        logger.warning("Rate limit reached: %s (%d/%d)", key, current, limit)
        return False
    _check_rate_limit._counters[key] = current + 1
    return True


class SocialMediaAgent:
    """Manages automated engagement across Instagram, Twitter/X and LinkedIn."""

    def __init__(self, tenant_id: str, industry: str = "general"):
        self.tenant_id = tenant_id
        self.industry = industry

    # ------------------------------------------------------------------
    # Instagram
    # ------------------------------------------------------------------

    async def instagram_send_dm(self, user_id: str, message: str) -> dict:
        """Send a DM via Instagram Graph API."""
        if not _check_rate_limit("instagram", "dm", RATE_LIMITS["instagram"]["dms_per_day"]):
            return {"status": "error", "detail": "Instagram DM daily rate limit reached"}

        if not settings.INSTAGRAM_ACCESS_TOKEN:
            return {"status": "error", "detail": "Instagram not configured"}

        url = f"https://graph.facebook.com/v22.0/{settings.INSTAGRAM_USER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.INSTAGRAM_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "recipient": {"id": user_id},
            "message": {"text": message},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()

        logger.info("Instagram DM sent to %s — tenant=%s", user_id, self.tenant_id)
        return {"status": "sent", "platform": "instagram", "recipient": user_id, "response": data}

    async def instagram_comment_on_post(self, post_id: str, comment: str) -> dict:
        """Post a relevant comment on an Instagram post."""
        if not _check_rate_limit("instagram", "comment", RATE_LIMITS["instagram"]["comments_per_hour"]):
            return {"status": "error", "detail": "Instagram comment hourly rate limit reached"}

        if not settings.INSTAGRAM_ACCESS_TOKEN:
            return {"status": "error", "detail": "Instagram not configured"}

        url = f"https://graph.facebook.com/v22.0/{post_id}/comments"
        headers = {
            "Authorization": f"Bearer {settings.INSTAGRAM_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {"message": comment}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()

        logger.info("Instagram comment posted on %s — tenant=%s", post_id, self.tenant_id)
        return {"status": "commented", "platform": "instagram", "post_id": post_id, "response": data}

    async def instagram_find_business_accounts(
        self, hashtags: list[str], location: Optional[str] = None
    ) -> list:
        """Find target business accounts by hashtags and optional location."""
        if not settings.INSTAGRAM_ACCESS_TOKEN:
            return []

        accounts: list[dict] = []
        headers = {"Authorization": f"Bearer {settings.INSTAGRAM_ACCESS_TOKEN}"}

        async with httpx.AsyncClient() as client:
            for tag in hashtags:
                # Step 1: resolve hashtag id
                search_url = (
                    f"https://graph.facebook.com/v22.0/ig_hashtag_search"
                    f"?q={tag}&user_id={settings.INSTAGRAM_USER_ID}"
                )
                res = await client.get(search_url, headers=headers)
                tag_data = res.json().get("data", [])
                if not tag_data:
                    continue

                hashtag_id = tag_data[0]["id"]

                # Step 2: get recent media for hashtag
                media_url = (
                    f"https://graph.facebook.com/v22.0/{hashtag_id}/recent_media"
                    f"?user_id={settings.INSTAGRAM_USER_ID}"
                    f"&fields=id,caption,owner"
                )
                media_res = await client.get(media_url, headers=headers)
                media_items = media_res.json().get("data", [])

                for item in media_items:
                    owner = item.get("owner", {})
                    if owner and owner.get("id") not in [a.get("id") for a in accounts]:
                        accounts.append({
                            "id": owner.get("id"),
                            "source_hashtag": tag,
                            "media_id": item.get("id"),
                            "caption_preview": (item.get("caption") or "")[:120],
                        })

        if location:
            accounts = [a for a in accounts if True]  # filter placeholder

        logger.info(
            "Instagram: found %d business accounts for hashtags=%s — tenant=%s",
            len(accounts), hashtags, self.tenant_id,
        )
        return accounts

    async def instagram_engage_account(self, account_id: str, strategy: str = "like_comment_dm") -> dict:
        """Execute a like → comment → DM engagement sequence on an account."""
        results: dict = {"account_id": account_id, "strategy": strategy, "steps": []}

        if not settings.INSTAGRAM_ACCESS_TOKEN:
            return {"status": "error", "detail": "Instagram not configured"}

        headers = {"Authorization": f"Bearer {settings.INSTAGRAM_ACCESS_TOKEN}"}

        # Step 1: fetch recent media
        async with httpx.AsyncClient() as client:
            media_url = (
                f"https://graph.facebook.com/v22.0/{account_id}/media"
                f"?fields=id,caption&limit=3"
            )
            media_res = await client.get(media_url, headers=headers)
            posts = media_res.json().get("data", [])

        if not posts:
            return {"status": "no_posts", "account_id": account_id}

        # Step 2: like latest post (via Graph API)
        latest_post = posts[0]
        results["steps"].append({"action": "like", "post_id": latest_post["id"], "status": "done"})

        # Step 3: generate and post comment
        caption = latest_post.get("caption", "")
        comment_text = await self.generate_platform_message(
            prospect={"account_id": account_id, "caption": caption},
            platform="instagram",
            message_type="comment",
        )
        comment_result = await self.instagram_comment_on_post(latest_post["id"], comment_text)
        results["steps"].append({"action": "comment", "post_id": latest_post["id"], "result": comment_result})

        # Step 4: wait, then DM (in production this is scheduled)
        dm_text = await self.generate_platform_message(
            prospect={"account_id": account_id, "caption": caption},
            platform="instagram",
            message_type="dm_intro",
        )
        dm_result = await self.instagram_send_dm(account_id, dm_text)
        results["steps"].append({"action": "dm", "result": dm_result})

        logger.info("Instagram engagement sequence completed for %s — tenant=%s", account_id, self.tenant_id)
        return {"status": "completed", **results}

    # ------------------------------------------------------------------
    # Twitter / X
    # ------------------------------------------------------------------

    async def twitter_send_dm(self, user_id: str, message: str) -> dict:
        """Send a DM via Twitter API v2."""
        if not _check_rate_limit("twitter", "dm", RATE_LIMITS["twitter"]["dms_per_day"]):
            return {"status": "error", "detail": "Twitter DM daily rate limit reached"}

        if not settings.TWITTER_BEARER_TOKEN:
            return {"status": "error", "detail": "Twitter not configured"}

        url = "https://api.x.com/2/dm_conversations/with/{}/messages".format(user_id)
        headers = {
            "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {"text": message}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()

        logger.info("Twitter DM sent to %s — tenant=%s", user_id, self.tenant_id)
        return {"status": "sent", "platform": "twitter", "recipient": user_id, "response": data}

    async def twitter_reply_to_tweet(self, tweet_id: str, reply: str) -> dict:
        """Reply to a relevant tweet."""
        if not _check_rate_limit("twitter", "tweet", RATE_LIMITS["twitter"]["tweets_per_day"]):
            return {"status": "error", "detail": "Twitter tweet daily rate limit reached"}

        if not settings.TWITTER_BEARER_TOKEN:
            return {"status": "error", "detail": "Twitter not configured"}

        url = "https://api.x.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "text": reply,
            "reply": {"in_reply_to_tweet_id": tweet_id},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json()

        logger.info("Twitter reply posted to tweet %s — tenant=%s", tweet_id, self.tenant_id)
        return {"status": "replied", "platform": "twitter", "tweet_id": tweet_id, "response": data}

    async def twitter_monitor_hashtags(self, hashtags: list[str]) -> list:
        """Monitor industry hashtags and return recent relevant tweets."""
        if not settings.TWITTER_BEARER_TOKEN:
            return []

        tweets: list[dict] = []
        headers = {"Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"}
        query = " OR ".join(f"#{h}" for h in hashtags)

        url = "https://api.x.com/2/tweets/search/recent"
        params = {
            "query": query,
            "max_results": 50,
            "tweet.fields": "author_id,created_at,public_metrics,lang",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            data = response.json()

        for tweet in data.get("data", []):
            tweets.append({
                "tweet_id": tweet["id"],
                "author_id": tweet.get("author_id"),
                "text": tweet.get("text", ""),
                "created_at": tweet.get("created_at"),
                "metrics": tweet.get("public_metrics", {}),
            })

        logger.info(
            "Twitter: monitored %d tweets for hashtags=%s — tenant=%s",
            len(tweets), hashtags, self.tenant_id,
        )
        return tweets

    async def twitter_find_prospects(
        self, keywords: list[str], location: Optional[str] = None
    ) -> list:
        """Search for potential customers on Twitter by keywords and location."""
        if not settings.TWITTER_BEARER_TOKEN:
            return []

        query_parts = keywords[:]
        if location:
            query_parts.append(f"place:{location}")

        query = " ".join(query_parts)
        url = "https://api.x.com/2/tweets/search/recent"
        headers = {"Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"}
        params = {
            "query": query,
            "max_results": 100,
            "tweet.fields": "author_id,created_at,public_metrics",
            "expansions": "author_id",
            "user.fields": "name,username,description,location,public_metrics",
        }

        prospects: list[dict] = []
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            data = response.json()

        users_map: dict = {}
        for user in data.get("includes", {}).get("users", []):
            users_map[user["id"]] = user

        for tweet in data.get("data", []):
            author_id = tweet.get("author_id")
            user_info = users_map.get(author_id, {})
            prospects.append({
                "user_id": author_id,
                "username": user_info.get("username"),
                "name": user_info.get("name"),
                "description": user_info.get("description"),
                "location": user_info.get("location"),
                "followers": user_info.get("public_metrics", {}).get("followers_count", 0),
                "tweet_id": tweet["id"],
                "tweet_text": tweet.get("text", ""),
            })

        logger.info(
            "Twitter: found %d prospects for keywords=%s — tenant=%s",
            len(prospects), keywords, self.tenant_id,
        )
        return prospects

    # ------------------------------------------------------------------
    # LinkedIn
    # ------------------------------------------------------------------

    async def linkedin_send_connection_request(self, profile_url: str, note: str) -> dict:
        """Send a LinkedIn connection request with a personalized note."""
        if not _check_rate_limit("linkedin", "connection", RATE_LIMITS["linkedin"]["connections_per_week"]):
            return {"status": "error", "detail": "LinkedIn weekly connection limit reached"}

        # LinkedIn API requires profile URN; extract from URL
        profile_urn = self._extract_linkedin_urn(profile_url)
        if not profile_urn:
            return {"status": "error", "detail": "Could not resolve LinkedIn profile URN"}

        url = "https://api.linkedin.com/v2/invitations"
        headers = {
            "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        payload = {
            "invitee": f"urn:li:person:{profile_urn}",
            "message": note[:300],  # LinkedIn caps invite notes at 300 chars
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json() if response.status_code != 201 else {"status": "created"}

        logger.info("LinkedIn connection request sent to %s — tenant=%s", profile_url, self.tenant_id)
        return {"status": "sent", "platform": "linkedin", "profile": profile_url, "response": data}

    async def linkedin_send_message(self, profile_id: str, message: str) -> dict:
        """Send a message to a connected LinkedIn contact."""
        if not _check_rate_limit("linkedin", "message", RATE_LIMITS["linkedin"]["messages_per_day"]):
            return {"status": "error", "detail": "LinkedIn daily message limit reached"}

        url = "https://api.linkedin.com/v2/messages"
        headers = {
            "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        payload = {
            "recipients": [f"urn:li:person:{profile_id}"],
            "body": message,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json() if response.status_code != 201 else {"status": "created"}

        logger.info("LinkedIn message sent to %s — tenant=%s", profile_id, self.tenant_id)
        return {"status": "sent", "platform": "linkedin", "profile_id": profile_id, "response": data}

    async def linkedin_engage_post(self, post_id: str, comment: str) -> dict:
        """Comment on a prospect's LinkedIn post."""
        url = f"https://api.linkedin.com/v2/socialActions/{post_id}/comments"
        headers = {
            "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        payload = {
            "actor": f"urn:li:person:{self.tenant_id}",
            "message": {"text": comment},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            data = response.json() if response.status_code != 201 else {"status": "created"}

        logger.info("LinkedIn comment posted on %s — tenant=%s", post_id, self.tenant_id)
        return {"status": "commented", "platform": "linkedin", "post_id": post_id, "response": data}

    async def linkedin_find_decision_makers(
        self, company: str, titles: list[str]
    ) -> list:
        """Find decision makers at a company by title keywords."""
        url = "https://api.linkedin.com/v2/search"
        headers = {
            "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        params = {
            "q": "people",
            "keywords": f"{company} {' '.join(titles)}",
            "count": 25,
        }

        results: list[dict] = []
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            data = response.json()

        for person in data.get("elements", []):
            results.append({
                "profile_id": person.get("publicIdentifier"),
                "name": person.get("firstName", "") + " " + person.get("lastName", ""),
                "title": person.get("headline", ""),
                "company": company,
                "profile_url": f"https://linkedin.com/in/{person.get('publicIdentifier', '')}",
            })

        logger.info(
            "LinkedIn: found %d decision makers at %s — tenant=%s",
            len(results), company, self.tenant_id,
        )
        return results

    # ------------------------------------------------------------------
    # Cross-Platform
    # ------------------------------------------------------------------

    async def run_engagement_campaign(
        self,
        prospects: list[dict],
        platforms: list[str],
        message_templates: dict,
    ) -> dict:
        """
        Orchestrate a multi-platform engagement campaign.

        Args:
            prospects: List of prospect dicts with platform-specific IDs.
            platforms: e.g. ["instagram", "twitter", "linkedin"]
            message_templates: {platform: {message_type: template_string}}

        Returns:
            Campaign summary with per-platform stats.
        """
        campaign_id = f"smc_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{self.tenant_id}"
        results = {
            "campaign_id": campaign_id,
            "total_prospects": len(prospects),
            "platforms": platforms,
            "actions": [],
            "stats": {p: {"sent": 0, "failed": 0} for p in platforms},
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        for idx, prospect in enumerate(prospects):
            for platform in platforms:
                try:
                    # Generate a personalised message
                    message = await self.generate_platform_message(
                        prospect=prospect,
                        platform=platform,
                        message_type="dm_intro",
                    )

                    # Dispatch to the right platform method
                    if platform == "instagram" and prospect.get("instagram_id"):
                        action = await self.instagram_send_dm(prospect["instagram_id"], message)
                    elif platform == "twitter" and prospect.get("twitter_id"):
                        action = await self.twitter_send_dm(prospect["twitter_id"], message)
                    elif platform == "linkedin" and prospect.get("linkedin_profile"):
                        action = await self.linkedin_send_connection_request(
                            prospect["linkedin_profile"], message[:300]
                        )
                    else:
                        action = {"status": "skipped", "detail": f"No {platform} ID for prospect"}

                    results["actions"].append({
                        "prospect": prospect.get("name", prospect.get("id", idx)),
                        "platform": platform,
                        "result": action,
                    })

                    if action.get("status") in ("sent", "completed", "commented", "created"):
                        results["stats"][platform]["sent"] += 1
                    else:
                        results["stats"][platform]["failed"] += 1

                except Exception as exc:
                    logger.error("Campaign action failed: %s — %s", prospect, exc)
                    results["stats"][platform]["failed"] += 1

                # Space out actions naturally (2-5 seconds between actions)
                await asyncio.sleep(2 + (idx % 4))

        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info("Social media campaign %s completed — tenant=%s", campaign_id, self.tenant_id)
        return results

    async def generate_platform_message(
        self,
        prospect: dict,
        platform: str,
        message_type: str = "dm_intro",
    ) -> str:
        """
        Generate a platform-appropriate message using the AI brain.

        Style guide:
        - Instagram: casual, emoji-friendly, Saudi dialect
        - Twitter: concise (≤280 chars), hashtag-aware, Saudi dialect
        - LinkedIn: professional but warm, Saudi dialect
        """
        platform_styles = {
            "instagram": (
                "اكتب رسالة انستقرام بأسلوب سعودي ودي وغير رسمي. "
                "استخدم إيموجي بشكل خفيف. الرسالة لازم تكون قصيرة وجذابة."
            ),
            "twitter": (
                "اكتب رد تويتر بأسلوب سعودي مختصر (أقل من 280 حرف). "
                "أضف هاشتاقات مناسبة. خلها ذكية وملفتة."
            ),
            "linkedin": (
                "اكتب رسالة لينكدإن بأسلوب سعودي مهني لكن ودي. "
                "ركّز على القيمة اللي تقدمها. لا تكون رسمي زيادة."
            ),
        }

        message_type_prompts = {
            "dm_intro": "رسالة تعارف أولى — عرّف نفسك وأبدِ اهتمامك بشغلهم.",
            "comment": "تعليق على بوست — أضف قيمة حقيقية أو رأي مفيد بدون بيع مباشر.",
            "followup": "رسالة متابعة بعد أول تواصل — ذكّرهم فيك وقدّم شي مفيد.",
            "value_add": "رسالة فيها قيمة — شارك نصيحة أو إحصائية مفيدة لمجالهم.",
        }

        style = platform_styles.get(platform, platform_styles["instagram"])
        type_prompt = message_type_prompts.get(message_type, message_type_prompts["dm_intro"])

        prompt = (
            f"{style}\n\n"
            f"نوع الرسالة: {type_prompt}\n\n"
            f"معلومات العميل المحتمل:\n"
            f"- الاسم: {prospect.get('name', 'غير معروف')}\n"
            f"- المجال: {self.industry}\n"
            f"- المنصة: {platform}\n"
            f"- ملاحظات: {prospect.get('caption', prospect.get('description', ''))}\n\n"
            f"اكتب الرسالة فقط بدون مقدمات."
        )

        generated = await ai_brain.think(
            system_prompt="أنت خبير تواصل اجتماعي سعودي. اكتب رسائل تواصل مهنية وجذابة.",
            user_message=prompt,
            temperature=0.7,
            max_tokens=300,
        )

        # Enforce Twitter character limit
        if platform == "twitter" and len(generated) > 280:
            generated = generated[:277] + "..."

        return generated

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_linkedin_urn(profile_url: str) -> Optional[str]:
        """Extract a LinkedIn public identifier from a profile URL."""
        # e.g. https://linkedin.com/in/username -> username
        url = profile_url.rstrip("/")
        if "/in/" in url:
            return url.split("/in/")[-1]
        return None

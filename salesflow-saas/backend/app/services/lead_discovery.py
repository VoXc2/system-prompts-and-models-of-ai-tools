"""
Dealix Lead Discovery Agent - Autonomous lead finder.
Searches the web, Google Maps, social media, and directories
to find potential customers for each industry.
"""
import httpx
import json
import re
from typing import Optional
from datetime import datetime, timezone
from app.config import get_settings
from app.services.ai_brain import ai_brain

settings = get_settings()


class LeadDiscoveryAgent:
    """Autonomous agent that discovers leads from multiple sources."""

    def __init__(self, tenant_id: str, industry: str, location: str = "الرياض"):
        self.tenant_id = tenant_id
        self.industry = industry
        self.location = location
        self.discovered_leads = []

    async def run_full_discovery(self, max_leads: int = 50) -> list:
        """Run complete lead discovery across all sources."""
        # Step 1: AI generates search strategy
        strategy = await ai_brain.generate_discovery_strategy(
            self.industry, self.location,
            f"Find {max_leads} potential customers"
        )

        leads = []

        # Step 2: Search Google Maps for businesses
        google_leads = await self.search_google_maps(
            strategy.get("keywords", []),
            max_results=max_leads // 2
        )
        leads.extend(google_leads)

        # Step 3: Search social media
        social_leads = await self.search_social_media(
            strategy.get("keywords", []),
            max_results=max_leads // 4
        )
        leads.extend(social_leads)

        # Step 4: Search business directories
        directory_leads = await self.search_directories(
            strategy.get("keywords", []),
            max_results=max_leads // 4
        )
        leads.extend(directory_leads)

        # Step 5: AI qualifies and scores each lead
        qualified_leads = []
        for lead in leads:
            qualification = await ai_brain.qualify_lead(lead)
            lead["ai_score"] = qualification.get("score", 50)
            lead["ai_status"] = qualification.get("status", "new")
            lead["ai_priority"] = qualification.get("priority", "medium")
            lead["ai_next_action"] = qualification.get("next_action", "")
            qualified_leads.append(lead)

        # Sort by score (highest first)
        qualified_leads.sort(key=lambda x: x.get("ai_score", 0), reverse=True)

        self.discovered_leads = qualified_leads[:max_leads]
        return self.discovered_leads

    async def search_google_maps(self, keywords: list, max_results: int = 25) -> list:
        """Search Google Maps/Places API for businesses."""
        if not settings.GOOGLE_MAPS_API_KEY:
            return await self._search_google_maps_scrape(keywords, max_results)

        leads = []
        async with httpx.AsyncClient(timeout=30) as client:
            for keyword in keywords[:5]:
                query = f"{keyword} {self.location}"
                try:
                    response = await client.get(
                        "https://maps.googleapis.com/maps/api/place/textsearch/json",
                        params={
                            "query": query,
                            "key": settings.GOOGLE_MAPS_API_KEY,
                            "language": "ar",
                            "region": "sa",
                        },
                    )
                    data = response.json()
                    for place in data.get("results", [])[:max_results]:
                        lead = {
                            "name": place.get("name", ""),
                            "source": "google_maps",
                            "address": place.get("formatted_address", ""),
                            "rating": place.get("rating", 0),
                            "total_ratings": place.get("user_ratings_total", 0),
                            "location": place.get("geometry", {}).get("location", {}),
                            "types": place.get("types", []),
                            "industry": self.industry,
                            "city": self.location,
                            "discovered_at": datetime.now(timezone.utc).isoformat(),
                        }
                        # Get phone number from place details
                        place_id = place.get("place_id")
                        if place_id:
                            detail = await self._get_place_details(client, place_id)
                            lead["phone"] = detail.get("phone", "")
                            lead["website"] = detail.get("website", "")
                        leads.append(lead)
                except Exception:
                    continue

        return leads[:max_results]

    async def _get_place_details(self, client: httpx.AsyncClient, place_id: str) -> dict:
        """Get detailed place info including phone number."""
        try:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={
                    "place_id": place_id,
                    "fields": "formatted_phone_number,international_phone_number,website,opening_hours",
                    "key": settings.GOOGLE_MAPS_API_KEY,
                },
            )
            result = response.json().get("result", {})
            return {
                "phone": result.get("international_phone_number", ""),
                "website": result.get("website", ""),
            }
        except Exception:
            return {}

    async def _search_google_maps_scrape(self, keywords: list, max_results: int) -> list:
        """Fallback: Search using SerpAPI or similar when no Google Maps API key."""
        if not settings.SERPAPI_KEY:
            # Use AI to generate likely leads based on industry knowledge
            return await self._generate_ai_leads(keywords, max_results)

        leads = []
        async with httpx.AsyncClient(timeout=30) as client:
            for keyword in keywords[:3]:
                try:
                    response = await client.get(
                        "https://serpapi.com/search",
                        params={
                            "engine": "google_maps",
                            "q": f"{keyword} {self.location}",
                            "api_key": settings.SERPAPI_KEY,
                            "hl": "ar",
                            "ll": "@24.7136,46.6753,12z",  # Riyadh coordinates
                        },
                    )
                    data = response.json()
                    for place in data.get("local_results", [])[:max_results]:
                        leads.append({
                            "name": place.get("title", ""),
                            "source": "google_maps",
                            "phone": place.get("phone", ""),
                            "address": place.get("address", ""),
                            "rating": place.get("rating", 0),
                            "website": place.get("website", ""),
                            "industry": self.industry,
                            "city": self.location,
                            "discovered_at": datetime.now(timezone.utc).isoformat(),
                        })
                except Exception:
                    continue

        return leads[:max_results]

    async def search_social_media(self, keywords: list, max_results: int = 15) -> list:
        """Search social media platforms for potential leads."""
        leads = []

        # Search Twitter/X for businesses
        if settings.TWITTER_BEARER_TOKEN:
            twitter_leads = await self._search_twitter(keywords, max_results)
            leads.extend(twitter_leads)

        # Search Instagram business profiles
        instagram_leads = await self._search_instagram(keywords, max_results)
        leads.extend(instagram_leads)

        return leads[:max_results]

    async def _search_twitter(self, keywords: list, max_results: int) -> list:
        """Search Twitter/X for business accounts."""
        leads = []
        async with httpx.AsyncClient(timeout=30) as client:
            for keyword in keywords[:3]:
                try:
                    query = f"{keyword} {self.location} -is:retweet lang:ar"
                    response = await client.get(
                        "https://api.twitter.com/2/tweets/search/recent",
                        headers={"Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"},
                        params={
                            "query": query,
                            "max_results": 10,
                            "expansions": "author_id",
                            "user.fields": "name,username,description,location,public_metrics",
                        },
                    )
                    data = response.json()
                    users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
                    for tweet in data.get("data", []):
                        user = users.get(tweet.get("author_id", ""), {})
                        if user.get("public_metrics", {}).get("followers_count", 0) > 100:
                            leads.append({
                                "name": user.get("name", ""),
                                "source": "twitter",
                                "twitter_handle": user.get("username", ""),
                                "bio": user.get("description", ""),
                                "followers": user.get("public_metrics", {}).get("followers_count", 0),
                                "industry": self.industry,
                                "city": self.location,
                                "discovered_at": datetime.now(timezone.utc).isoformat(),
                            })
                except Exception:
                    continue

        return leads[:max_results]

    async def _search_instagram(self, keywords: list, max_results: int) -> list:
        """Search for businesses on Instagram via hashtags."""
        # Instagram requires Graph API access - use AI to identify potential leads
        leads = []
        if settings.INSTAGRAM_ACCESS_TOKEN:
            async with httpx.AsyncClient(timeout=30) as client:
                for keyword in keywords[:3]:
                    try:
                        hashtag = keyword.replace(" ", "")
                        response = await client.get(
                            f"https://graph.facebook.com/v22.0/ig_hashtag_search",
                            params={
                                "q": hashtag,
                                "user_id": settings.INSTAGRAM_USER_ID,
                                "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                            },
                        )
                        data = response.json()
                        hashtag_id = data.get("data", [{}])[0].get("id")
                        if hashtag_id:
                            media_response = await client.get(
                                f"https://graph.facebook.com/v22.0/{hashtag_id}/top_media",
                                params={
                                    "user_id": settings.INSTAGRAM_USER_ID,
                                    "fields": "caption,permalink",
                                    "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                                },
                            )
                            for media in media_response.json().get("data", [])[:max_results]:
                                caption = media.get("caption", "")
                                phone = self._extract_phone(caption)
                                if phone:
                                    leads.append({
                                        "name": caption[:50],
                                        "source": "instagram",
                                        "phone": phone,
                                        "instagram_url": media.get("permalink", ""),
                                        "industry": self.industry,
                                        "city": self.location,
                                        "discovered_at": datetime.now(timezone.utc).isoformat(),
                                    })
                    except Exception:
                        continue

        return leads[:max_results]

    async def search_directories(self, keywords: list, max_results: int = 10) -> list:
        """Search Saudi business directories."""
        leads = []

        # Use SerpAPI to search Saudi directories
        if settings.SERPAPI_KEY:
            async with httpx.AsyncClient(timeout=30) as client:
                for keyword in keywords[:3]:
                    try:
                        queries = [
                            f"{keyword} site:yellowpages.com.sa",
                            f"{keyword} {self.location} دليل",
                            f"{keyword} {self.location} أرقام تواصل",
                        ]
                        for query in queries:
                            response = await client.get(
                                "https://serpapi.com/search",
                                params={
                                    "engine": "google",
                                    "q": query,
                                    "api_key": settings.SERPAPI_KEY,
                                    "gl": "sa",
                                    "hl": "ar",
                                },
                            )
                            data = response.json()
                            for result in data.get("organic_results", [])[:5]:
                                phone = self._extract_phone(result.get("snippet", ""))
                                leads.append({
                                    "name": result.get("title", ""),
                                    "source": "directory",
                                    "website": result.get("link", ""),
                                    "phone": phone or "",
                                    "description": result.get("snippet", ""),
                                    "industry": self.industry,
                                    "city": self.location,
                                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                                })
                    except Exception:
                        continue

        return leads[:max_results]

    async def _generate_ai_leads(self, keywords: list, max_results: int) -> list:
        """Use AI to generate realistic lead profiles when APIs unavailable."""
        prompt = f"""Based on your knowledge of the {self.industry} industry in {self.location}, Saudi Arabia,
generate {max_results} realistic potential business lead profiles. For each lead include:
- name (Arabic business name)
- type (business type)
- estimated_size (small/medium/large)
- likely_needs (what they probably need)
- best_approach (how to approach them)
- priority (high/medium/low)

Return as a JSON array."""
        result = await ai_brain.think_json("You are a Saudi market research expert.", prompt)
        leads = result if isinstance(result, list) else result.get("leads", [])
        for lead in leads:
            lead["source"] = "ai_generated"
            lead["industry"] = self.industry
            lead["city"] = self.location
            lead["discovered_at"] = datetime.now(timezone.utc).isoformat()
        return leads[:max_results]

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract Saudi phone numbers from text."""
        patterns = [
            r'(?:\+966|00966|0)5\d{8}',
            r'05\d{8}',
            r'5\d{8}',
            r'(?:\+966|00966)\s?5\d[\s-]?\d{3}[\s-]?\d{4}',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = re.sub(r'[\s-]', '', match.group())
                if phone.startswith('0'):
                    phone = '966' + phone[1:]
                elif phone.startswith('5'):
                    phone = '966' + phone
                elif phone.startswith('+'):
                    phone = phone[1:]
                elif phone.startswith('00'):
                    phone = phone[2:]
                return phone
        return None


class IndustryLeadFinder:
    """Industry-specific lead discovery strategies."""

    @staticmethod
    def get_healthcare_keywords() -> list:
        return [
            "عيادات الرياض", "مستشفيات خاصة", "عيادة أسنان",
            "عيادة جلدية", "مركز طبي", "عيادة تجميل",
            "مركز علاج طبيعي", "عيادة عيون", "مركز أشعة",
            "clinic riyadh", "medical center riyadh", "dental clinic",
            "dermatology clinic", "physiotherapy center",
        ]

    @staticmethod
    def get_realestate_keywords() -> list:
        return [
            "مكتب عقار الرياض", "عقارات الرياض", "شركة عقارية",
            "مطور عقاري", "بيع شقق الرياض", "فلل للبيع الرياض",
            "أراضي للبيع", "إيجار شقق", "مكتب تأجير",
            "real estate riyadh", "property developer riyadh",
            "apartment sale riyadh", "villa riyadh",
        ]

    @staticmethod
    def get_construction_keywords() -> list:
        return [
            "مقاولات الرياض", "شركة مقاولات", "مقاولات عامة",
            "ترميم وصيانة", "تصميم داخلي الرياض", "مقاول بناء",
            "contractor riyadh", "construction company riyadh",
        ]

    @staticmethod
    def get_keywords_for_industry(industry: str) -> list:
        mapping = {
            "healthcare": IndustryLeadFinder.get_healthcare_keywords,
            "real_estate": IndustryLeadFinder.get_realestate_keywords,
            "construction": IndustryLeadFinder.get_construction_keywords,
        }
        return mapping.get(industry, lambda: [])()

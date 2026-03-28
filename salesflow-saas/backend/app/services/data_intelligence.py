"""
Dealix Data Intelligence — استخراج بيانات العملاء المحتملين من كل المصادر
Supports 15+ data sources for maximum Saudi market coverage.
"""
import httpx
import asyncio
import logging
import re
from typing import Optional
from urllib.parse import quote_plus

from app.config import get_settings
from app.utils.phone_utils import normalize_saudi_phone, is_valid_saudi_mobile

logger = logging.getLogger(__name__)

settings = get_settings()

HTTP_TIMEOUT = 15.0


class DataIntelligenceService:
    """Unified data extraction from every legitimate B2B source."""

    def __init__(self):
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=HTTP_TIMEOUT)
        return self._http_client

    async def close(self):
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    # ─── 1. Unified Search ──────────────────────────────────────────────────

    async def search_all_sources(
        self,
        query: str,
        industry: str,
        location: str,
        limit: int = 50,
    ) -> list[dict]:
        """Run all available sources in parallel, deduplicate, score, and rank."""
        tasks = []

        # Google Maps
        if settings.GOOGLE_MAPS_API_KEY:
            tasks.append(self.search_google_maps(query, location))

        # Apollo.io
        if settings.APOLLO_API_KEY:
            tasks.append(self.search_apollo(industry, location))

        # SerpAPI
        if settings.SERPAPI_KEY:
            tasks.append(self.search_serp(f"{query} {industry}", location))

        # Saudi directories
        tasks.append(self.search_saudi_directories(industry, location))

        if not tasks:
            logger.warning("No data sources configured — returning empty results")
            return []

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_prospects: list[dict] = []
        for result in results:
            if isinstance(result, Exception):
                logger.error("Source failed: %s", result)
                continue
            if isinstance(result, list):
                all_prospects.extend(result)

        # Deduplicate
        unique = self.deduplicate(all_prospects)

        # Score each prospect
        target_criteria = {
            "industry": industry,
            "location": location,
        }
        for prospect in unique:
            prospect["score"] = self.score_prospect(prospect, target_criteria)

        # Sort by score descending, limit results
        unique.sort(key=lambda p: p.get("score", 0), reverse=True)
        return unique[:limit]

    # ─── 2. Google Maps / Places ────────────────────────────────────────────

    async def search_google_maps(
        self,
        query: str,
        location: str,
        radius_km: int = 10,
    ) -> list[dict]:
        """Google Places API: nearby + text search with detail enrichment."""
        try:
            client = await self._client()
            prospects: list[dict] = []

            # Text search
            text_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": f"{query} in {location}",
                "key": settings.GOOGLE_MAPS_API_KEY,
                "language": "ar",
                "region": "sa",
            }
            resp = await client.get(text_url, params=params)
            data = resp.json()

            for place in data.get("results", [])[:20]:
                prospect = {
                    "source": "google_maps",
                    "name": place.get("name", ""),
                    "address": place.get("formatted_address", ""),
                    "rating": place.get("rating"),
                    "reviews_count": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id", ""),
                    "types": place.get("types", []),
                    "location_lat": place.get("geometry", {}).get("location", {}).get("lat"),
                    "location_lng": place.get("geometry", {}).get("location", {}).get("lng"),
                }
                prospects.append(prospect)

            # Fetch details for top 10 results
            detail_url = "https://maps.googleapis.com/maps/api/place/details/json"
            for prospect in prospects[:10]:
                if not prospect.get("place_id"):
                    continue
                try:
                    detail_params = {
                        "place_id": prospect["place_id"],
                        "fields": "formatted_phone_number,international_phone_number,website,opening_hours,photos,url",
                        "key": settings.GOOGLE_MAPS_API_KEY,
                        "language": "ar",
                    }
                    detail_resp = await client.get(detail_url, params=detail_params)
                    detail = detail_resp.json().get("result", {})

                    prospect["phone"] = detail.get("international_phone_number", "")
                    prospect["phone_local"] = detail.get("formatted_phone_number", "")
                    prospect["website"] = detail.get("website", "")
                    prospect["google_maps_url"] = detail.get("url", "")
                    prospect["opening_hours"] = detail.get("opening_hours", {}).get("weekday_text", [])

                    photos = detail.get("photos", [])
                    if photos:
                        ref = photos[0].get("photo_reference", "")
                        if ref:
                            prospect["photo_url"] = (
                                f"https://maps.googleapis.com/maps/api/place/photo"
                                f"?maxwidth=400&photoreference={ref}&key={settings.GOOGLE_MAPS_API_KEY}"
                            )
                except Exception as e:
                    logger.debug("Place details fetch failed for %s: %s", prospect.get("place_id"), e)

            logger.info("Google Maps returned %d prospects", len(prospects))
            return prospects

        except Exception as e:
            logger.error("Google Maps search failed: %s", e)
            return []

    # ─── 3. Apollo.io ───────────────────────────────────────────────────────

    async def search_apollo(
        self,
        industry: str,
        location: str,
        company_size_min: int = 10,
    ) -> list[dict]:
        """Apollo.io: organization search + people enrichment."""
        try:
            client = await self._client()
            prospects: list[dict] = []

            # Organization search
            org_url = "https://api.apollo.io/v1/mixed_companies/search"
            headers = {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "X-Api-Key": settings.APOLLO_API_KEY,
            }
            payload = {
                "q_organization_keyword_tags": [industry],
                "organization_locations": [location, "Saudi Arabia"],
                "organization_num_employees_ranges": [f"{company_size_min},"],
                "page": 1,
                "per_page": 25,
            }
            resp = await client.post(org_url, json=payload, headers=headers)
            data = resp.json()

            for org in data.get("organizations", []):
                prospect = {
                    "source": "apollo",
                    "name": org.get("name", ""),
                    "domain": org.get("primary_domain", ""),
                    "website": org.get("website_url", ""),
                    "phone": org.get("phone", ""),
                    "industry": org.get("industry", ""),
                    "employee_count": org.get("estimated_num_employees"),
                    "city": org.get("city", ""),
                    "country": org.get("country", ""),
                    "linkedin_url": org.get("linkedin_url", ""),
                    "description": org.get("short_description", ""),
                    "founded_year": org.get("founded_year"),
                    "annual_revenue": org.get("annual_revenue_printed"),
                    "apollo_id": org.get("id", ""),
                }
                prospects.append(prospect)

            # People enrichment for top companies
            people_url = "https://api.apollo.io/v1/mixed_people/search"
            for prospect in prospects[:10]:
                if not prospect.get("domain"):
                    continue
                try:
                    people_payload = {
                        "q_organization_domains": [prospect["domain"]],
                        "person_seniorities": ["owner", "founder", "c_suite", "vp", "director"],
                        "page": 1,
                        "per_page": 5,
                    }
                    people_resp = await client.post(people_url, json=people_payload, headers=headers)
                    people_data = people_resp.json()
                    contacts = []
                    for person in people_data.get("people", []):
                        contacts.append({
                            "name": person.get("name", ""),
                            "title": person.get("title", ""),
                            "email": person.get("email", ""),
                            "phone": person.get("phone_number", ""),
                            "linkedin": person.get("linkedin_url", ""),
                        })
                    if contacts:
                        prospect["decision_makers"] = contacts
                except Exception as e:
                    logger.debug("Apollo people enrichment failed for %s: %s", prospect.get("domain"), e)

            logger.info("Apollo returned %d prospects", len(prospects))
            return prospects

        except Exception as e:
            logger.error("Apollo search failed: %s", e)
            return []

    # ─── 4. Hunter.io ───────────────────────────────────────────────────────

    async def search_hunter(self, domain: str) -> dict:
        """Hunter.io: domain search for email patterns and verified emails."""
        try:
            client = await self._client()
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                "domain": domain,
                "api_key": settings.HUNTER_API_KEY,
            }
            resp = await client.get(url, params=params)
            data = resp.json().get("data", {})

            emails = []
            for email_entry in data.get("emails", []):
                emails.append({
                    "email": email_entry.get("value", ""),
                    "type": email_entry.get("type", ""),
                    "confidence": email_entry.get("confidence", 0),
                    "first_name": email_entry.get("first_name", ""),
                    "last_name": email_entry.get("last_name", ""),
                    "position": email_entry.get("position", ""),
                    "department": email_entry.get("department", ""),
                    "sources_count": len(email_entry.get("sources", [])),
                })

            result = {
                "domain": data.get("domain", domain),
                "organization": data.get("organization", ""),
                "pattern": data.get("pattern", ""),
                "emails": emails,
                "total_emails": data.get("emails_count", 0),
            }

            logger.info("Hunter found %d emails for %s", len(emails), domain)
            return result

        except Exception as e:
            logger.error("Hunter search failed for %s: %s", domain, e)
            return {"domain": domain, "emails": [], "total_emails": 0}

    # ─── 5. SerpAPI ─────────────────────────────────────────────────────────

    async def search_serp(
        self,
        query: str,
        location: str = "Saudi Arabia",
    ) -> list[dict]:
        """SerpAPI: Google search for business info and websites."""
        try:
            client = await self._client()
            url = "https://serpapi.com/search.json"
            params = {
                "q": query,
                "location": location,
                "hl": "ar",
                "gl": "sa",
                "api_key": settings.SERPAPI_KEY,
                "num": 20,
            }
            resp = await client.get(url, params=params)
            data = resp.json()

            prospects: list[dict] = []

            # Organic results
            for item in data.get("organic_results", []):
                prospect = {
                    "source": "serp",
                    "name": item.get("title", ""),
                    "website": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "domain": item.get("displayed_link", ""),
                }
                prospects.append(prospect)

            # Local results (maps pack)
            for item in data.get("local_results", []):
                prospect = {
                    "source": "serp_local",
                    "name": item.get("title", ""),
                    "address": item.get("address", ""),
                    "phone": item.get("phone", ""),
                    "rating": item.get("rating"),
                    "reviews_count": item.get("reviews"),
                    "website": item.get("website", ""),
                    "types": item.get("type", ""),
                }
                prospects.append(prospect)

            logger.info("SerpAPI returned %d results", len(prospects))
            return prospects

        except Exception as e:
            logger.error("SerpAPI search failed: %s", e)
            return []

    # ─── 6. Saudi Directories ───────────────────────────────────────────────

    async def search_saudi_directories(
        self,
        category: str,
        city: str = "الرياض",
    ) -> list[dict]:
        """Search Maroof.sa and Saudi Yellow Pages for local businesses."""
        prospects: list[dict] = []

        # Maroof.sa
        try:
            client = await self._client()
            maroof_url = f"https://maroof.sa/search?q={quote_plus(category + ' ' + city)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Dealix/1.0)",
                "Accept-Language": "ar",
            }
            resp = await client.get(maroof_url, headers=headers, follow_redirects=True)

            if resp.status_code == 200:
                text = resp.text
                # Extract business cards from Maroof search results
                # Maroof uses structured data; parse what is available
                name_pattern = re.findall(r'class="business-name[^"]*"[^>]*>([^<]+)', text)
                cr_pattern = re.findall(r'(?:سجل تجاري|CR)[:\s]*(\d{10})', text)
                phone_pattern = re.findall(r'(?:\+966|05)\d[\d\s-]{7,}', text)

                for i, name in enumerate(name_pattern[:20]):
                    prospect = {
                        "source": "maroof",
                        "name": name.strip(),
                        "cr_number": cr_pattern[i] if i < len(cr_pattern) else "",
                        "phone": phone_pattern[i].strip() if i < len(phone_pattern) else "",
                        "city": city,
                    }
                    prospects.append(prospect)

                logger.info("Maroof returned %d results for %s", len(prospects), category)

        except Exception as e:
            logger.debug("Maroof search failed: %s", e)

        # Saudi Yellow Pages
        try:
            client = await self._client()
            yp_url = "https://www.saudiyp.com/search"
            params = {
                "q": category,
                "city": city,
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Dealix/1.0)",
                "Accept-Language": "ar",
            }
            resp = await client.get(yp_url, params=params, headers=headers, follow_redirects=True)

            if resp.status_code == 200:
                text = resp.text
                name_pattern = re.findall(r'class="[^"]*listing-title[^"]*"[^>]*>([^<]+)', text)
                phone_pattern = re.findall(r'(?:\+966|05)\d[\d\s-]{7,}', text)
                addr_pattern = re.findall(r'class="[^"]*listing-address[^"]*"[^>]*>([^<]+)', text)

                for i, name in enumerate(name_pattern[:20]):
                    prospect = {
                        "source": "saudi_yp",
                        "name": name.strip(),
                        "phone": phone_pattern[i].strip() if i < len(phone_pattern) else "",
                        "address": addr_pattern[i].strip() if i < len(addr_pattern) else "",
                        "city": city,
                    }
                    prospects.append(prospect)

                logger.info("Saudi YP returned %d results for %s", len(name_pattern), category)

        except Exception as e:
            logger.debug("Saudi Yellow Pages search failed: %s", e)

        return prospects

    # ─── 7. Social Profiles ─────────────────────────────────────────────────

    async def search_social_profiles(self, company_name: str) -> dict:
        """Find Instagram, Twitter, and LinkedIn profiles for a company."""
        result: dict = {
            "instagram": {},
            "twitter": {},
            "linkedin": {},
        }
        client = await self._client()

        # Instagram Business Search
        if settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_USER_ID:
            try:
                ig_url = "https://graph.facebook.com/v18.0/ig_hashtag_search"
                params = {
                    "q": company_name.replace(" ", ""),
                    "user_id": settings.INSTAGRAM_USER_ID,
                    "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                }
                resp = await client.get(ig_url, params=params)
                data = resp.json()
                if "data" in data:
                    result["instagram"] = {
                        "found": True,
                        "hashtag_id": data["data"][0].get("id") if data["data"] else None,
                        "search_query": company_name,
                    }
            except Exception as e:
                logger.debug("Instagram search failed: %s", e)

        # Twitter / X Search
        if settings.TWITTER_BEARER_TOKEN:
            try:
                tw_url = "https://api.twitter.com/2/users/by"
                params = {"usernames": company_name.replace(" ", "")}
                headers = {"Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"}
                resp = await client.get(tw_url, params=params, headers=headers)
                data = resp.json()
                if "data" in data and data["data"]:
                    user = data["data"][0]
                    result["twitter"] = {
                        "found": True,
                        "username": user.get("username", ""),
                        "name": user.get("name", ""),
                        "id": user.get("id", ""),
                    }
            except Exception as e:
                logger.debug("Twitter search failed: %s", e)

        # LinkedIn (via SerpAPI fallback since direct API is restricted)
        if settings.SERPAPI_KEY:
            try:
                serp_url = "https://serpapi.com/search.json"
                params = {
                    "q": f"site:linkedin.com/company {company_name} Saudi Arabia",
                    "api_key": settings.SERPAPI_KEY,
                    "num": 3,
                }
                resp = await client.get(serp_url, params=params)
                data = resp.json()
                organic = data.get("organic_results", [])
                if organic:
                    link = organic[0].get("link", "")
                    if "linkedin.com/company" in link:
                        result["linkedin"] = {
                            "found": True,
                            "url": link,
                            "title": organic[0].get("title", ""),
                            "snippet": organic[0].get("snippet", ""),
                        }
            except Exception as e:
                logger.debug("LinkedIn search via SerpAPI failed: %s", e)

        return result

    # ─── 8. Website Scraping ────────────────────────────────────────────────

    async def scrape_website_info(self, url: str) -> dict:
        """Fetch a company website and extract structured info."""
        result: dict = {
            "url": url,
            "title": "",
            "description": "",
            "emails": [],
            "phones": [],
            "social_links": {},
        }

        try:
            client = await self._client()
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; Dealix/1.0)",
                "Accept-Language": "ar,en",
            }
            resp = await client.get(url, headers=headers, follow_redirects=True)

            if resp.status_code != 200:
                return result

            text = resp.text

            # Title
            title_match = re.search(r"<title[^>]*>([^<]+)</title>", text, re.IGNORECASE)
            if title_match:
                result["title"] = title_match.group(1).strip()

            # Meta description
            desc_match = re.search(
                r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)',
                text,
                re.IGNORECASE,
            )
            if desc_match:
                result["description"] = desc_match.group(1).strip()

            # Emails
            emails = set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text))
            # Filter out common non-personal emails
            result["emails"] = [
                e for e in emails
                if not any(skip in e.lower() for skip in ["example.com", "wixpress", "sentry", "webpack"])
            ]

            # Phones (Saudi format)
            phones = re.findall(r'(?:\+966|00966|05)\d[\d\s\-]{7,12}', text)
            seen_phones: set[str] = set()
            for phone in phones:
                normalized = normalize_saudi_phone(phone)
                if normalized not in seen_phones:
                    seen_phones.add(normalized)
                    result["phones"].append(normalized)

            # Social links
            social_patterns = {
                "instagram": r'https?://(?:www\.)?instagram\.com/[\w.]+',
                "twitter": r'https?://(?:www\.)?(?:twitter|x)\.com/[\w]+',
                "linkedin": r'https?://(?:www\.)?linkedin\.com/(?:company|in)/[\w-]+',
                "facebook": r'https?://(?:www\.)?facebook\.com/[\w.]+',
                "youtube": r'https?://(?:www\.)?youtube\.com/[\w@]+',
                "tiktok": r'https?://(?:www\.)?tiktok\.com/@[\w.]+',
                "snapchat": r'https?://(?:www\.)?snapchat\.com/add/[\w.]+',
            }
            for platform, pattern in social_patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result["social_links"][platform] = match.group(0)

        except Exception as e:
            logger.error("Website scrape failed for %s: %s", url, e)

        return result

    # ─── 9. Deduplication ───────────────────────────────────────────────────

    def deduplicate(self, prospects: list[dict]) -> list[dict]:
        """Remove duplicate prospects by phone, email, and fuzzy company name."""
        seen_phones: set[str] = set()
        seen_emails: set[str] = set()
        seen_names: list[str] = []
        unique: list[dict] = []

        for prospect in prospects:
            # Phone dedup
            phone = prospect.get("phone", "")
            if phone:
                normalized = normalize_saudi_phone(phone)
                if normalized in seen_phones:
                    continue
                if is_valid_saudi_mobile(normalized) or len(normalized) >= 10:
                    seen_phones.add(normalized)
                    prospect["phone"] = normalized

            # Email dedup
            email = prospect.get("email", "")
            if email:
                email_lower = email.lower().strip()
                if email_lower in seen_emails:
                    continue
                seen_emails.add(email_lower)

            # Company name fuzzy dedup (simple containment)
            name = prospect.get("name", "").strip()
            if name:
                is_duplicate = False
                name_lower = name.lower()
                for existing in seen_names:
                    if name_lower in existing or existing in name_lower:
                        is_duplicate = True
                        break
                if is_duplicate:
                    continue
                seen_names.append(name_lower)

            unique.append(prospect)

        logger.info("Deduplication: %d -> %d prospects", len(prospects), len(unique))
        return unique

    # ─── 10. Prospect Scoring ───────────────────────────────────────────────

    def score_prospect(self, prospect: dict, target_criteria: dict) -> int:
        """Score a prospect 0-100 based on data quality and relevance."""
        score = 0

        # Data completeness (up to 40 points)
        if prospect.get("name"):
            score += 5
        if prospect.get("phone"):
            score += 10
        if prospect.get("email") or prospect.get("decision_makers"):
            score += 10
        if prospect.get("website"):
            score += 5
        if prospect.get("address"):
            score += 3
        if prospect.get("description") or prospect.get("snippet"):
            score += 3
        if prospect.get("rating"):
            score += 2
        if prospect.get("social_links") or prospect.get("linkedin_url"):
            score += 2

        # Industry match (up to 20 points)
        target_industry = target_criteria.get("industry", "").lower()
        if target_industry:
            prospect_industry = (
                prospect.get("industry", "") +
                " " + prospect.get("snippet", "") +
                " " + " ".join(prospect.get("types", []))
            ).lower()
            if target_industry in prospect_industry:
                score += 20
            elif any(word in prospect_industry for word in target_industry.split()):
                score += 10

        # Location match (up to 15 points)
        target_location = target_criteria.get("location", "").lower()
        prospect_location = (
            prospect.get("city", "") +
            " " + prospect.get("address", "") +
            " " + prospect.get("country", "")
        ).lower()
        if target_location and target_location in prospect_location:
            score += 15

        # Saudi major city bonus (up to 10 points)
        major_cities = ["الرياض", "riyadh", "جدة", "jeddah", "الدمام", "dammam"]
        for city in major_cities:
            if city in prospect_location:
                score += 10
                break

        # Company size / established signals (up to 10 points)
        employee_count = prospect.get("employee_count")
        if employee_count:
            if employee_count >= 50:
                score += 10
            elif employee_count >= 10:
                score += 6
            else:
                score += 3

        reviews = prospect.get("reviews_count", 0)
        if reviews and reviews > 100:
            score += 5
        elif reviews and reviews > 20:
            score += 3

        # Decision makers available (up to 5 points)
        if prospect.get("decision_makers"):
            score += 5

        return min(score, 100)

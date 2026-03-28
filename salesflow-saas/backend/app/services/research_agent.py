"""
Dealix Research Agent — بحث عميق عن العملاء المحتملين
Deep prospect investigation for maximum sales intelligence.
"""
import httpx
import asyncio
import logging
import re
from typing import Optional

from app.config import get_settings
from app.services.data_intelligence import DataIntelligenceService
from app.services.ai_brain import AIBrain

logger = logging.getLogger(__name__)

settings = get_settings()

HTTP_TIMEOUT = 15.0


class ResearchAgent:
    """Deep research on individual companies and people."""

    def __init__(self):
        self._data_intel = DataIntelligenceService()
        self._ai_brain = AIBrain()
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=HTTP_TIMEOUT)
        return self._http_client

    async def close(self):
        await self._data_intel.close()
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    # ─── 1. Company Research ────────────────────────────────────────────────

    async def research_company(
        self,
        name: str,
        domain: Optional[str] = None,
        cr_number: Optional[str] = None,
    ) -> dict:
        """Aggregate comprehensive company profile from multiple sources."""
        profile: dict = {
            "name": name,
            "domain": domain,
            "cr_number": cr_number,
            "website_info": {},
            "news": [],
            "social_presence": {},
            "apollo_data": {},
            "tech_stack": [],
            "estimated_size": "",
        }

        tasks = {}

        # a. Website analysis
        if domain:
            url = domain if domain.startswith("http") else f"https://{domain}"
            tasks["website"] = self._data_intel.scrape_website_info(url)

        # b. Google search for news/press
        tasks["news"] = self._search_company_news(name)

        # c. Social media presence
        tasks["social"] = self._data_intel.search_social_profiles(name)

        # d. Apollo enrichment
        if settings.APOLLO_API_KEY and domain:
            tasks["apollo"] = self._apollo_company_enrich(domain)

        # e. Tech stack from website
        if domain:
            url = domain if domain.startswith("http") else f"https://{domain}"
            tasks["tech"] = self._estimate_tech_stack(url)

        # Run all in parallel
        keys = list(tasks.keys())
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for key, result in zip(keys, results):
            if isinstance(result, Exception):
                logger.debug("Research task '%s' failed for %s: %s", key, name, result)
                continue
            if key == "website":
                profile["website_info"] = result
            elif key == "news":
                profile["news"] = result
            elif key == "social":
                profile["social_presence"] = result
            elif key == "apollo":
                profile["apollo_data"] = result
            elif key == "tech":
                profile["tech_stack"] = result

        # Estimate company size from all gathered data
        profile["estimated_size"] = self.estimate_company_size(profile)

        return profile

    async def _search_company_news(self, company_name: str) -> list[dict]:
        """Search Google for recent news and press about a company."""
        if not settings.SERPAPI_KEY:
            return []

        try:
            client = await self._client()
            url = "https://serpapi.com/search.json"
            params = {
                "q": f'"{company_name}" أخبار OR news',
                "tbm": "nws",
                "hl": "ar",
                "gl": "sa",
                "api_key": settings.SERPAPI_KEY,
                "num": 10,
            }
            resp = await client.get(url, params=params)
            data = resp.json()

            news = []
            for item in data.get("news_results", []):
                news.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "source": item.get("source", {}).get("name", ""),
                    "date": item.get("date", ""),
                    "snippet": item.get("snippet", ""),
                })
            return news

        except Exception as e:
            logger.debug("News search failed for %s: %s", company_name, e)
            return []

    async def _apollo_company_enrich(self, domain: str) -> dict:
        """Enrich company data via Apollo.io."""
        try:
            client = await self._client()
            url = "https://api.apollo.io/v1/organizations/enrich"
            headers = {
                "Content-Type": "application/json",
                "X-Api-Key": settings.APOLLO_API_KEY,
            }
            params = {"domain": domain}
            resp = await client.get(url, params=params, headers=headers)
            data = resp.json().get("organization", {})

            return {
                "name": data.get("name", ""),
                "industry": data.get("industry", ""),
                "employee_count": data.get("estimated_num_employees"),
                "annual_revenue": data.get("annual_revenue_printed", ""),
                "founded_year": data.get("founded_year"),
                "description": data.get("short_description", ""),
                "technologies": data.get("current_technologies", []),
                "keywords": data.get("keywords", []),
                "linkedin_url": data.get("linkedin_url", ""),
                "phone": data.get("phone", ""),
                "city": data.get("city", ""),
                "country": data.get("country", ""),
            }

        except Exception as e:
            logger.debug("Apollo company enrich failed for %s: %s", domain, e)
            return {}

    async def _estimate_tech_stack(self, url: str) -> list[str]:
        """Estimate technology stack from website headers and content."""
        tech_signatures = {
            "WordPress": ["wp-content", "wp-includes", "wordpress"],
            "Shopify": ["shopify", "cdn.shopify"],
            "React": ["react", "_next", "__next"],
            "Vue.js": ["vue", "__vue"],
            "Laravel": ["laravel", "csrf-token"],
            "Django": ["csrfmiddlewaretoken", "django"],
            "Salla": ["salla.sa", "salla"],
            "Zid": ["zid.store", "zid"],
            "Google Analytics": ["google-analytics", "gtag", "UA-", "G-"],
            "Google Tag Manager": ["googletagmanager", "GTM-"],
            "Facebook Pixel": ["fbevents", "facebook.com/tr"],
            "HubSpot": ["hubspot", "hs-scripts"],
            "Intercom": ["intercom", "intercomSettings"],
            "Tawk.to": ["tawk.to", "tawkto"],
            "WhatsApp Widget": ["wa.me", "whatsapp"],
        }

        try:
            client = await self._client()
            headers = {"User-Agent": "Mozilla/5.0 (compatible; Dealix/1.0)"}
            resp = await client.get(url, headers=headers, follow_redirects=True)
            text = resp.text.lower()
            server = resp.headers.get("server", "").lower()

            detected: list[str] = []

            # Check server header
            if "nginx" in server:
                detected.append("Nginx")
            elif "apache" in server:
                detected.append("Apache")
            elif "cloudflare" in server:
                detected.append("Cloudflare")

            # Check HTML content for tech signatures
            for tech, signatures in tech_signatures.items():
                for sig in signatures:
                    if sig.lower() in text:
                        detected.append(tech)
                        break

            return list(set(detected))

        except Exception as e:
            logger.debug("Tech stack estimation failed for %s: %s", url, e)
            return []

    # ─── 2. Person Research ─────────────────────────────────────────────────

    async def research_person(
        self,
        name: str,
        company: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict:
        """Deep research on an individual prospect."""
        profile: dict = {
            "name": name,
            "company": company,
            "phone": phone,
            "email": email,
            "apollo_data": {},
            "linkedin": {},
            "social_presence": {},
            "professional_background": "",
            "decision_authority": "unknown",
        }

        tasks = {}

        # Apollo person lookup
        if settings.APOLLO_API_KEY:
            tasks["apollo"] = self._apollo_person_lookup(name, company, email)

        # LinkedIn via Proxycurl
        if settings.PROXYCURL_API_KEY and email:
            tasks["linkedin"] = self._proxycurl_lookup(email=email)

        # Social media search
        if company:
            tasks["social"] = self._data_intel.search_social_profiles(name)

        keys = list(tasks.keys())
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        for key, result in zip(keys, results):
            if isinstance(result, Exception):
                logger.debug("Person research '%s' failed for %s: %s", key, name, result)
                continue
            if key == "apollo":
                profile["apollo_data"] = result
                # Extract professional background from Apollo
                title = result.get("title", "")
                if title:
                    profile["professional_background"] = title
                # Assess decision authority
                profile["decision_authority"] = self._assess_authority(title)
            elif key == "linkedin":
                profile["linkedin"] = result
            elif key == "social":
                profile["social_presence"] = result

        return profile

    async def _apollo_person_lookup(
        self,
        name: str,
        company: Optional[str],
        email: Optional[str],
    ) -> dict:
        """Look up a person via Apollo.io."""
        try:
            client = await self._client()
            url = "https://api.apollo.io/v1/people/match"
            headers = {
                "Content-Type": "application/json",
                "X-Api-Key": settings.APOLLO_API_KEY,
            }
            payload: dict = {"name": name}
            if company:
                payload["organization_name"] = company
            if email:
                payload["email"] = email

            resp = await client.post(url, json=payload, headers=headers)
            person = resp.json().get("person", {})

            return {
                "name": person.get("name", ""),
                "title": person.get("title", ""),
                "email": person.get("email", ""),
                "phone": person.get("phone_number", ""),
                "linkedin_url": person.get("linkedin_url", ""),
                "city": person.get("city", ""),
                "country": person.get("country", ""),
                "company": person.get("organization", {}).get("name", ""),
                "company_industry": person.get("organization", {}).get("industry", ""),
                "seniority": person.get("seniority", ""),
                "departments": person.get("departments", []),
            }

        except Exception as e:
            logger.debug("Apollo person lookup failed for %s: %s", name, e)
            return {}

    async def _proxycurl_lookup(
        self,
        linkedin_url: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict:
        """Look up LinkedIn profile via Proxycurl."""
        try:
            client = await self._client()
            headers = {"Authorization": f"Bearer {settings.PROXYCURL_API_KEY}"}

            if linkedin_url:
                url = "https://nubela.co/proxycurl/api/v2/linkedin"
                params = {"url": linkedin_url}
            elif email:
                url = "https://nubela.co/proxycurl/api/linkedin/profile/resolve/email"
                params = {"work_email": email}
            else:
                return {}

            resp = await client.get(url, params=params, headers=headers)
            data = resp.json()

            return {
                "full_name": data.get("full_name", ""),
                "headline": data.get("headline", ""),
                "summary": data.get("summary", ""),
                "city": data.get("city", ""),
                "country": data.get("country_full_name", ""),
                "profile_url": data.get("public_identifier", ""),
                "followers": data.get("follower_count"),
                "connections": data.get("connections"),
                "experiences": [
                    {
                        "title": exp.get("title", ""),
                        "company": exp.get("company", ""),
                        "starts_at": exp.get("starts_at"),
                        "ends_at": exp.get("ends_at"),
                    }
                    for exp in (data.get("experiences", []) or [])[:5]
                ],
            }

        except Exception as e:
            logger.debug("Proxycurl lookup failed: %s", e)
            return {}

    def _assess_authority(self, title: str) -> str:
        """Assess decision-making authority from job title."""
        if not title:
            return "unknown"

        title_lower = title.lower()

        high_authority = [
            "ceo", "cto", "cfo", "cmo", "coo", "cio",
            "founder", "co-founder", "owner", "president",
            "مالك", "مؤسس", "رئيس مجلس", "الرئيس التنفيذي",
            "مدير عام", "general manager",
        ]
        medium_authority = [
            "vp", "vice president", "director", "head of",
            "مدير", "نائب", "رئيس قسم",
            "مدير المبيعات", "مدير التسويق", "مدير التقنية",
        ]
        low_authority = [
            "manager", "supervisor", "lead", "senior",
            "مشرف", "قائد فريق",
        ]

        for keyword in high_authority:
            if keyword in title_lower:
                return "high"
        for keyword in medium_authority:
            if keyword in title_lower:
                return "medium"
        for keyword in low_authority:
            if keyword in title_lower:
                return "low"

        return "unknown"

    # ─── 3. Find Decision Makers ────────────────────────────────────────────

    async def find_decision_makers(
        self,
        company_name: str,
        domain: Optional[str] = None,
    ) -> list[dict]:
        """Search for C-level, VP, and Director contacts at a company."""
        if not settings.APOLLO_API_KEY:
            logger.warning("Apollo API key not configured — cannot find decision makers")
            return []

        try:
            client = await self._client()
            url = "https://api.apollo.io/v1/mixed_people/search"
            headers = {
                "Content-Type": "application/json",
                "X-Api-Key": settings.APOLLO_API_KEY,
            }

            # Build search payload
            payload: dict = {
                "person_seniorities": ["owner", "founder", "c_suite", "vp", "director"],
                "person_titles": [
                    "CEO", "CTO", "CMO", "CFO", "COO",
                    "VP Sales", "VP Marketing", "VP Engineering",
                    "Director", "General Manager",
                    "مدير عام", "مدير المبيعات", "مدير التسويق",
                    "الرئيس التنفيذي",
                ],
                "page": 1,
                "per_page": 15,
            }

            if domain:
                payload["q_organization_domains"] = [domain]
            else:
                payload["q_organization_name"] = company_name

            resp = await client.post(url, json=payload, headers=headers)
            data = resp.json()

            decision_makers: list[dict] = []
            for person in data.get("people", []):
                dm = {
                    "name": person.get("name", ""),
                    "title": person.get("title", ""),
                    "email": person.get("email", ""),
                    "phone": person.get("phone_number", ""),
                    "linkedin": person.get("linkedin_url", ""),
                    "seniority": person.get("seniority", ""),
                    "city": person.get("city", ""),
                    "authority": self._assess_authority(person.get("title", "")),
                }
                decision_makers.append(dm)

            # Sort by authority level
            authority_order = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
            decision_makers.sort(key=lambda d: authority_order.get(d.get("authority", "unknown"), 3))

            logger.info("Found %d decision makers at %s", len(decision_makers), company_name)
            return decision_makers

        except Exception as e:
            logger.error("Decision maker search failed for %s: %s", company_name, e)
            return []

    # ─── 4. Generate Prospect Brief ─────────────────────────────────────────

    async def generate_prospect_brief(self, all_data: dict) -> str:
        """Use AI brain to generate an Arabic prospect brief with actionable insights."""
        company_name = all_data.get("name", "شركة غير محددة")
        industry = all_data.get("apollo_data", {}).get("industry", "غير محدد")
        size = all_data.get("estimated_size", "غير محدد")
        news = all_data.get("news", [])
        social = all_data.get("social_presence", {})
        tech = all_data.get("tech_stack", [])
        decision_makers = all_data.get("decision_makers", [])
        website_info = all_data.get("website_info", {})

        news_summary = ""
        if news:
            news_items = [f"- {n.get('title', '')}" for n in news[:5]]
            news_summary = "\n".join(news_items)

        social_summary_parts = []
        for platform, data in social.items():
            if isinstance(data, dict) and data.get("found"):
                social_summary_parts.append(f"- {platform}: موجود")
        social_summary = "\n".join(social_summary_parts) if social_summary_parts else "لا يوجد حضور رقمي واضح"

        dm_summary = ""
        if decision_makers:
            dm_items = [f"- {dm.get('name', '')}: {dm.get('title', '')}" for dm in decision_makers[:5]]
            dm_summary = "\n".join(dm_items)

        prompt = f"""أنت محلل مبيعات خبير في السوق السعودي. اكتب ملخص مختصر وعملي عن هذا العميل المحتمل:

الشركة: {company_name}
القطاع: {industry}
الحجم: {size}
الموقع: {website_info.get('title', 'غير متوفر')}
الوصف: {website_info.get('description', 'غير متوفر')}
التقنيات: {', '.join(tech) if tech else 'غير محدد'}

آخر الأخبار:
{news_summary or 'لا توجد أخبار حديثة'}

الحضور الرقمي:
{social_summary}

صناع القرار:
{dm_summary or 'غير محدد'}

اكتب الملخص بالعربية ويشمل:
1. نبذة سريعة عن الشركة
2. نقاط الألم المحتملة
3. أفضل طريقة للتواصل
4. نقاط حوار مقترحة
5. توصيات خاصة بالقطاع
"""

        try:
            brief = await self._ai_brain.think(
                system_prompt="أنت محلل مبيعات B2B خبير في السوق السعودي.",
                user_message=prompt,
            )
            return brief
        except Exception as e:
            logger.error("Failed to generate prospect brief: %s", e)
            return f"ملخص تلقائي: {company_name} - {industry} - حجم: {size}"

    # ─── 5. Estimate Company Size ───────────────────────────────────────────

    def estimate_company_size(self, data: dict) -> str:
        """Estimate company size from available signals."""
        # Direct employee count from Apollo
        apollo = data.get("apollo_data", {})
        employee_count = apollo.get("employee_count")

        if employee_count:
            if employee_count >= 1000:
                return "enterprise"
            elif employee_count >= 200:
                return "large"
            elif employee_count >= 50:
                return "medium"
            elif employee_count >= 10:
                return "small"
            else:
                return "startup"

        # Infer from social presence
        social = data.get("social_presence", {})
        linkedin = social.get("linkedin", {})
        instagram = social.get("instagram", {})

        # Infer from website complexity
        tech_stack = data.get("tech_stack", [])
        website_info = data.get("website_info", {})
        emails_count = len(website_info.get("emails", []))

        signals = 0

        # Multiple social platforms = larger company
        active_platforms = sum(
            1 for v in social.values()
            if isinstance(v, dict) and v.get("found")
        )
        signals += active_platforms

        # Complex tech stack
        if len(tech_stack) >= 5:
            signals += 3
        elif len(tech_stack) >= 3:
            signals += 2
        elif tech_stack:
            signals += 1

        # Multiple email addresses on website
        if emails_count >= 5:
            signals += 2
        elif emails_count >= 2:
            signals += 1

        # News coverage
        if len(data.get("news", [])) >= 3:
            signals += 2

        if signals >= 8:
            return "large"
        elif signals >= 5:
            return "medium"
        elif signals >= 3:
            return "small"
        else:
            return "startup"

    # ─── 6. Hiring Signals ──────────────────────────────────────────────────

    async def detect_hiring_signals(self, company_name: str) -> list[dict]:
        """Detect hiring activity as a growth signal (hiring = good prospect)."""
        if not settings.SERPAPI_KEY:
            logger.warning("SerpAPI key not configured — cannot detect hiring signals")
            return []

        try:
            client = await self._client()
            signals: list[dict] = []

            # Search for Arabic and English job postings
            queries = [
                f'"{company_name}" وظائف توظيف',
                f'"{company_name}" hiring jobs careers',
            ]

            for query in queries:
                try:
                    url = "https://serpapi.com/search.json"
                    params = {
                        "q": query,
                        "hl": "ar",
                        "gl": "sa",
                        "api_key": settings.SERPAPI_KEY,
                        "num": 10,
                    }
                    resp = await client.get(url, params=params)
                    data = resp.json()

                    for item in data.get("organic_results", []):
                        title = item.get("title", "")
                        snippet = item.get("snippet", "")
                        link = item.get("link", "")

                        # Filter for actual job postings
                        job_keywords = [
                            "وظيفة", "وظائف", "توظيف", "نوظف", "مطلوب",
                            "hiring", "job", "career", "vacancy", "position",
                            "linkedin.com/jobs", "bayt.com", "indeed",
                        ]
                        text_lower = (title + " " + snippet + " " + link).lower()

                        if any(kw in text_lower for kw in job_keywords):
                            signals.append({
                                "title": title,
                                "link": link,
                                "snippet": snippet,
                                "source": item.get("displayed_link", ""),
                            })
                except Exception as e:
                    logger.debug("Hiring signal search failed for query '%s': %s", query, e)

            # Deduplicate by link
            seen_links: set[str] = set()
            unique_signals: list[dict] = []
            for signal in signals:
                link = signal.get("link", "")
                if link not in seen_links:
                    seen_links.add(link)
                    unique_signals.append(signal)

            logger.info("Found %d hiring signals for %s", len(unique_signals), company_name)
            return unique_signals

        except Exception as e:
            logger.error("Hiring signal detection failed for %s: %s", company_name, e)
            return []

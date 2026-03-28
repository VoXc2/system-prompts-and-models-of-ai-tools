"""
Dealix Lead Enrichment Service - Enriches leads with company and contact
data from external sources (Apollo.io, Hunter.io, and more).
Includes Saudi-specific industry detection and lead scoring.
"""
import httpx
import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Saudi Arabia city names used for location-based scoring
SAUDI_CITIES = {
    "riyadh", "jeddah", "dammam", "mecca", "medina", "khobar", "dhahran",
    "tabuk", "abha", "taif", "hail", "jubail", "yanbu", "najran", "jazan",
    "الرياض", "جدة", "الدمام", "مكة", "المدينة", "الخبر", "الظهران",
    "تبوك", "أبها", "الطائف", "حائل", "الجبيل", "ينبع", "نجران", "جازان",
}

# Industry keywords for Saudi market detection
INDUSTRY_KEYWORDS = {
    "healthcare": {
        "en": ["hospital", "clinic", "medical", "health", "pharmaceutical", "pharma",
               "dental", "laboratory", "diagnostics", "biotech", "wellness"],
        "ar": ["مستشفى", "عيادة", "طبي", "صحة", "صيدلانية", "أسنان", "مختبر"],
    },
    "real_estate": {
        "en": ["real estate", "property", "realty", "housing", "residential",
               "commercial property", "land", "development", "mortgage", "broker"],
        "ar": ["عقارات", "عقار", "إسكان", "تطوير عقاري", "أراضي", "سكني"],
    },
    "construction": {
        "en": ["construction", "building", "contracting", "engineering", "infrastructure",
               "architecture", "cement", "steel", "concrete", "contractor"],
        "ar": ["مقاولات", "بناء", "تشييد", "هندسة", "بنية تحتية", "إنشاءات"],
    },
    "retail": {
        "en": ["retail", "store", "shop", "ecommerce", "e-commerce", "marketplace",
               "wholesale", "supermarket", "mall", "consumer goods", "fashion"],
        "ar": ["تجزئة", "متجر", "تجارة إلكترونية", "سوق", "جملة", "مول"],
    },
    "fnb": {
        "en": ["restaurant", "food", "beverage", "catering", "cafe", "coffee",
               "bakery", "dining", "hospitality", "hotel", "kitchen", "f&b"],
        "ar": ["مطعم", "أغذية", "مشروبات", "تموين", "مقهى", "ضيافة", "فندق"],
    },
    "education": {
        "en": ["education", "school", "university", "college", "training", "academy",
               "institute", "learning", "edtech", "tutoring", "e-learning"],
        "ar": ["تعليم", "مدرسة", "جامعة", "كلية", "تدريب", "أكاديمية", "معهد"],
    },
}


class LeadEnrichmentService:
    """Enriches lead records with company and contact data from external APIs."""

    def __init__(self):
        self.apollo_api_key = settings.APOLLO_API_KEY
        self.hunter_api_key = settings.HUNTER_API_KEY
        self.http_timeout = 15.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def enrich_lead(self, lead_data: dict) -> dict:
        """Main enrichment pipeline. Merges data from all available sources
        and appends a lead score.

        Args:
            lead_data: Raw lead dict, expected keys include any of
                       email, domain, company_name, phone, location.

        Returns:
            The enriched lead dict with additional fields.
        """
        enriched = dict(lead_data)

        email = lead_data.get("email", "")
        domain = lead_data.get("domain", "")
        company_name = lead_data.get("company_name", "")

        # Derive domain from email when not explicitly provided
        if not domain and email and "@" in email:
            domain = email.split("@")[1]

        # Step 1: Apollo enrichment (company + contact)
        if email or domain:
            apollo_data = await self._enrich_from_apollo(email or domain)
            if apollo_data:
                enriched.setdefault("company", {})
                enriched["company"].update(apollo_data.get("company", {}))
                enriched.update({
                    k: v for k, v in apollo_data.items()
                    if k != "company" and v
                })
                # Backfill company_name if we got one from Apollo
                if not company_name:
                    company_name = enriched.get("company", {}).get("name", "")

        # Step 2: Hunter enrichment (email patterns / verification)
        if domain:
            hunter_data = await self._enrich_from_hunter(domain)
            if hunter_data:
                enriched.setdefault("email_info", {})
                enriched["email_info"].update(hunter_data)

        # Step 3: Basic company info fallback
        if company_name and not enriched.get("company", {}).get("description"):
            company_info = await self._enrich_company_info(company_name)
            if company_info:
                enriched.setdefault("company", {})
                enriched["company"].update(company_info)

        # Step 4: Industry detection
        company_data = enriched.get("company", {})
        if company_data and not enriched.get("industry"):
            enriched["industry"] = self._detect_industry(company_data)

        # Step 5: Lead scoring
        enriched["lead_score"] = self._calculate_lead_score(enriched)
        enriched["enrichment_status"] = "completed"

        return enriched

    # ------------------------------------------------------------------
    # Apollo.io
    # ------------------------------------------------------------------

    async def _enrich_from_apollo(self, email_or_domain: str) -> dict:
        """Fetch company and contact data from the Apollo.io API.

        Args:
            email_or_domain: An email address or a bare domain name.

        Returns:
            Dict with ``company`` and top-level contact fields, or empty
            dict on failure.
        """
        if not self.apollo_api_key:
            logger.debug("Apollo API key not configured, skipping enrichment")
            return {}

        url = "https://api.apollo.io/v1/people/match"
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

        # Apollo accepts either an email or a domain for matching
        payload: dict = {"api_key": self.apollo_api_key}
        if "@" in email_or_domain:
            payload["email"] = email_or_domain
        else:
            payload["domain"] = email_or_domain

        try:
            async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()

            person = data.get("person", {})
            org = person.get("organization", {})

            result: dict = {}
            if person:
                result.update({
                    "first_name": person.get("first_name", ""),
                    "last_name": person.get("last_name", ""),
                    "title": person.get("title", ""),
                    "linkedin_url": person.get("linkedin_url", ""),
                    "email_verified": bool(person.get("email_status") == "verified"),
                })

            if org:
                result["company"] = {
                    "name": org.get("name", ""),
                    "domain": org.get("primary_domain", ""),
                    "description": org.get("short_description", ""),
                    "industry": org.get("industry", ""),
                    "employee_count": org.get("estimated_num_employees"),
                    "annual_revenue": org.get("annual_revenue_printed", ""),
                    "location": org.get("raw_address", ""),
                    "country": org.get("country", ""),
                    "city": org.get("city", ""),
                    "logo_url": org.get("logo_url", ""),
                    "founded_year": org.get("founded_year"),
                    "phone": org.get("phone", ""),
                    "linkedin_url": org.get("linkedin_url", ""),
                }

            return result

        except httpx.HTTPStatusError as exc:
            logger.warning("Apollo API HTTP error %s: %s", exc.response.status_code, exc)
        except httpx.RequestError as exc:
            logger.warning("Apollo API request failed: %s", exc)
        except Exception as exc:
            logger.error("Unexpected error during Apollo enrichment: %s", exc)

        return {}

    # ------------------------------------------------------------------
    # Hunter.io
    # ------------------------------------------------------------------

    async def _enrich_from_hunter(self, domain: str) -> dict:
        """Retrieve email pattern and verification data from Hunter.io.

        Args:
            domain: Company domain (e.g. ``example.com``).

        Returns:
            Dict with email pattern, sources count, and sample emails,
            or empty dict on failure.
        """
        if not self.hunter_api_key:
            logger.debug("Hunter API key not configured, skipping enrichment")
            return {}

        url = "https://api.hunter.io/v2/domain-search"
        params = {
            "domain": domain,
            "api_key": self.hunter_api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json().get("data", {})

            emails = data.get("emails", [])
            return {
                "domain": domain,
                "organization": data.get("organization", ""),
                "email_pattern": data.get("pattern", ""),
                "total_sources": data.get("sources", 0),
                "webmail": data.get("webmail", False),
                "disposable": data.get("disposable", False),
                "sample_emails": [
                    {
                        "email": e.get("value", ""),
                        "type": e.get("type", ""),
                        "confidence": e.get("confidence", 0),
                        "first_name": e.get("first_name", ""),
                        "last_name": e.get("last_name", ""),
                        "position": e.get("position", ""),
                    }
                    for e in emails[:5]
                ],
            }

        except httpx.HTTPStatusError as exc:
            logger.warning("Hunter API HTTP error %s: %s", exc.response.status_code, exc)
        except httpx.RequestError as exc:
            logger.warning("Hunter API request failed: %s", exc)
        except Exception as exc:
            logger.error("Unexpected error during Hunter enrichment: %s", exc)

        return {}

    # ------------------------------------------------------------------
    # Basic company info (Clearbit-style fallback via logo + domain)
    # ------------------------------------------------------------------

    async def _enrich_company_info(self, company_name: str) -> dict:
        """Best-effort company info lookup using the Autocomplete API
        on Apollo when a full match was not found earlier.

        Args:
            company_name: Human-readable company name.

        Returns:
            Dict with basic company metadata or empty dict.
        """
        if not self.apollo_api_key:
            return {}

        url = "https://api.apollo.io/v1/organizations/enrich"
        payload = {
            "api_key": self.apollo_api_key,
            "domain": None,
            "name": company_name,
        }

        try:
            async with httpx.AsyncClient(timeout=self.http_timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                org = resp.json().get("organization", {})

            if not org:
                return {}

            return {
                "name": org.get("name", company_name),
                "domain": org.get("primary_domain", ""),
                "description": org.get("short_description", ""),
                "industry": org.get("industry", ""),
                "employee_count": org.get("estimated_num_employees"),
                "annual_revenue": org.get("annual_revenue_printed", ""),
                "location": org.get("raw_address", ""),
                "country": org.get("country", ""),
                "city": org.get("city", ""),
                "logo_url": org.get("logo_url", ""),
                "founded_year": org.get("founded_year"),
            }

        except Exception as exc:
            logger.warning("Company info enrichment failed for '%s': %s", company_name, exc)

        return {}

    # ------------------------------------------------------------------
    # Lead scoring
    # ------------------------------------------------------------------

    def _calculate_lead_score(self, lead_data: dict) -> int:
        """Score a lead from 0-100 based on enriched data quality and fit.

        Scoring weights:
            - Company size         : up to 25 pts
            - Industry match       : up to 20 pts
            - Location (Saudi)     : up to 15 pts
            - Email verified       : up to 15 pts
            - Phone available      : up to 10 pts
            - LinkedIn available   : up to  5 pts
            - Company description  : up to  5 pts
            - Job title present    : up to  5 pts

        Args:
            lead_data: The enriched lead dict.

        Returns:
            Integer score between 0 and 100.
        """
        score = 0
        company = lead_data.get("company", {})

        # --- Company size (max 25) ---
        employee_count = company.get("employee_count") or 0
        if employee_count >= 1000:
            score += 25
        elif employee_count >= 200:
            score += 20
        elif employee_count >= 50:
            score += 15
        elif employee_count >= 10:
            score += 10
        elif employee_count > 0:
            score += 5

        # --- Industry match (max 20) ---
        industry = (
            lead_data.get("industry", "")
            or company.get("industry", "")
        )
        if industry:
            # Known Saudi-priority industries get full points
            priority_industries = {
                "healthcare", "real_estate", "construction",
                "retail", "fnb", "education",
            }
            if industry.lower().replace(" ", "_") in priority_industries:
                score += 20
            else:
                score += 10  # recognised but not priority

        # --- Location / Saudi bonus (max 15) ---
        location_fields = [
            company.get("country", ""),
            company.get("city", ""),
            company.get("location", ""),
            lead_data.get("location", ""),
        ]
        location_text = " ".join(f.lower() for f in location_fields if f)
        is_saudi = (
            "saudi" in location_text
            or "ksa" in location_text
            or "السعودية" in location_text
            or any(city in location_text for city in SAUDI_CITIES)
        )
        if is_saudi:
            score += 15
        elif location_text.strip():
            score += 5  # at least we know where they are

        # --- Email verified (max 15) ---
        if lead_data.get("email_verified"):
            score += 15
        elif lead_data.get("email"):
            score += 7

        # --- Phone available (max 10) ---
        phone = (
            lead_data.get("phone", "")
            or company.get("phone", "")
        )
        if phone:
            score += 10

        # --- LinkedIn available (max 5) ---
        if lead_data.get("linkedin_url") or company.get("linkedin_url"):
            score += 5

        # --- Company description (max 5) ---
        if company.get("description"):
            score += 5

        # --- Job title (max 5) ---
        if lead_data.get("title"):
            score += 5

        return min(score, 100)

    # ------------------------------------------------------------------
    # Industry detection
    # ------------------------------------------------------------------

    def _detect_industry(self, company_data: dict) -> str:
        """Auto-detect industry from company metadata using keyword matching.

        Checks the company name, description, and any existing industry
        field against Saudi-market-relevant industry keyword lists.

        Args:
            company_data: Dict with company fields (name, description,
                          industry, etc.).

        Returns:
            Detected industry key (e.g. ``"healthcare"``, ``"fnb"``),
            or ``"other"`` if no match is found.
        """
        searchable_text = " ".join([
            company_data.get("name", ""),
            company_data.get("description", ""),
            company_data.get("industry", ""),
        ]).lower()

        if not searchable_text.strip():
            return "other"

        best_match: Optional[str] = None
        best_hits = 0

        for industry_key, keyword_sets in INDUSTRY_KEYWORDS.items():
            hits = 0
            for kw in keyword_sets.get("en", []):
                if kw in searchable_text:
                    hits += 1
            for kw in keyword_sets.get("ar", []):
                if kw in searchable_text:
                    hits += 1

            if hits > best_hits:
                best_hits = hits
                best_match = industry_key

        return best_match if best_match else "other"


# Module-level singleton for convenience
lead_enrichment_service = LeadEnrichmentService()

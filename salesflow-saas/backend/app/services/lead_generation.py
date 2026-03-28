"""
Dealix Legitimate Lead Generation Service.
Uses official B2B APIs (Apollo, Hunter) and inbound channels (Meta CTWA, forms).
NO web scraping or bot farms.
"""
import httpx
from typing import Optional
from datetime import datetime, timezone
from app.config import get_settings

settings = get_settings()


class ApolloIntegration:
    """Apollo.io B2B contact database integration."""

    BASE_URL = "https://api.apollo.io/v1"

    def __init__(self):
        self.api_key = settings.APOLLO_API_KEY

    async def search_companies(
        self, industry: str, location: str = "Saudi Arabia",
        city: str = "Riyadh", limit: int = 25
    ) -> list:
        """Search for companies matching criteria."""
        if not self.api_key:
            return []

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.BASE_URL}/mixed_companies/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": self.api_key,
                    "q_organization_keyword_tags": [industry],
                    "organization_locations": [location],
                    "organization_not_locations": [],
                    "per_page": limit,
                },
            )
            if response.status_code != 200:
                return []
            data = response.json()
            return [
                {
                    "name": org.get("name", ""),
                    "domain": org.get("primary_domain", ""),
                    "phone": org.get("phone", ""),
                    "industry": org.get("industry", ""),
                    "city": city,
                    "employees": org.get("estimated_num_employees", 0),
                    "source": "apollo",
                    "apollo_id": org.get("id", ""),
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                }
                for org in data.get("organizations", [])
            ]

    async def search_people(
        self, title: str = "owner", industry: str = "",
        location: str = "Saudi Arabia", limit: int = 25
    ) -> list:
        """Search for decision makers at companies."""
        if not self.api_key:
            return []

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.BASE_URL}/mixed_people/search",
                headers={"Content-Type": "application/json"},
                json={
                    "api_key": self.api_key,
                    "person_titles": [title],
                    "q_organization_keyword_tags": [industry] if industry else [],
                    "person_locations": [location],
                    "per_page": limit,
                },
            )
            if response.status_code != 200:
                return []
            data = response.json()
            return [
                {
                    "name": p.get("name", ""),
                    "email": p.get("email", ""),
                    "phone": p.get("phone_numbers", [{}])[0].get("sanitized_number", "") if p.get("phone_numbers") else "",
                    "title": p.get("title", ""),
                    "company": p.get("organization", {}).get("name", ""),
                    "linkedin_url": p.get("linkedin_url", ""),
                    "source": "apollo",
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                }
                for p in data.get("people", [])
            ]


class HunterIntegration:
    """Hunter.io email finding and verification."""

    BASE_URL = "https://api.hunter.io/v2"

    def __init__(self):
        self.api_key = settings.HUNTER_API_KEY

    async def find_emails(self, domain: str) -> list:
        """Find email addresses for a company domain."""
        if not self.api_key or not domain:
            return []

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.BASE_URL}/domain-search",
                params={"domain": domain, "api_key": self.api_key},
            )
            if response.status_code != 200:
                return []
            data = response.json()
            return [
                {
                    "email": e.get("value", ""),
                    "first_name": e.get("first_name", ""),
                    "last_name": e.get("last_name", ""),
                    "position": e.get("position", ""),
                    "confidence": e.get("confidence", 0),
                    "source": "hunter",
                }
                for e in data.get("data", {}).get("emails", [])
            ]

    async def verify_email(self, email: str) -> dict:
        """Verify if an email address is valid."""
        if not self.api_key:
            return {"status": "unknown"}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.BASE_URL}/email-verifier",
                params={"email": email, "api_key": self.api_key},
            )
            if response.status_code != 200:
                return {"status": "unknown"}
            data = response.json().get("data", {})
            return {
                "status": data.get("status", "unknown"),
                "score": data.get("score", 0),
                "disposable": data.get("disposable", False),
            }


class FormLeadCapture:
    """Process inbound leads from web forms, CTWA ads, etc."""

    @staticmethod
    def process_web_form(data: dict) -> dict:
        """Process a web form submission into a lead."""
        return {
            "name": data.get("name", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "company_name": data.get("company", ""),
            "industry": data.get("industry", ""),
            "team_size": data.get("team_size", ""),
            "source": "web_form",
            "utm_source": data.get("utm_source", ""),
            "utm_medium": data.get("utm_medium", ""),
            "utm_campaign": data.get("utm_campaign", ""),
            "consent_given": True,
            "consent_source": "web_form",
        }

    @staticmethod
    def process_ctwa_lead(data: dict) -> dict:
        """Process a Click-to-WhatsApp ad lead."""
        return {
            "name": data.get("contact_name", ""),
            "phone": data.get("wa_id", ""),
            "source": "meta_ctwa",
            "ad_id": data.get("ad_id", ""),
            "campaign_id": data.get("campaign_id", ""),
            "consent_given": True,
            "consent_source": "ctwa_ad",
        }


class LeadGenerationOrchestrator:
    """Orchestrates lead generation from all legitimate sources."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.apollo = ApolloIntegration()
        self.hunter = HunterIntegration()

    async def find_companies(self, industry: str, city: str = "Riyadh", limit: int = 25) -> list:
        """Find companies from Apollo."""
        return await self.apollo.search_companies(industry, city=city, limit=limit)

    async def find_decision_makers(self, industry: str, title: str = "owner", limit: int = 25) -> list:
        """Find decision makers from Apollo."""
        return await self.apollo.search_people(title=title, industry=industry, limit=limit)

    async def enrich_lead(self, domain: str = None, email: str = None) -> dict:
        """Enrich a lead with additional data."""
        result = {"emails": [], "verified": None}
        if domain:
            result["emails"] = await self.hunter.find_emails(domain)
        if email:
            result["verified"] = await self.hunter.verify_email(email)
        return result

"""Enrichment Agent — adds structured data to a company profile from allowed sources."""
from dealix_gtm_os.agents.base_agent import BaseAgent


class EnrichmentAgent(BaseAgent):
    name = "enrichment"
    description = "Enriches company data from website and public sources"

    async def run(self, input_data: dict) -> dict:
        company = input_data.get("name", "")
        website = input_data.get("website", "")
        email = input_data.get("email", "")
        sector = input_data.get("sector", "")

        enriched = {
            "company": company,
            "website_found": bool(website),
            "email_found": bool(email),
            "sector_confirmed": sector if sector else "unknown",
            "social_links": {},
            "contact_page": f"{website}/contact" if website else None,
            "has_whatsapp": None,
            "has_forms": None,
            "employee_estimate": None,
            "enrichment_source": "mock",
            "note": "Connect website fetcher + Tavily for live enrichment",
        }

        if website:
            enriched["social_links"] = {
                "linkedin": f"Search: {company} LinkedIn",
                "instagram": f"Search: {company} Instagram",
                "twitter": f"Search: {company} Twitter",
            }

        return enriched

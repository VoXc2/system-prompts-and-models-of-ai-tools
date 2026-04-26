"""Web Search Agent — searches allowed web sources for company intelligence."""
import json
from dealix_gtm_os.agents.base_agent import BaseAgent


class WebSearchAgent(BaseAgent):
    name = "web_search"
    description = "Searches the web for company information using allowed sources"

    async def run(self, input_data: dict) -> dict:
        company = input_data.get("name", "")
        website = input_data.get("website", "")
        city = input_data.get("city", "")

        queries = []
        if company:
            queries.append(f"{company} خدمات")
            queries.append(f"{company} {city}" if city else company)
        if website:
            queries.append(f"site:{website}")

        return {
            "company": company,
            "queries_generated": queries,
            "sources_checked": [
                "google_programmable_search",
                "company_website",
                "public_directories",
            ],
            "results": [],
            "provider": "mock",
            "note": "Connect Tavily or Google Search API key to enable live search",
        }

import json
from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.agents.llm_client import call_llm
from dealix_gtm_os.models.company import CompanyInput, CompanyIntelligence

class CompanyResearchAgent(BaseAgent):
    name = "company_research"
    description = "Understands a company from available data"

    async def run(self, input_data: dict) -> dict:
        company = CompanyInput(**input_data)
        result_json = await call_llm(
            f"Analyze company: {company.name}, sector: {company.sector}, city: {company.city}",
            context={"sector": company.sector or ""}
        )
        data = json.loads(result_json)
        intel = CompanyIntelligence(
            name=company.name,
            website=company.website,
            sector=company.sector or data.get("sector", "unknown"),
            city=company.city or "",
            confidence=0.7,
            **{k: v for k, v in data.items() if k in CompanyIntelligence.model_fields}
        )
        return intel.model_dump()

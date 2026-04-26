from dealix_gtm_os.agents.base_agent import BaseAgent

class EnrichmentAgentAgent(BaseAgent):
    name = "enrichment_agent"
    description = "enrichment agent"

    async def run(self, input_data: dict) -> dict:
        return {"status": "stub", "agent": self.name, "note": "Connect real tools in production"}

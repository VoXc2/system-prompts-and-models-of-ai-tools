from dealix_gtm_os.agents.base_agent import BaseAgent

class CompetitorIntelligenceAgentAgent(BaseAgent):
    name = "competitor_intelligence_agent"
    description = "competitor intelligence agent"

    async def run(self, input_data: dict) -> dict:
        return {"status": "stub", "agent": self.name, "note": "Connect real tools in production"}

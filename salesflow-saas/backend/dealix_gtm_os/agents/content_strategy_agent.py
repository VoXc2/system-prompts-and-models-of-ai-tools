from dealix_gtm_os.agents.base_agent import BaseAgent

class ContentStrategyAgentAgent(BaseAgent):
    name = "content_strategy_agent"
    description = "content strategy agent"

    async def run(self, input_data: dict) -> dict:
        return {"status": "stub", "agent": self.name, "note": "Connect real tools in production"}

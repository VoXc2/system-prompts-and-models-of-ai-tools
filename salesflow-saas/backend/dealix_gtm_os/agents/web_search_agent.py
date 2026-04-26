from dealix_gtm_os.agents.base_agent import BaseAgent

class WebSearchAgentAgent(BaseAgent):
    name = "web_search_agent"
    description = "web search agent"

    async def run(self, input_data: dict) -> dict:
        return {"status": "stub", "agent": self.name, "note": "Connect real tools in production"}

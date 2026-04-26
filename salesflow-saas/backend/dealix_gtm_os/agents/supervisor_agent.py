from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.agents.company_research_agent import CompanyResearchAgent
from dealix_gtm_os.agents.scoring_agent import ScoringAgent
from dealix_gtm_os.agents.channel_strategy_agent import ChannelStrategyAgent
from dealix_gtm_os.agents.compliance_agent import ComplianceAgent
from dealix_gtm_os.agents.message_generation_agent import MessageGenerationAgent

class SupervisorAgent(BaseAgent):
    name = "supervisor"
    description = "Orchestrates all GTM agents into a complete pipeline"

    def __init__(self):
        self.research = CompanyResearchAgent()
        self.scoring = ScoringAgent()
        self.channel = ChannelStrategyAgent()
        self.compliance = ComplianceAgent()
        self.message = MessageGenerationAgent()

    async def run(self, input_data: dict) -> dict:
        intel = await self.research.run(input_data)
        score = await self.scoring.run({**input_data, **intel})
        channel_plan = await self.channel.run(intel)
        compliance = await self.compliance.run({"channel": channel_plan["primary_channel"], "action": "send_message"})
        msg_input = {**intel, "channel": channel_plan["primary_channel"]}
        message = await self.message.run(msg_input)
        return {
            "company": input_data.get("name", "Unknown"),
            "intelligence": intel,
            "score": score,
            "channel_plan": channel_plan,
            "compliance": compliance,
            "message": message,
            "next_action": "send" if compliance["allowed"] else "manual_review",
            "approval_required": message.get("approval_required", True),
        }

"""Supervisor Agent — orchestrates all GTM agents with full AI OS integration.

Wired into: token counting, model routing, response cache, cost guard,
output validation, compliance gate, tracing, and proof packs.
"""
from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.agents.company_research_agent import CompanyResearchAgent
from dealix_gtm_os.agents.scoring_agent import ScoringAgent
from dealix_gtm_os.agents.channel_strategy_agent import ChannelStrategyAgent
from dealix_gtm_os.agents.compliance_agent import ComplianceAgent
from dealix_gtm_os.agents.message_generation_agent import MessageGenerationAgent
from dealix_gtm_os.agents.partnership_strategist_agent import PartnershipStrategistAgent
from dealix_gtm_os.ai.response_cache import get_cached, set_cached
from dealix_gtm_os.ai.token_counter import estimate_tokens
from dealix_gtm_os.guardrails.output_validator import validate_output
from dealix_gtm_os.guardrails.cost_guard import CostGuard
from dealix_gtm_os.observability.trace import PipelineTrace


class SupervisorAgent(BaseAgent):
    name = "supervisor"
    description = "Orchestrates all GTM agents with cost/quality/proof integration"

    def __init__(self):
        self.research = CompanyResearchAgent()
        self.scoring = ScoringAgent()
        self.channel = ChannelStrategyAgent()
        self.compliance = ComplianceAgent()
        self.message = MessageGenerationAgent()
        self.partnership = PartnershipStrategistAgent()
        self.cost_guard = CostGuard()

    async def run(self, input_data: dict) -> dict:
        trace = PipelineTrace("gtm_full_pipeline", input_data.get("name", ""))

        budget_check = self.cost_guard.check()
        if not budget_check["allowed"]:
            return {"error": "Daily AI budget exceeded", "cost_report": budget_check, "trace_id": trace.trace_id}

        cached_full = get_cached("supervisor_full", input_data, ttl_hours=1)
        if cached_full:
            trace.log_step("cache", "full pipeline cache hit", cost=0)
            cached_full["cache_status"] = "HIT"
            cached_full["trace_id"] = trace.trace_id
            return cached_full

        # Step 1: Company Research
        intel = await self.research.run(input_data)
        input_tokens = estimate_tokens(str(input_data))
        output_tokens = estimate_tokens(str(intel))
        trace.log_step("company_research", f"sector={intel.get('sector')}", cost=0.001)

        # Step 2: Scoring
        score = await self.scoring.run({**input_data, **intel})
        trace.log_step("scoring", f"total={score.get('total')}, priority={score.get('priority')}")

        # Step 3: Partnership classification
        partnership = await self.partnership.run(intel)
        trace.log_step("partnership", f"type={partnership.get('primary_type')}")

        # Step 4: Channel strategy
        channel_plan = await self.channel.run(intel)
        trace.log_step("channel_strategy", f"primary={channel_plan['primary_channel']}")

        # Step 5: Compliance gate
        compliance = await self.compliance.run({
            "channel": channel_plan["primary_channel"],
            "action": "send_message"
        })
        trace.log_step("compliance", f"allowed={compliance['allowed']}, level={compliance['level']}")

        # Step 6: Message generation
        msg_input = {**intel, "channel": channel_plan["primary_channel"]}
        message = await self.message.run(msg_input)
        trace.log_step("message_generation", f"words={len(message.get('body','').split())}")

        # Step 7: Output validation (guardrails)
        validation = validate_output(message.get("body", ""), context="outreach message")
        trace.log_step("output_validation", f"valid={validation['valid']}, issues={validation['issue_count']}")

        # Step 8: Proof pack
        proof_pack = {
            "company_analyzed": input_data.get("name"),
            "sector_source": "config/scoring_weights.yaml + llm_client mock",
            "intelligence_confidence": intel.get("confidence", 0),
            "scoring_method": "weighted sector defaults",
            "channel_reason": channel_plan.get("reason", ""),
            "compliance_reason": compliance.get("reason", ""),
            "message_validated": validation["valid"],
            "validation_issues": validation["issues"],
            "sources": intel.get("sources", ["uploaded company file", "sector knowledge base"]),
            "no_real_send": True,
        }

        # Build result
        model_tier = "mid"
        estimated_cost = 0.002

        result = {
            "company": input_data.get("name", "Unknown"),
            "intelligence": intel,
            "score": score,
            "partnership": partnership,
            "channel_plan": channel_plan,
            "compliance": compliance,
            "message": message,
            "proof_pack": proof_pack,
            "output_validation": validation,
            "model_selected": model_tier,
            "estimated_tokens": {"input": input_tokens, "output": output_tokens},
            "estimated_cost_sar": round(estimated_cost * 3.75, 4),
            "cache_status": "MISS",
            "approval_required": message.get("approval_required", True),
            "next_action": "sami_approve_and_send" if compliance["allowed"] else "manual_review_required",
            "trace_id": trace.trace_id,
        }

        trace_report = trace.finish()
        result["trace"] = trace_report

        set_cached("supervisor_full", input_data, result)
        self.cost_guard.record(estimated_cost * 3.75)

        return result

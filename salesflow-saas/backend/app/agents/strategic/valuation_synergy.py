"""
Valuation & Synergy Agent — Layer 8
═══════════════════════════════════
Estimates fair value via DCF + multiples, calculates revenue/cost synergies.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent, AgentPriority

SYSTEM_PROMPT = """أنت محلل التقييم والتآزر في Dealix. مهمتك:
1. تقدير القيمة العادلة بطريقتين (DCF + مضاعفات السوق)
2. حساب عوائد التآزر (إيرادات + تكاليف)
3. تقدير تكاليف التكامل
4. تحديد نطاق العرض الموصى به

رد بـ JSON:
{
  "valuation": {
    "dcf_sar": 0, "multiples_sar": 0, "average_sar": 0,
    "assumptions": {"discount_rate": 0.12, "growth_rate": 0.08, "multiple": 5}
  },
  "synergies": {
    "revenue_synergy_sar": 0, "cost_synergy_sar": 0,
    "net_synergy_sar": 0, "realization_months": 18
  },
  "integration_cost_sar": 0,
  "recommended_offer": {"min_sar": 0, "max_sar": 0, "sweet_spot_sar": 0},
  "payback_months": 0,
  "irr_percent": 0,
  "summary_ar": "..."
}"""


class ValuationSynergyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="valuation_synergy",
            name_ar="محلل التقييم والتآزر",
            layer=8,
            description="يقدّر القيمة العادلة + عوائد التآزر (Revenue/Cost Synergies)",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, MAEvent, MAEventType,
            RiskLevel, ApprovalLevel,
        )

        target = task.get("target", {})
        dd = task.get("dd_results", {})
        tenant_id = task.get("tenant_id")
        company = target.get("name", "غير محدد")

        prompt = f"""قيّم شركة {company}:
القطاع: {target.get('industry', '')}
الإيرادات: {target.get('revenue_sar', 0):,.0f} ريال
نتائج DD: درجة إجمالية {dd.get('overall_dd_score', 0)}/100
مجالات التآزر: {target.get('synergy_areas', [])}

احسب DCF + مضاعفات + تآزر إيرادات/تكاليف + نطاق العرض."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")
        avg_val = result.get("valuation", {}).get("average_sar", 0)

        bus = get_strategic_event_bus()
        event = MAEvent(
            tenant_id=tenant_id,
            event_type=MAEventType.VALUATION_READY.value,
            agent_name=self.name,
            confidence=0.75,
            target_company=company,
            estimated_valuation_sar=avg_val,
            synergy_estimate_sar=result.get("synergies", {}).get("net_synergy_sar", 0),
            risk_level=RiskLevel.HIGH,
            requires_approval=True,
            approval_level=ApprovalLevel.CXOO,
            payload=result,
        )
        await bus.publish(event)

        self.send_message(
            "executive_negotiator", "prepare_negotiation",
            {"target": target, "valuation": result, "tenant_id": str(tenant_id)},
            AgentPriority.HIGH,
        )

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "valuation_sar": avg_val, "event_id": str(event.id), "data": result}

    def get_capabilities(self) -> List[str]:
        return ["dcf_valuation", "multiples_valuation", "synergy_analysis", "offer_range_calculation"]

    async def handle_message(self, message):
        if message.action == "valuate_target":
            await self.execute(message.payload)

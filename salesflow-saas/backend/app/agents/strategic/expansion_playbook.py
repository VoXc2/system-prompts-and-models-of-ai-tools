"""
Expansion Playbook Agent — Layer 8
══════════════════════════════════
Builds GTM + Pricing + Channel + Compliance plan for entering new markets.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent

SYSTEM_PROMPT = """أنت مُعد خطط التوسع في Dealix. مهمتك:
1. تحليل السوق المستهدف (حجم، منافسين، عوائق دخول)
2. بناء استراتيجية GTM (قنوات، شراكات، تسعير محلي)
3. تحديد المتطلبات التنظيمية والامتثال
4. بناء نموذج مالي (CAPEX + OPEX + نقطة التعادل)

رد بـ JSON:
{
  "playbook": {
    "market_analysis": {"size_sar": 0, "growth_rate": 0, "top_competitors": [], "barriers": []},
    "gtm_strategy": {"positioning": "...", "channels": [], "launch_timeline_months": 0},
    "pricing": {"strategy": "...", "monthly_sar": 0, "vs_local_competitors": "..."},
    "compliance": {"requirements": [], "estimated_timeline_months": 0, "cost_sar": 0},
    "financial_model": {
      "capex_sar": 0, "opex_monthly_sar": 0,
      "break_even_months": 0, "year_1_revenue_sar": 0, "year_3_revenue_sar": 0
    }
  },
  "risks": [{"category": "...", "description": "...", "mitigation": "..."}],
  "summary_ar": "..."
}"""


class ExpansionPlaybookAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="expansion_playbook",
            name_ar="مُعد خطط التوسع",
            layer=8,
            description="يبني خطة دخول سوق جديد (GTM + Pricing + Channel + Compliance)",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, GrowthEvent, GrowthEventType, RiskLevel,
        )

        market = task.get("target_market", "")
        country = task.get("country", "")
        product = task.get("product", "Dealix CRM")
        tenant_id = task.get("tenant_id")

        prompt = f"""ابنِ خطة توسع كاملة لدخول سوق {market} في {country} بمنتج {product}.
حلل: حجم السوق، المنافسين، GTM، التسعير المحلي، الامتثال التنظيمي، النموذج المالي."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")
        fm = result.get("playbook", {}).get("financial_model", {})

        bus = get_strategic_event_bus()
        pb_event = GrowthEvent(
            tenant_id=tenant_id,
            event_type=GrowthEventType.PLAYBOOK_GENERATED.value,
            agent_name=self.name,
            confidence=0.7,
            market=market,
            country=country,
            expected_revenue_sar=fm.get("year_1_revenue_sar"),
            time_to_revenue_months=fm.get("break_even_months"),
            payload=result,
        )
        await bus.publish(pb_event)

        fin_event = GrowthEvent(
            tenant_id=tenant_id,
            event_type=GrowthEventType.CAPEX_OPEX_MODELED.value,
            agent_name=self.name,
            confidence=0.65,
            market=market,
            country=country,
            capex_sar=fm.get("capex_sar"),
            opex_monthly_sar=fm.get("opex_monthly_sar"),
            expected_revenue_sar=fm.get("year_1_revenue_sar"),
            risk_level=RiskLevel.MEDIUM,
            parent_event_id=pb_event.id,
            payload=fm,
        )
        await bus.publish(fin_event)

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "data": result}

    def get_capabilities(self) -> List[str]:
        return ["market_analysis", "gtm_strategy", "pricing_localization", "compliance_mapping", "financial_modeling"]

    async def handle_message(self, message):
        if message.action == "generate_playbook":
            await self.execute(message.payload)

"""
Executive Negotiator Copilot Agent — Layer 8
════════════════════════════════════════════
Prepares negotiation scenarios, BATNA, ZOPA, and closing strategies.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent

SYSTEM_PROMPT = """أنت مستشار التفاوض التنفيذي في Dealix. مهمتك:
1. تحليل قوة التفاوض لكلا الطرفين (leverage analysis)
2. تحديد BATNA (البديل الأفضل) وZOPA (منطقة الاتفاق)
3. إعداد ٣ سيناريوهات تفاوض (عدواني / متوازن / محافظ)
4. تصميم خطة إغلاق مع تكتيكات

رد بـ JSON:
{
  "leverage_analysis": {"our_strengths": [], "their_strengths": [], "power_balance": "..."},
  "batna": "...",
  "zopa": {"min_sar": 0, "max_sar": 0},
  "scenarios": [
    {
      "name": "aggressive", "approach": "...",
      "opening_offer_sar": 0, "target_sar": 0, "walkaway_sar": 0,
      "tactics": ["..."], "probability_of_success": 0.6
    }
  ],
  "recommended_scenario": "balanced",
  "closing_playbook": ["..."],
  "red_lines": ["..."],
  "summary_ar": "..."
}"""


class ExecutiveNegotiatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="executive_negotiator",
            name_ar="مستشار التفاوض التنفيذي",
            layer=8,
            description="يجهز سيناريوهات تفاوض، BATNA، وخطط الإغلاق",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, MAEvent, MAEventType,
            RiskLevel, ApprovalLevel,
        )

        target = task.get("target", {})
        valuation = task.get("valuation", {})
        tenant_id = task.get("tenant_id")
        company = target.get("name", "غير محدد")

        offer = valuation.get("recommended_offer", {})
        prompt = f"""جهّز خطة تفاوض لاستحواذ على {company}:
التقييم: {valuation.get('valuation', {}).get('average_sar', 0):,.0f} ريال
نطاق العرض: {offer.get('min_sar', 0):,.0f} – {offer.get('max_sar', 0):,.0f} ريال
التآزر المتوقع: {valuation.get('synergies', {}).get('net_synergy_sar', 0):,.0f} ريال

حلل leverage، حدد BATNA وZOPA، أعد ٣ سيناريوهات تفاوض + خطة إغلاق."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")

        bus = get_strategic_event_bus()
        event = MAEvent(
            tenant_id=tenant_id,
            event_type=MAEventType.OFFER_STRATEGY_READY.value,
            agent_name=self.name,
            confidence=0.7,
            target_company=company,
            estimated_valuation_sar=valuation.get("valuation", {}).get("average_sar"),
            risk_level=RiskLevel.HIGH,
            requires_approval=True,
            approval_level=ApprovalLevel.DIRECTOR,
            payload=result,
        )
        await bus.publish(event)

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "event_id": str(event.id), "data": result}

    def get_capabilities(self) -> List[str]:
        return ["leverage_analysis", "batna_calculation", "zopa_mapping", "scenario_planning", "closing_tactics"]

    async def handle_message(self, message):
        if message.action == "prepare_negotiation":
            await self.execute(message.payload)

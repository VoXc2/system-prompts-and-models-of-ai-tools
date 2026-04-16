"""
Due Diligence Analyst Agent — Layer 8
═════════════════════════════════════
Manages preliminary financial/operational/legal due diligence on M&A targets.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent, AgentPriority

SYSTEM_PROMPT = """أنت محلل الفحص النافي للجهالة (Due Diligence) في Dealix. مهمتك:
1. تحليل الصحة المالية (إيرادات، هوامش، ديون، تدفقات نقدية)
2. تقييم المخاطر التشغيلية (فريق، عمليات، تقنية، عملاء)
3. فحص المخاطر القانونية والامتثال (عقود، نزاعات، تراخيص، PDPL)
4. تقييم جودة الفريق والإدارة

رد بـ JSON:
{
  "financial_health_score": 75,
  "operational_score": 80,
  "legal_score": 85,
  "team_score": 70,
  "overall_dd_score": 78,
  "red_flags": ["..."],
  "green_flags": ["..."],
  "recommendations": ["..."],
  "summary_ar": "..."
}"""


class DueDiligenceAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="dd_analyst",
            name_ar="محلل الفحص النافي للجهالة",
            layer=8,
            description="يدير الفحص المبدئي المالي/التشغيلي/القانوني لأهداف الاستحواذ",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, MAEvent, MAEventType, RiskLevel, ApprovalLevel,
        )

        target = task.get("target", {})
        tenant_id = task.get("tenant_id")
        company = target.get("name", "غير محدد")

        bus = get_strategic_event_bus()
        # Emit DD_STARTED
        start_event = MAEvent(
            tenant_id=tenant_id,
            event_type=MAEventType.DD_STARTED.value,
            agent_name=self.name,
            confidence=0.5,
            target_company=company,
            payload={"phase": "preliminary"},
        )
        await bus.publish(start_event)

        prompt = f"""أجرِ فحصاً نافياً للجهالة مبدئياً على:
الشركة: {company}
القطاع: {target.get('industry', '')}
الإيرادات: {target.get('revenue_sar', 0):,.0f} ريال
مجالات التآزر: {target.get('synergy_areas', [])}

حلل: الصحة المالية، المخاطر التشغيلية، الامتثال القانوني، جودة الفريق."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")
        red_flags = result.get("red_flags", [])
        overall = result.get("overall_dd_score", 0)

        if red_flags:
            risk_event = MAEvent(
                tenant_id=tenant_id,
                event_type=MAEventType.DD_RISK_FLAGGED.value,
                agent_name=self.name,
                confidence=overall / 100,
                target_company=company,
                risk_level=RiskLevel.HIGH if len(red_flags) > 2 else RiskLevel.MEDIUM,
                requires_approval=True,
                approval_level=ApprovalLevel.DIRECTOR,
                payload={"red_flags": red_flags, "scores": result},
            )
            await bus.publish(risk_event)

        if overall >= 70:
            self.send_message(
                "valuation_synergy", "valuate_target",
                {"target": target, "dd_results": result, "tenant_id": str(tenant_id)},
                AgentPriority.HIGH,
            )

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "overall_score": overall, "red_flags": len(red_flags), "data": result}

    def get_capabilities(self) -> List[str]:
        return ["financial_dd", "operational_dd", "legal_dd", "team_assessment", "risk_flagging"]

    async def handle_message(self, message):
        if message.action == "start_due_diligence":
            await self.execute(message.payload)

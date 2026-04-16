"""
Post-Merger Integration Agent — Layer 8
═══════════════════════════════════════
Manages 30/60/90 day PMI plan (systems, teams, customers, operations).
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent

SYSTEM_PROMPT = """أنت مدير تكامل ما بعد الاستحواذ (PMI) في Dealix. مهمتك:
1. بناء خطة تكامل 30/60/90 يوم
2. تغطية: تكامل الأنظمة، محاذاة الفرق، نقل العملاء، العلامة التجارية، العمليات
3. تحديد المخاطر وخطط التخفيف
4. تعريف KPIs لقياس نجاح التكامل

رد بـ JSON:
{
  "pmi_plan": {
    "day_30": {
      "theme": "Stabilize",
      "priorities": ["..."],
      "milestones": [{"name": "...", "owner": "...", "status": "pending"}]
    },
    "day_60": {
      "theme": "Integrate",
      "priorities": ["..."],
      "milestones": [{"name": "...", "owner": "...", "status": "pending"}]
    },
    "day_90": {
      "theme": "Optimize",
      "priorities": ["..."],
      "milestones": [{"name": "...", "owner": "...", "status": "pending"}]
    }
  },
  "risk_register": [{"risk": "...", "impact": "high", "mitigation": "..."}],
  "kpis": [{"name": "...", "target": "...", "measurement": "..."}],
  "total_integration_cost_sar": 0,
  "summary_ar": "..."
}"""


class PostMergerIntegrationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="post_merger_integration",
            name_ar="مدير تكامل ما بعد الاستحواذ",
            layer=8,
            description="يدير PMI خلال 30/60/90 يوم (أنظمة، فرق، عملاء، عمليات)",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, MAEvent, MAEventType, RiskLevel,
        )

        company = task.get("acquired_company", "غير محدد")
        deal = task.get("deal_terms", {})
        synergy = task.get("synergy_targets", {})
        tenant_id = task.get("tenant_id")

        prompt = f"""ابنِ خطة تكامل PMI لشركة {company}:
شروط الصفقة: {deal}
أهداف التآزر: {synergy}

خطة 30/60/90 يوم تغطي: الأنظمة، الفرق، العملاء، العلامة التجارية، العمليات."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")

        bus = get_strategic_event_bus()
        kickoff = MAEvent(
            tenant_id=tenant_id,
            event_type=MAEventType.INTEGRATION_KICKOFF.value,
            agent_name=self.name,
            confidence=0.9,
            target_company=company,
            risk_level=RiskLevel.MEDIUM,
            payload=result,
        )
        await bus.publish(kickoff)

        # Create milestone events for each phase
        for phase in ["day_30", "day_60", "day_90"]:
            phase_data = result.get("pmi_plan", {}).get(phase, {})
            if phase_data:
                milestone = MAEvent(
                    tenant_id=tenant_id,
                    event_type=MAEventType.INTEGRATION_MILESTONE.value,
                    agent_name=self.name,
                    confidence=0.85,
                    target_company=company,
                    parent_event_id=kickoff.id,
                    payload={"phase": phase, **phase_data},
                )
                await bus.publish(milestone)

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "data": result}

    def get_capabilities(self) -> List[str]:
        return ["pmi_planning", "systems_integration", "team_alignment", "customer_migration", "synergy_tracking"]

    async def handle_message(self, message):
        if message.action == "plan_integration":
            await self.execute(message.payload)

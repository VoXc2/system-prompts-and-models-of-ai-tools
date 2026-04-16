"""
M&A Target Screener Agent — Layer 8
════════════════════════════════════
Screens acquisition targets by fit, risk, and growth potential.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent, AgentPriority

SYSTEM_PROMPT = """أنت فلتر أهداف الاستحواذ في Dealix. مهمتك:
1. تحليل أهداف استحواذ محتملة حسب القطاع والحجم والتوافق الاستراتيجي
2. تسجيل درجة ملاءمة (0–100) لكل هدف
3. تقدير إمكانات النمو ومجالات التآزر
4. تحديد المخاطر الرئيسية

رد بـ JSON:
{
  "targets": [
    {
      "name": "...", "industry": "...", "revenue_sar": 0,
      "fit_score": 80, "growth_potential": "high",
      "synergy_areas": ["customer_base", "technology", "geography"],
      "risks": ["..."], "rationale": "..."
    }
  ],
  "summary_ar": "..."
}"""


class MATargetScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ma_screener",
            name_ar="فلتر أهداف الاستحواذ",
            layer=8,
            description="يفلتر أهداف الاستحواذ بذكاء (fit + risk + growth potential)",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, MAEvent, MAEventType, RiskLevel,
        )

        industry = task.get("industry", "")
        min_rev = task.get("min_revenue_sar", 1_000_000)
        max_rev = task.get("max_revenue_sar", 50_000_000)
        tenant_id = task.get("tenant_id")
        criteria = task.get("strategic_criteria", "")

        prompt = f"""ابحث عن أهداف استحواذ في قطاع {industry}.
نطاق الإيرادات: {min_rev:,.0f} – {max_rev:,.0f} ريال
معايير استراتيجية: {criteria}

حلل أفضل 5 أهداف مع درجة ملاءمة ومخاطر ومجالات تآزر."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")
        targets = result.get("targets", [])

        bus = get_strategic_event_bus()
        events = []
        for t in targets:
            score = t.get("fit_score", 0)
            if score >= 65:
                event = MAEvent(
                    tenant_id=tenant_id,
                    event_type=MAEventType.TARGET_DETECTED.value,
                    agent_name=self.name,
                    confidence=score / 100,
                    target_company=t.get("name"),
                    target_industry=t.get("industry"),
                    target_revenue_sar=t.get("revenue_sar"),
                    fit_score=score,
                    risk_level=RiskLevel.MEDIUM if score < 80 else RiskLevel.LOW,
                    payload=t,
                )
                await bus.publish(event)
                events.append(str(event.id))

                if score >= 80:
                    self.send_message(
                        "dd_analyst", "start_due_diligence",
                        {"target": t, "event_id": str(event.id), "tenant_id": str(tenant_id)},
                        AgentPriority.HIGH,
                    )

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "targets_found": len(targets), "qualified": len(events), "data": result}

    def get_capabilities(self) -> List[str]:
        return ["ma_target_screening", "fit_scoring", "growth_assessment", "synergy_identification"]

    async def handle_message(self, message):
        if message.action == "screen_targets":
            await self.execute(message.payload)

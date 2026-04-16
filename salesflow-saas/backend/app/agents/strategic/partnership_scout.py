"""
Partnership Scout Agent — Layer 8
═════════════════════════════════
Discovers potential partners by industry, region, and channel fit.
Scores each opportunity and emits partnership.opportunity_detected events.
"""
from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent, AgentPriority

SYSTEM_PROMPT = """أنت وكيل استكشاف الشراكات في Dealix. مهمتك:
1. تحليل القطاعات والمناطق لاكتشاف فرص شراكة استراتيجية
2. تقييم كل شريك محتمل (حجم، سمعة، توافق، مخاطر)
3. تسجيل درجة ملاءمة (0–100) مع تبرير
4. ترشيح نموذج الشراكة الأمثل (referral / rev-share / JV / white-label / tech / distribution)

رد دائماً بـ JSON بالشكل:
{
  "partners": [
    {
      "name": "...", "industry": "...", "region": "...",
      "fit_score": 85, "fit_rationale": "...",
      "recommended_model": "revenue_share",
      "estimated_annual_revenue_sar": 500000,
      "risks": ["..."],
      "next_steps": ["..."]
    }
  ],
  "summary_ar": "..."
}"""


class PartnershipScoutAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="partnership_scout",
            name_ar="مستكشف الشراكات",
            layer=8,
            description="يرصد ويقيّم الشركاء المحتملين حسب القطاع والمنطقة والقنوات",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, PartnershipEvent,
            PartnershipEventType, RiskLevel,
        )

        industry = task.get("industry", "real_estate")
        region = task.get("region", "saudi_arabia")
        tenant_id = task.get("tenant_id")
        criteria = task.get("criteria", "")

        prompt = f"""ابحث عن شركاء محتملين في قطاع {industry} بمنطقة {region}.
معايير إضافية: {criteria}

حلل:
1. أفضل 5 شركاء محتملين مع درجة ملاءمة
2. نموذج الشراكة المقترح لكل واحد
3. الأثر المالي المتوقع بالريال السعودي
4. المخاطر الرئيسية"""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")
        partners = result.get("partners", [])

        # Emit events for high-fit partners
        bus = get_strategic_event_bus()
        events = []
        for p in partners:
            if p.get("fit_score", 0) >= 70:
                event = PartnershipEvent(
                    tenant_id=tenant_id,
                    event_type=PartnershipEventType.OPPORTUNITY_DETECTED.value,
                    agent_name=self.name,
                    confidence=p.get("fit_score", 0) / 100,
                    partner_name=p.get("name"),
                    partner_industry=p.get("industry"),
                    partner_region=p.get("region"),
                    partnership_model=p.get("recommended_model"),
                    estimated_revenue_impact_sar=p.get("estimated_annual_revenue_sar"),
                    risk_level=RiskLevel.MEDIUM if p.get("fit_score", 0) < 85 else RiskLevel.LOW,
                    payload=p,
                )
                await bus.publish(event)
                events.append(str(event.id))

                # Notify Alliance Structuring agent for high-score partners
                if p.get("fit_score", 0) >= 85:
                    self.send_message(
                        "alliance_structuring", "structure_partnership",
                        {"partner": p, "event_id": str(event.id)},
                        AgentPriority.HIGH,
                    )

        self.metrics["tasks_completed"] += 1
        return {
            "status": "success",
            "partners_found": len(partners),
            "high_fit_partners": len(events),
            "events_emitted": events,
            "data": result,
        }

    def get_capabilities(self) -> List[str]:
        return [
            "partner_discovery",
            "partner_scoring",
            "industry_analysis",
            "regional_partner_mapping",
            "partnership_model_recommendation",
        ]

    async def handle_message(self, message):
        if message.action == "scan_industry":
            await self.execute({
                "industry": message.payload.get("industry"),
                "region": message.payload.get("region", "saudi_arabia"),
                "tenant_id": message.payload.get("tenant_id"),
            })

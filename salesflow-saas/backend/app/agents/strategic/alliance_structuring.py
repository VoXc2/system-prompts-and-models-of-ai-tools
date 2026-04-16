"""
Alliance Structuring Agent — Layer 8
════════════════════════════════════
Designs partnership structures (Referral / Rev-share / JV) with financial models.
"""
from typing import Any, Dict, List
from app.agents.base_agent import BaseAgent, AgentPriority

SYSTEM_PROMPT = """أنت مهندس هيكلة الشراكات في Dealix. مهمتك:
1. تصميم نموذج الشراكة الأمثل بناءً على ملف الشريك
2. بناء النموذج المالي (إيرادات / تكاليف / عمولات / مدة)
3. صياغة الشروط الرئيسية (Term Sheet)
4. تقييم المخاطر القانونية والتشغيلية

رد بـ JSON:
{
  "partnership_model": "revenue_share",
  "financial_model": {
    "year_1_revenue_sar": 0, "year_2_revenue_sar": 0, "year_3_revenue_sar": 0,
    "partner_share_percent": 20, "dealix_share_percent": 80,
    "setup_cost_sar": 0, "monthly_cost_sar": 0
  },
  "term_sheet": {
    "duration_months": 24, "exclusivity": false,
    "territory": "saudi_arabia", "termination_notice_days": 90,
    "key_terms": ["..."]
  },
  "risks": [{"category": "...", "description": "...", "mitigation": "..."}],
  "recommendation_ar": "...",
  "next_steps": ["..."]
}"""


class AllianceStructuringAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="alliance_structuring",
            name_ar="مهندس هيكلة الشراكات",
            layer=8,
            description="يبني نماذج الشراكة (Referral/Rev-share/JV) مع أثر مالي",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, PartnershipEvent,
            PartnershipEventType, RiskLevel, ApprovalLevel,
        )

        partner = task.get("partner", {})
        tenant_id = task.get("tenant_id")

        prompt = f"""صمم هيكل شراكة مع:
الشريك: {partner.get('name', 'غير محدد')}
القطاع: {partner.get('industry', 'غير محدد')}
المنطقة: {partner.get('region', 'السعودية')}
درجة الملاءمة: {partner.get('fit_score', 0)}
النموذج المقترح: {partner.get('recommended_model', 'referral')}

قدم نموذج مالي لـ 3 سنوات + شروط رئيسية + مخاطر."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")

        bus = get_strategic_event_bus()
        event = PartnershipEvent(
            tenant_id=tenant_id,
            event_type=PartnershipEventType.MODEL_RECOMMENDED.value,
            agent_name=self.name,
            confidence=0.8,
            partner_name=partner.get("name"),
            partnership_model=result.get("partnership_model"),
            estimated_revenue_impact_sar=result.get("financial_model", {}).get("year_1_revenue_sar"),
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
            approval_level=ApprovalLevel.DIRECTOR,
            payload=result,
        )
        await bus.publish(event)

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "event_id": str(event.id), "data": result}

    def get_capabilities(self) -> List[str]:
        return [
            "partnership_structuring",
            "financial_modeling",
            "term_sheet_generation",
            "risk_assessment",
            "rev_share_calculation",
        ]

    async def handle_message(self, message):
        if message.action == "structure_partnership":
            await self.execute({
                "partner": message.payload.get("partner"),
                "tenant_id": message.payload.get("tenant_id"),
            })

"""
Sovereign Growth Intelligence Agent — Layer 8
══════════════════════════════════════════════
Executive dashboard aggregator — board-level strategic brief.
Read-only: does NOT emit events, only reads and synthesizes.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent


SYSTEM_PROMPT = """أنت وكيل الذكاء السيادي للنمو في Dealix. مهمتك:
1. تجميع كل الأحداث الاستراتيجية في تقرير تنفيذي موحد
2. تحديد أهم الفرص والمخاطر والمبادرات
3. حساب pipeline الإيرادات من كل مصدر (شراكات / استحواذات / توسع)
4. تقديم توصيات مبنية على البيانات لمجلس الإدارة

رد بـ JSON:
{
  "executive_brief": {
    "period": "...",
    "highlights": ["..."],
    "top_opportunities": [
      {"title": "...", "impact_sar": 0, "confidence": 0.8, "source_agent": "...", "urgency": "high"}
    ],
    "top_risks": [
      {"title": "...", "severity": "high", "mitigation_status": "..."}
    ],
    "active_initiatives": {"total": 0, "on_track": 0, "at_risk": 0, "blocked": 0},
    "revenue_pipeline": {
      "partnerships_sar": 0, "ma_sar": 0, "expansion_sar": 0, "total_sar": 0
    },
    "pending_decisions": 0,
    "recommendations_for_board": ["..."]
  },
  "summary_ar": "..."
}"""


class SovereignGrowthAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="sovereign_growth",
            name_ar="وكيل الذكاء السيادي للنمو",
            layer=8,
            description="لوحة سيادية للنمو: فرص كبيرة + توصيات مجلس الإدارة",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, EventDomain,
        )

        tenant_id = task.get("tenant_id")
        period = task.get("reporting_period", "monthly")

        bus = get_strategic_event_bus()

        # Gather all events
        partnerships = bus.get_history(EventDomain.PARTNERSHIP, tenant_id)
        ma_events = bus.get_history(EventDomain.MA, tenant_id)
        growth = bus.get_history(EventDomain.GROWTH, tenant_id)
        execution = bus.get_history(EventDomain.EXECUTION, tenant_id)
        pending = bus.get_pending_approvals(tenant_id)

        # Build context for AI synthesis
        context = {
            "partnership_events": len(partnerships),
            "ma_events": len(ma_events),
            "growth_events": len(growth),
            "execution_events": len(execution),
            "pending_approvals": len(pending),
            "partnership_highlights": [
                {"type": e.event_type, "partner": getattr(e, "partner_name", "?"),
                 "impact": getattr(e, "estimated_revenue_impact_sar", 0),
                 "confidence": e.confidence}
                for e in partnerships[-10:]
            ],
            "ma_highlights": [
                {"type": e.event_type, "target": getattr(e, "target_company", "?"),
                 "valuation": getattr(e, "estimated_valuation_sar", 0),
                 "confidence": e.confidence}
                for e in ma_events[-10:]
            ],
            "growth_highlights": [
                {"type": e.event_type, "market": getattr(e, "market", "?"),
                 "revenue": getattr(e, "expected_revenue_sar", 0)}
                for e in growth[-10:]
            ],
        }

        prompt = f"""اصنع تقرير تنفيذي سيادي للفترة: {period}

البيانات المتاحة:
- أحداث الشراكات: {context['partnership_events']}
- أحداث الاستحواذ: {context['ma_events']}
- أحداث النمو والتوسع: {context['growth_events']}
- المبادرات التنفيذية: {context['execution_events']}
- قرارات معلقة: {context['pending_approvals']}

أبرز الشراكات: {context['partnership_highlights']}
أبرز الاستحواذات: {context['ma_highlights']}
أبرز التوسعات: {context['growth_highlights']}

قدم: ملخص تنفيذي + أهم الفرص + أهم المخاطر + pipeline الإيرادات + توصيات لمجلس الإدارة."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "data": result, "raw_counts": {
            "partnerships": len(partnerships),
            "ma": len(ma_events),
            "growth": len(growth),
            "execution": len(execution),
            "pending_decisions": len(pending),
        }}

    def get_capabilities(self) -> List[str]:
        return [
            "executive_briefing", "board_memo_generation", "strategic_synthesis",
            "revenue_pipeline_aggregation", "risk_consolidation", "recommendation_ranking",
        ]

    async def handle_message(self, message):
        if message.action in ("generate_brief", "board_report"):
            await self.execute(message.payload)

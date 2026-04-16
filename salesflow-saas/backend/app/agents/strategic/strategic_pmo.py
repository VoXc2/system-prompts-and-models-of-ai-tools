"""
Strategic PMO Agent — Layer 8
════════════════════════════
Converts strategic decisions into executable initiatives with SLAs and owners.
"""
from typing import Dict, List
from app.agents.base_agent import BaseAgent, AgentPriority

SYSTEM_PROMPT = """أنت مدير المشاريع الاستراتيجية (PMO) في Dealix. مهمتك:
1. تحويل القرارات الاستراتيجية إلى مبادرات تنفيذية
2. تحديد المالك (Owner) والمعالم (Milestones) لكل مبادرة
3. تحديد SLA والتبعيات ومؤشرات الأداء
4. رصد التأخيرات والعوائق

رد بـ JSON:
{
  "initiatives": [
    {
      "name": "...", "name_ar": "...", "owner": "...",
      "priority": "high", "sla_days": 30,
      "milestones": [{"name": "...", "due_date": "2026-05-01", "status": "pending"}],
      "dependencies": ["..."],
      "kpis": [{"name": "...", "target": "...", "unit": "..."}],
      "estimated_cost_sar": 0
    }
  ],
  "summary_ar": "..."
}"""


class StrategicPMOAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="strategic_pmo",
            name_ar="مدير المشاريع الاستراتيجية",
            layer=8,
            description="يحول القرارات إلى مبادرات تنفيذية مع SLA وOwners",
        )

    async def execute(self, task: Dict) -> Dict:
        from app.agents.strategic.events import (
            get_strategic_event_bus, ExecutionEvent, ExecutionEventType, RiskLevel,
        )

        decision = task.get("decision", "")
        context = task.get("context", {})
        tenant_id = task.get("tenant_id")

        prompt = f"""حوّل هذا القرار الاستراتيجي إلى مبادرات تنفيذية:
القرار: {decision}
السياق: {context}

لكل مبادرة حدد: المالك، المعالم مع تواريخ، SLA، التبعيات، KPIs."""

        result = await self.think_json(prompt, SYSTEM_PROMPT, task_type="strategic")
        initiatives = result.get("initiatives", [])

        bus = get_strategic_event_bus()
        events = []
        for init in initiatives:
            event = ExecutionEvent(
                tenant_id=tenant_id,
                event_type=ExecutionEventType.INITIATIVE_CREATED.value,
                agent_name=self.name,
                confidence=0.85,
                initiative_name=init.get("name"),
                owner=init.get("owner"),
                sla_days=init.get("sla_days", 30),
                risk_level=RiskLevel.LOW,
                payload=init,
            )
            await bus.publish(event)
            events.append(str(event.id))

        self.metrics["tasks_completed"] += 1
        return {"status": "success", "initiatives_created": len(initiatives), "events": events, "data": result}

    async def check_sla_breaches(self, tenant_id):
        """Periodic check for SLA breaches across all active initiatives."""
        from app.agents.strategic.events import (
            get_strategic_event_bus, ExecutionEvent, ExecutionEventType, RiskLevel,
        )
        from datetime import datetime, timezone

        bus = get_strategic_event_bus()
        active = [e for e in bus.get_history()
                  if e.event_type == ExecutionEventType.INITIATIVE_CREATED.value
                  and getattr(e, "tenant_id", None) == tenant_id]

        now = datetime.now(timezone.utc)
        breaches = []
        for e in active:
            sla = getattr(e, "sla_days", 30) or 30
            elapsed = (now - e.timestamp).days
            if elapsed > sla:
                breach = ExecutionEvent(
                    tenant_id=tenant_id,
                    event_type=ExecutionEventType.SLA_BREACHED.value,
                    agent_name=self.name,
                    confidence=1.0,
                    initiative_name=getattr(e, "initiative_name", ""),
                    sla_days=sla,
                    days_elapsed=elapsed,
                    risk_level=RiskLevel.HIGH,
                    requires_approval=True,
                    parent_event_id=e.id,
                    payload={"original_event": str(e.id)},
                )
                await bus.publish(breach)
                breaches.append(str(breach.id))
        return breaches

    def get_capabilities(self) -> List[str]:
        return ["initiative_creation", "milestone_tracking", "sla_monitoring", "dependency_mapping", "kpi_definition"]

    async def handle_message(self, message):
        if message.action == "create_initiatives":
            await self.execute(message.payload)
        elif message.action == "check_sla":
            await self.check_sla_breaches(message.payload.get("tenant_id"))

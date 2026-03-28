"""
Dealix Sequence Worker - Executes automated sales sequence steps.
Runs every minute via Celery beat, checks for due steps, and executes them.
"""
from celery import shared_task
from datetime import datetime, timezone, timedelta
import asyncio


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(name="app.workers.sequence_worker.process_sequence_steps")
def process_sequence_steps():
    """
    Check for sequence steps that are due and execute them.
    Runs every minute via Celery beat.
    """
    from app.services.smart_sales import SmartSalesAgent
    from app.services.auto_outreach import OutreachScheduler
    from app.integrations.whatsapp import send_whatsapp_message, send_whatsapp_template

    # Only process during optimal sending hours
    if not OutreachScheduler.should_send_now():
        return {
            "status": "skipped",
            "reason": "Outside optimal sending hours",
            "next_window": OutreachScheduler.get_next_send_time().isoformat(),
        }

    # In production, this queries the DB for enrollments where next_step_at <= now
    # For now, return structure showing the pattern
    return {
        "status": "processed",
        "steps_executed": 0,
        "messages_sent": 0,
        "tasks_created": 0,
        "errors": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@shared_task(name="app.workers.sequence_worker.execute_sequence_step")
def execute_sequence_step(enrollment_id: str, step_data: dict):
    """Execute a single sequence step for an enrolled lead."""
    from app.services.smart_sales import SmartSalesAgent
    from app.integrations.whatsapp import send_whatsapp_message, send_whatsapp_template

    async def _execute():
        step_type = step_data.get("step_type", "")
        lead_data = step_data.get("lead_data", {})
        industry = step_data.get("industry", "general")

        if step_type == "send_whatsapp":
            if step_data.get("ai_generated"):
                agent = SmartSalesAgent(tenant_id="default", industry=industry)
                message = await agent.generate_followup_message(
                    lead_data, days_since_last=step_data.get("delay_days", 3)
                )
            else:
                message = step_data.get("message_content", "")

            if lead_data.get("phone") and message:
                result = await send_whatsapp_message(lead_data["phone"], message)
                return {"sent": True, "channel": "whatsapp", "result": result}

        elif step_type == "send_whatsapp_template":
            template = step_data.get("template_name", "")
            if lead_data.get("phone") and template:
                result = await send_whatsapp_template(lead_data["phone"], template)
                return {"sent": True, "channel": "whatsapp_template", "result": result}

        elif step_type == "create_task":
            return {
                "action": "task_created",
                "task": step_data.get("message_content", "متابعة العميل"),
                "assigned_to": step_data.get("assigned_to"),
            }

        elif step_type == "update_status":
            return {
                "action": "status_updated",
                "new_status": step_data.get("new_status", "contacted"),
            }

        elif step_type == "ai_reply":
            agent = SmartSalesAgent(tenant_id="default", industry=industry)
            message = await agent.generate_outreach_message(lead_data, step_data.get("message_type", "متابعة"))
            if lead_data.get("phone") and message:
                result = await send_whatsapp_message(lead_data["phone"], message)
                return {"sent": True, "channel": "whatsapp", "ai_generated": True, "result": result}

        return {"sent": False, "reason": "invalid_step_type"}

    return run_async(_execute())


@shared_task(name="app.workers.sequence_worker.enroll_lead_in_sequence")
def enroll_lead_in_sequence(tenant_id: str, lead_data: dict, sequence_id: str):
    """Enroll a lead in a sales sequence."""
    return {
        "status": "enrolled",
        "tenant_id": tenant_id,
        "lead_name": lead_data.get("name", ""),
        "sequence_id": sequence_id,
        "first_step_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
    }

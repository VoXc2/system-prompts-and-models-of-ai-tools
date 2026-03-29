"""
Dealix Sequence Worker - Executes automated sales sequence steps.
Runs every minute via Celery beat, checks for due steps, and executes them.
"""
import logging
from celery import shared_task
from datetime import datetime, timezone, timedelta
import asyncio

from sqlalchemy import select, and_

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _process_due_steps():
    """Query DB for due sequence steps and execute them."""
    from app.database import async_session
    from app.models.sequence import SequenceEnrollment, SequenceStep, Sequence
    from app.models.lead import Lead
    from app.services.consent_service import ConsentService
    from app.integrations.whatsapp import send_whatsapp_message, send_whatsapp_template
    from app.services.smart_sales import SmartSalesAgent

    now = datetime.now(timezone.utc)
    results = {
        "steps_executed": 0,
        "messages_sent": 0,
        "tasks_created": 0,
        "errors": 0,
        "suppressed": 0,
    }

    async with async_session() as db:
        # Find active enrollments with due steps
        stmt = select(SequenceEnrollment).where(
            and_(
                SequenceEnrollment.status == "active",
                SequenceEnrollment.next_step_at <= now,
            )
        ).limit(100)
        result = await db.execute(stmt)
        enrollments = result.scalars().all()

        for enrollment in enrollments:
            try:
                # Get the current step definition
                step_stmt = select(SequenceStep).where(
                    and_(
                        SequenceStep.sequence_id == enrollment.sequence_id,
                        SequenceStep.step_order == enrollment.current_step,
                    )
                )
                step_result = await db.execute(step_stmt)
                step = step_result.scalar_one_or_none()

                if not step:
                    enrollment.status = "completed"
                    enrollment.completed_at = now
                    results["steps_executed"] += 1
                    continue

                # Get lead data
                lead_stmt = select(Lead).where(Lead.id == enrollment.lead_id)
                lead_result = await db.execute(lead_stmt)
                lead = lead_result.scalar_one_or_none()

                if not lead:
                    enrollment.status = "bounced"
                    continue

                tenant_id = str(enrollment.tenant_id)

                # PDPL: Check suppression before sending
                consent_svc = ConsentService(db, tenant_id)
                channel = step.channel or "whatsapp"
                eligibility = await consent_svc.can_contact(
                    phone=lead.phone, email=getattr(lead, "email", None),
                    channel=channel, consent_type="marketing",
                )
                if not eligibility.get("allowed", True):
                    enrollment.status = "suppressed"
                    results["suppressed"] += 1
                    continue

                # Execute the step
                step_type = step.step_type

                if step_type in ("send_whatsapp", "ai_reply"):
                    if step.ai_generated or step_type == "ai_reply":
                        agent = SmartSalesAgent(tenant_id=tenant_id, industry=getattr(lead, "industry", "general") or "general")
                        message = await agent.generate_followup_message(
                            {"name": lead.full_name, "phone": lead.phone, "company": getattr(lead, "company", "")},
                            days_since_last=step.delay_days or 3,
                        )
                    else:
                        message = step.message_content or ""

                    if lead.phone and message:
                        await send_whatsapp_message(lead.phone, message)
                        results["messages_sent"] += 1

                elif step_type == "send_whatsapp_template":
                    if lead.phone and step.template_name:
                        await send_whatsapp_template(lead.phone, step.template_name)
                        results["messages_sent"] += 1

                elif step_type == "create_task":
                    results["tasks_created"] += 1

                elif step_type == "update_status":
                    new_status = step.message_content or "contacted"
                    lead.status = new_status

                elif step_type == "wait":
                    pass  # Just advances to next step

                # Advance to next step
                enrollment.current_step += 1
                next_delay = timedelta(days=step.delay_days or 0, hours=step.delay_hours or 0)
                if next_delay.total_seconds() == 0:
                    next_delay = timedelta(hours=1)
                enrollment.next_step_at = now + next_delay

                # Check if sequence is complete (get total steps)
                seq_stmt = select(Sequence).where(Sequence.id == enrollment.sequence_id)
                seq_result = await db.execute(seq_stmt)
                sequence = seq_result.scalar_one_or_none()
                if sequence and enrollment.current_step >= sequence.total_steps:
                    enrollment.status = "completed"
                    enrollment.completed_at = now

                results["steps_executed"] += 1

            except Exception as e:
                results["errors"] += 1
                logger.error("Error executing step for enrollment %s: %s", enrollment.id, e)

        await db.commit()

    return results


@shared_task(name="app.workers.sequence_worker.process_sequence_steps")
def process_sequence_steps():
    """
    Check for sequence steps that are due and execute them.
    Runs every minute via Celery beat.
    """
    from app.services.auto_outreach import OutreachScheduler

    # Only process during optimal sending hours
    if not OutreachScheduler.should_send_now():
        return {
            "status": "skipped",
            "reason": "Outside optimal sending hours",
            "next_window": OutreachScheduler.get_next_send_time().isoformat(),
        }

    results = run_async(_process_due_steps())
    return {"status": "processed", "timestamp": datetime.now(timezone.utc).isoformat(), **results}


@shared_task(name="app.workers.sequence_worker.execute_sequence_step")
def execute_sequence_step(enrollment_id: str, step_data: dict):
    """Execute a single sequence step for an enrolled lead."""
    from app.services.smart_sales import SmartSalesAgent
    from app.integrations.whatsapp import send_whatsapp_message, send_whatsapp_template

    async def _execute():
        step_type = step_data.get("step_type", "")
        lead_data = step_data.get("lead_data", {})
        industry = step_data.get("industry", "general")
        tenant_id = step_data.get("tenant_id", "default")

        if step_type == "send_whatsapp":
            if step_data.get("ai_generated"):
                agent = SmartSalesAgent(tenant_id=tenant_id, industry=industry)
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
            agent = SmartSalesAgent(tenant_id=tenant_id, industry=industry)
            message = await agent.generate_outreach_message(lead_data, step_data.get("message_type", "متابعة"))
            if lead_data.get("phone") and message:
                result = await send_whatsapp_message(lead_data["phone"], message)
                return {"sent": True, "channel": "whatsapp", "ai_generated": True, "result": result}

        return {"sent": False, "reason": "invalid_step_type"}

    return run_async(_execute())


@shared_task(name="app.workers.sequence_worker.enroll_lead_in_sequence")
def enroll_lead_in_sequence(tenant_id: str, lead_data: dict, sequence_id: str):
    """Enroll a lead in a sales sequence."""
    async def _enroll():
        from app.database import async_session
        from app.models.sequence import SequenceEnrollment

        now = datetime.now(timezone.utc)
        async with async_session() as db:
            enrollment = SequenceEnrollment(
                tenant_id=tenant_id,
                sequence_id=sequence_id,
                lead_id=lead_data.get("id"),
                current_step=0,
                status="active",
                enrolled_at=now,
                next_step_at=now + timedelta(minutes=5),
            )
            db.add(enrollment)
            await db.commit()
            return {
                "status": "enrolled",
                "enrollment_id": str(enrollment.id),
                "first_step_at": enrollment.next_step_at.isoformat(),
            }

    return run_async(_enroll())

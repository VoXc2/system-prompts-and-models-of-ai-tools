"""Command Feed من أحداث DB — مع fallback إلى العرض التجريبي."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auto_client_acquisition.innovation.command_feed import build_demo_command_feed
from db.models import EmailSendLog, OutreachQueueRecord, ProofLedgerEventRecord, TaskRecord


async def build_command_feed_from_db(
    session: AsyncSession,
    *,
    tenant_id: str = "default",
    limit_per_type: int = 3,
) -> dict[str, Any]:
    """
    يبني بطاقات من طابور الموافقة، المهام المتأخرة، سجل الإيميل، آخر أحداث الدفتر.

    عند غياب بيانات كافية يُرجع نفس بطاقات ``build_demo_command_feed`` مع ``source=demo_fallback``.

    عند فشل الاستعلام (مثلاً جداول غير مهيأة في بيئة اختبار) يُرجع العرض التجريبي.
    """
    try:
        return await _build_command_feed_from_db_impl(
            session, tenant_id=tenant_id, limit_per_type=limit_per_type
        )
    except SQLAlchemyError:
        demo = build_demo_command_feed()
        return {**demo, "source": "demo_fallback", "live": False}


async def _build_command_feed_from_db_impl(
    session: AsyncSession,
    *,
    tenant_id: str = "default",
    limit_per_type: int = 3,
) -> dict[str, Any]:
    cards: list[dict[str, Any]] = []
    now = datetime.now(tz=UTC)
    lim = min(max(limit_per_type, 1), 10)

    q_queue = (
        select(OutreachQueueRecord)
        .where(
            OutreachQueueRecord.approval_required.is_(True),
            OutreachQueueRecord.status == "queued",
        )
        .order_by(OutreachQueueRecord.created_at.desc())
        .limit(lim)
    )
    res_q = await session.execute(q_queue)
    for row in res_q.scalars():
        cards.append(
            {
                "type": "approval_needed",
                "title_ar": "موافقة مطلوبة — رسالة في الطابور",
                "why": f"رسالة {row.channel} بانتظار الموافقة.",
                "risk": row.risk_reason or "راجع المحتوى والامتثال قبل الإرسال.",
                "suggested_action": "راجع النص ووافق أو عدّل من لوحة الإدارة.",
                "cta": "مراجعة الطابور",
                "source_ref": {"table": "outreach_queue", "id": row.id},
            }
        )

    overdue = now - timedelta(days=3)
    q_tasks = (
        select(TaskRecord)
        .where(
            TaskRecord.status == "pending",
            TaskRecord.due_at < overdue,
        )
        .order_by(TaskRecord.due_at.asc())
        .limit(lim)
    )
    res_t = await session.execute(q_tasks)
    for row in res_t.scalars():
        cards.append(
            {
                "type": "leak",
                "title_ar": "مهمة متابعة متأخرة",
                "why": f"مهمة {row.task_type} تجاوزت موعدها.",
                "risk": "تسريب زخم الصفقة أو انطباع ضعيف.",
                "suggested_action": "حدّد خطوة تالية أو أغلق المهمة بتعليق.",
                "cta": "عرض المهام",
                "source_ref": {"table": "tasks", "id": row.id},
            }
        )

    q_block = (
        select(EmailSendLog)
        .where(EmailSendLog.status == "blocked_compliance")
        .order_by(EmailSendLog.created_at.desc())
        .limit(lim)
    )
    res_b = await session.execute(q_block)
    for row in res_b.scalars():
        cards.append(
            {
                "type": "compliance_risk",
                "title_ar": "إرسال بريد موقوف لأسباب امتثال",
                "why": f"سجل إرسال إلى {row.to_email} بحالة blocked_compliance.",
                "risk": "تكرار المحاولة دون مراجعة قد يخالف السياسة.",
                "suggested_action": "راجع compliance_check_json وسجّل القرار.",
                "cta": "سجل الإرسال",
                "source_ref": {"table": "email_send_log", "id": row.id},
            }
        )

    q_pl = (
        select(ProofLedgerEventRecord)
        .where(ProofLedgerEventRecord.tenant_id == tenant_id)
        .order_by(ProofLedgerEventRecord.created_at.desc())
        .limit(lim)
    )
    res_p = await session.execute(q_pl)
    for row in res_p.scalars():
        cards.append(
            {
                "type": "proof_update",
                "title_ar": f"حدث دفتر إثبات — {row.event_type}",
                "why": row.notes_ar or "حدث جديد في سجل الإثبات.",
                "risk": "التقديرات تقريبية حتى ربط CRM.",
                "suggested_action": "أدرج في تقرير الأسبوع للإدارة.",
                "cta": "عرض الدفتر",
                "source_ref": {"table": "proof_ledger_events", "id": row.id},
            }
        )

    if not cards:
        demo = build_demo_command_feed()
        return {**demo, "source": "demo_fallback", "live": False}

    return {"cards": cards[:25], "source": "database", "live": True, "demo": False}

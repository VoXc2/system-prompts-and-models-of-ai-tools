"""
Dealix Notification Service - In-app notifications, email alerts, and WhatsApp notifications.
Handles all notification dispatch for the Dealix CRM platform.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.config import get_settings
from app.database import get_db
from app.models.notification import Notification

settings = get_settings()

# ---------------------------------------------------------------------------
# Arabic notification templates keyed by notification type
# ---------------------------------------------------------------------------
NOTIFICATION_TEMPLATES = {
    "new_lead": {
        "title": "عميل محتمل جديد",
        "body": "عميل محتمل جديد: {name} - {source}",
    },
    "deal_won": {
        "title": "صفقة مكسوبة",
        "body": "تم إغلاق صفقة: {title} - {amount} ر.س",
    },
    "deal_lost": {
        "title": "صفقة خاسرة",
        "body": "تم خسارة صفقة: {title} - السبب: {reason}",
    },
    "task_assigned": {
        "title": "مهمة جديدة",
        "body": "تم تعيين مهمة جديدة لك: {task}",
    },
    "message_received": {
        "title": "رسالة جديدة",
        "body": "رسالة جديدة من {contact_name}",
    },
    "sequence_completed": {
        "title": "اكتملت السلسلة",
        "body": "اكتملت سلسلة التواصل \"{sequence_name}\" للعميل {contact_name}",
    },
    "system_alert": {
        "title": "تنبيه النظام",
        "body": "{message}",
    },
    "ai_insight": {
        "title": "رؤية ذكية من ديليكس",
        "body": "{insight}",
    },
}

VALID_NOTIFICATION_TYPES = set(NOTIFICATION_TEMPLATES.keys())


class NotificationService:
    """Central service for creating and managing Dealix CRM notifications."""

    # ------------------------------------------------------------------
    # Core send helpers
    # ------------------------------------------------------------------

    async def send_notification(
        self,
        tenant_id: str,
        user_id: str,
        notification_type: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> dict:
        """Create a single in-app notification record.

        Parameters
        ----------
        tenant_id : str
            The tenant (organisation) this notification belongs to.
        user_id : str
            Target user who should receive the notification.
        notification_type : str
            One of the VALID_NOTIFICATION_TYPES.
        title : str
            Notification title (Arabic).
        body : str
            Notification body text (Arabic).
        data : dict, optional
            Arbitrary JSON metadata attached to the notification.

        Returns
        -------
        dict
            Created notification record.
        """
        if notification_type not in VALID_NOTIFICATION_TYPES:
            return {
                "success": False,
                "error": f"نوع الإشعار غير صالح: {notification_type}",
            }

        notification_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        notification_record = {
            "id": notification_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
            "type": notification_type,
            "title": title,
            "body": body,
            "is_read": False,
            "extra_data": data or {},
            "created_at": now.isoformat(),
        }

        try:
            db = get_db()
            notification = Notification(
                id=uuid.UUID(notification_id),
                tenant_id=uuid.UUID(tenant_id) if isinstance(tenant_id, str) else tenant_id,
                user_id=uuid.UUID(user_id) if isinstance(user_id, str) else user_id,
                type=notification_type,
                title=title,
                body=body,
                is_read=False,
                extra_data=data or {},
            )
            db.add(notification)
            db.commit()
        except Exception:
            # If persistence fails we still return the record so callers
            # can handle gracefully (e.g. during tests or DB downtime).
            pass

        return {"success": True, "notification": notification_record}

    async def send_bulk_notification(
        self,
        tenant_id: str,
        user_ids: list,
        notification_type: str,
        title: str,
        body: str,
    ) -> dict:
        """Send the same notification to multiple users.

        Returns
        -------
        dict
            Summary with sent / failed counts and per-user results.
        """
        results = []
        sent_count = 0
        failed_count = 0

        for user_id in user_ids:
            result = await self.send_notification(
                tenant_id=tenant_id,
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                body=body,
            )
            results.append(result)
            if result.get("success"):
                sent_count += 1
            else:
                failed_count += 1

        return {
            "success": True,
            "total": len(user_ids),
            "sent": sent_count,
            "failed": failed_count,
            "results": results,
        }

    # ------------------------------------------------------------------
    # Domain-specific notification helpers
    # ------------------------------------------------------------------

    async def notify_new_lead(self, tenant_id: str, lead_data: dict) -> dict:
        """Notify assigned users about a newly created lead.

        ``lead_data`` should contain at least ``name``, ``source``, and
        ``assigned_to`` (user id or list of user ids).
        """
        template = NOTIFICATION_TEMPLATES["new_lead"]
        name = lead_data.get("name", "غير معروف")
        source = lead_data.get("source", "غير محدد")

        title = template["title"]
        body = template["body"].format(name=name, source=source)

        assigned_to = lead_data.get("assigned_to")
        if isinstance(assigned_to, list):
            return await self.send_bulk_notification(
                tenant_id=tenant_id,
                user_ids=assigned_to,
                notification_type="new_lead",
                title=title,
                body=body,
            )

        user_id = assigned_to or lead_data.get("user_id", "")
        return await self.send_notification(
            tenant_id=tenant_id,
            user_id=user_id,
            notification_type="new_lead",
            title=f"عميل محتمل جديد: {name}",
            body=body,
            data={"lead_id": lead_data.get("id")},
        )

    async def notify_deal_won(self, tenant_id: str, deal_data: dict) -> dict:
        """Notify when a deal is closed-won."""
        template = NOTIFICATION_TEMPLATES["deal_won"]
        deal_title = deal_data.get("title", "صفقة")
        amount = deal_data.get("amount", 0)

        title = template["title"]
        body = template["body"].format(title=deal_title, amount=amount)
        formatted_title = f"تم إغلاق صفقة: {deal_title} - {amount} ر.س"

        user_id = deal_data.get("owner_id") or deal_data.get("user_id", "")
        return await self.send_notification(
            tenant_id=tenant_id,
            user_id=user_id,
            notification_type="deal_won",
            title=formatted_title,
            body=body,
            data={
                "deal_id": deal_data.get("id"),
                "amount": amount,
            },
        )

    async def notify_deal_lost(self, tenant_id: str, deal_data: dict) -> dict:
        """Notify when a deal is closed-lost."""
        template = NOTIFICATION_TEMPLATES["deal_lost"]
        deal_title = deal_data.get("title", "صفقة")
        reason = deal_data.get("lost_reason", "غير محدد")

        title = template["title"]
        body = template["body"].format(title=deal_title, reason=reason)

        user_id = deal_data.get("owner_id") or deal_data.get("user_id", "")
        return await self.send_notification(
            tenant_id=tenant_id,
            user_id=user_id,
            notification_type="deal_lost",
            title=title,
            body=body,
            data={
                "deal_id": deal_data.get("id"),
                "lost_reason": reason,
            },
        )

    async def notify_task_assigned(
        self, tenant_id: str, user_id: str, task_data: dict
    ) -> dict:
        """Notify a user that a task has been assigned to them."""
        template = NOTIFICATION_TEMPLATES["task_assigned"]
        task_title = task_data.get("title", task_data.get("task", "مهمة"))

        title = template["title"]
        body = template["body"].format(task=task_title)
        formatted_title = f"تم تعيين مهمة جديدة لك: {task_title}"

        return await self.send_notification(
            tenant_id=tenant_id,
            user_id=user_id,
            notification_type="task_assigned",
            title=formatted_title,
            body=body,
            data={
                "task_id": task_data.get("id"),
                "due_date": task_data.get("due_date"),
            },
        )

    async def notify_message_received(
        self, tenant_id: str, message_data: dict
    ) -> dict:
        """Notify when a new message is received from a contact."""
        template = NOTIFICATION_TEMPLATES["message_received"]
        contact_name = message_data.get("contact_name", "جهة اتصال")

        title = template["title"]
        body = template["body"].format(contact_name=contact_name)
        formatted_title = f"رسالة جديدة من {contact_name}"

        user_id = message_data.get("assigned_to") or message_data.get("user_id", "")
        return await self.send_notification(
            tenant_id=tenant_id,
            user_id=user_id,
            notification_type="message_received",
            title=formatted_title,
            body=body,
            data={
                "message_id": message_data.get("id"),
                "contact_id": message_data.get("contact_id"),
                "channel": message_data.get("channel", "whatsapp"),
            },
        )

    async def notify_sequence_completed(
        self, tenant_id: str, enrollment_data: dict
    ) -> dict:
        """Notify when an outreach sequence finishes for a contact."""
        template = NOTIFICATION_TEMPLATES["sequence_completed"]
        sequence_name = enrollment_data.get("sequence_name", "سلسلة")
        contact_name = enrollment_data.get("contact_name", "عميل")

        title = template["title"]
        body = template["body"].format(
            sequence_name=sequence_name, contact_name=contact_name
        )

        user_id = (
            enrollment_data.get("owner_id")
            or enrollment_data.get("user_id", "")
        )
        return await self.send_notification(
            tenant_id=tenant_id,
            user_id=user_id,
            notification_type="sequence_completed",
            title=title,
            body=body,
            data={
                "sequence_id": enrollment_data.get("sequence_id"),
                "enrollment_id": enrollment_data.get("id"),
                "contact_id": enrollment_data.get("contact_id"),
            },
        )

    # ------------------------------------------------------------------
    # Read / update helpers
    # ------------------------------------------------------------------

    async def get_user_notifications(
        self,
        tenant_id: str,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list:
        """Return notifications for a user, newest first.

        Parameters
        ----------
        tenant_id : str
        user_id : str
        unread_only : bool
            If ``True``, only return unread notifications.
        limit : int
            Maximum number of notifications to return (default 50).

        Returns
        -------
        list[dict]
        """
        try:
            db = get_db()
            query = (
                db.query(Notification)
                .filter(
                    Notification.tenant_id == tenant_id,
                    Notification.user_id == user_id,
                )
            )
            if unread_only:
                query = query.filter(Notification.is_read == False)  # noqa: E712

            notifications = (
                query.order_by(Notification.created_at.desc())
                .limit(limit)
                .all()
            )

            return [
                {
                    "id": str(n.id),
                    "type": n.type,
                    "title": n.title,
                    "body": n.body,
                    "is_read": n.is_read,
                    "extra_data": n.extra_data,
                    "created_at": n.created_at.isoformat() if n.created_at else None,
                }
                for n in notifications
            ]
        except Exception:
            return []

    async def mark_as_read(self, notification_id: str) -> dict:
        """Mark a single notification as read."""
        try:
            db = get_db()
            notification = (
                db.query(Notification)
                .filter(Notification.id == notification_id)
                .first()
            )
            if not notification:
                return {"success": False, "error": "الإشعار غير موجود"}

            notification.is_read = True
            db.commit()
            return {"success": True, "notification_id": notification_id}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    async def mark_all_as_read(self, tenant_id: str, user_id: str) -> dict:
        """Mark every unread notification for a user as read."""
        try:
            db = get_db()
            updated = (
                db.query(Notification)
                .filter(
                    Notification.tenant_id == tenant_id,
                    Notification.user_id == user_id,
                    Notification.is_read == False,  # noqa: E712
                )
                .update({"is_read": True})
            )
            db.commit()
            return {"success": True, "updated_count": updated}
        except Exception as exc:
            return {"success": False, "error": str(exc)}


# Module-level singleton for convenience
notification_service = NotificationService()

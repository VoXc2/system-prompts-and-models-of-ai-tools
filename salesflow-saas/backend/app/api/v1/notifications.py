"""In-app notification endpoints for Dealix CRM."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from typing import Optional

from app.api.v1.deps import get_current_user, get_db
from app.models.notification import Notification

router = APIRouter()


def _serialize(n: Notification) -> dict:
    return {
        "id": str(n.id),
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "is_read": n.is_read,
        "metadata": n.extra_data or {},
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


@router.get("")
async def list_notifications(
    unread_only: bool = Query(False, description="عرض غير المقروءة فقط"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """عرض الإشعارات الخاصة بالمستخدم."""
    user_id = current_user["user_id"]
    tenant_id = current_user["tenant_id"]

    query = select(Notification).where(
        Notification.tenant_id == tenant_id,
        Notification.user_id == user_id,
    )
    if unread_only:
        query = query.where(Notification.is_read == False)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
    unread_count = (await db.execute(
        select(func.count()).where(
            Notification.tenant_id == tenant_id,
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
    )).scalar() or 0

    offset = (page - 1) * per_page
    query = query.order_by(Notification.created_at.desc()).offset(offset).limit(per_page)
    result = await db.execute(query)
    notifications = result.scalars().all()

    return {
        "status": "success",
        "data": {
            "items": [_serialize(n) for n in notifications],
            "total": total,
            "unread_count": unread_count,
            "page": page,
            "per_page": per_page,
        },
    }


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """تحديد إشعار كمقروء."""
    user_id = current_user["user_id"]
    tenant_id = current_user["tenant_id"]

    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.tenant_id == tenant_id,
            Notification.user_id == user_id,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="الإشعار غير موجود")

    notif.is_read = True
    await db.commit()
    return {"status": "success", "message": "تم تحديد الإشعار كمقروء"}


@router.post("/read-all")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """تحديد جميع الإشعارات كمقروءة."""
    user_id = current_user["user_id"]
    tenant_id = current_user["tenant_id"]

    await db.execute(
        update(Notification)
        .where(
            Notification.tenant_id == tenant_id,
            Notification.user_id == user_id,
            Notification.is_read == False,
        )
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "success", "message": "تم تحديد جميع الإشعارات كمقروءة"}

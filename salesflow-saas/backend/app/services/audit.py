"""Audit logging service — records all significant actions for compliance."""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


async def log_action(
    db: AsyncSession,
    tenant_id: str,
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str = None,
    changes: dict = None,
    ip_address: str = None,
):
    """Record an audit log entry.

    Args:
        action: create, update, delete, login, logout, export, etc.
        entity_type: lead, deal, user, tenant, proposal, etc.
    """
    try:
        entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
        )
        if entity_id and hasattr(entry, "entity_id"):
            entry.entity_id = entity_id
        if changes and hasattr(entry, "changes"):
            entry.changes = changes
        if ip_address and hasattr(entry, "ip_address"):
            entry.ip_address = ip_address
        db.add(entry)
    except Exception as e:
        logger.warning("Failed to write audit log: %s", e)

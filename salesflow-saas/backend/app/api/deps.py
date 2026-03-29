"""Backward-compatible re-export. Use app.api.v1.deps directly."""
from app.api.v1.deps import get_current_user, get_current_tenant, get_db, require_role

__all__ = ["get_current_user", "get_current_tenant", "get_db", "require_role"]

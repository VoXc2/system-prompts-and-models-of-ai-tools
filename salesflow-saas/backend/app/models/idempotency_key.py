"""Idempotency Key — prevent duplicate side effects on retried requests."""

from __future__ import annotations

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import TenantModel


class IdempotencyKey(TenantModel):
    __tablename__ = "idempotency_keys"

    key = Column(String(128), nullable=False, unique=True, index=True)
    endpoint = Column(String(255), nullable=False)
    request_hash = Column(String(64), nullable=False)  # SHA256 of request body
    response = Column(JSONB, default=dict)
    status_code = Column(String(8), default="200")
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

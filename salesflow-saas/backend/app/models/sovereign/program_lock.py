"""Platform-level program lock (not tenant-scoped)."""

from sqlalchemy import Column, String, Text, Boolean, Integer

from app.models.base import BaseModel
from app.models.compat import JSONB


class SovereignProgramLock(BaseModel):
    __tablename__ = "sovereign_program_locks"

    version = Column(Integer, nullable=False, default=1)
    lock_config = Column(JSONB, nullable=False)
    locked_by = Column(String(200), nullable=False)
    reason = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

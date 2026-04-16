"""Sovereign compliance check results."""

from sqlalchemy import Column, String, Boolean

from app.models.base import TenantModel
from app.models.compat import JSONB


class SovereignComplianceCheck(TenantModel):
    __tablename__ = "sovereign_compliance_checks"

    framework = Column(String(50), nullable=False, index=True)
    check_type = Column(String(100), nullable=False)
    target_id = Column(String(200), nullable=True)
    compliant = Column(Boolean, nullable=False)
    findings = Column(JSONB, default=list)
    findings_ar = Column(JSONB, default=list)
    recommendations = Column(JSONB, default=list)
    recommendations_ar = Column(JSONB, default=list)

from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
from app.models.base import TenantModel


class Playbook(TenantModel):
    """Industry-specific revenue playbook for B2B sectors.

    Represents the 4 core Revenue Engine offers:
    - Revenue Engine Setup
    - Managed Pipeline Growth
    - AI Sales Operating System
    - Outbound & Reactivation Program

    With sector-specific templates for Tier A industries:
    clinics/healthcare, real estate, B2B services, training/education, industrial suppliers.
    """
    __tablename__ = "playbooks"

    name = Column(String(255), nullable=False)
    name_ar = Column(String(255))
    industry = Column(String(100), nullable=False, index=True)  # healthcare, real_estate, b2b_services, training, industrial
    product_type = Column(String(100), nullable=False, index=True)  # revenue_engine_setup, managed_pipeline, ai_sales_os, outbound_reactivation
    tier = Column(String(20), default="A", index=True)  # A, B, C sector tier
    description = Column(Text)
    description_ar = Column(Text)

    # Revenue model
    setup_fee = Column(Numeric(12, 2), default=0)
    monthly_fee = Column(Numeric(12, 2), default=0)
    performance_percentage = Column(Numeric(5, 2), default=0)  # % of revenue upside
    currency = Column(String(3), default="SAR")

    # Playbook content
    target_persona = Column(JSONB, default=dict)  # {"title": "...", "pain_points": [...], "triggers": [...]}
    outreach_sequence = Column(JSONB, default=list)  # [{"channel": "whatsapp", "template": "...", "delay_hours": 0}, ...]
    qualification_criteria = Column(JSONB, default=dict)  # {"budget_min": ..., "company_size": ..., "signals": [...]}
    content_templates = Column(JSONB, default=list)  # [{"type": "email|whatsapp|social", "subject": "...", "body": "..."}]
    kpi_targets = Column(JSONB, default=dict)  # {"meetings_per_month": 20, "pipeline_value": 500000, "win_rate": 25}
    sales_cycle_days = Column(Integer, default=30)

    # Pipeline stages override (if different from default)
    custom_stages = Column(JSONB, default=list)  # ["discovery", "demo", "proposal", "negotiation", "closed"]

    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

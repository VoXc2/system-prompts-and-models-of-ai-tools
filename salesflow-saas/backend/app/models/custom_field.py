"""Tenant-defined custom fields."""
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from app.models.base import TenantModel


class CustomField(TenantModel):
    """Custom field definition for a tenant."""
    __tablename__ = "custom_fields"

    entity_type = Column(String(50), nullable=False)  # lead, customer, deal, property
    field_name = Column(String(100), nullable=False)
    field_label = Column(String(255), nullable=False)
    field_label_ar = Column(String(255))
    field_type = Column(String(50), nullable=False)  # text, number, date, select, multiselect, boolean, url, phone, email
    options = Column(JSONB, default=list)  # For select/multiselect: list of options
    is_required = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    default_value = Column(String(500))
    placeholder = Column(String(255))
    settings = Column(JSONB, default=dict)

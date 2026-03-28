"""Tags and segments for organizing contacts."""
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import TenantModel


class Tag(TenantModel):
    """Flexible tag for leads, customers, deals."""
    __tablename__ = "tags"

    name = Column(String(100), nullable=False)
    color = Column(String(7), default="#6B7280")  # Hex color
    entity_type = Column(String(50))  # lead, customer, deal, conversation
    usage_count = Column(Integer, default=0)


class Segment(TenantModel):
    """Dynamic segment/smart list of contacts."""
    __tablename__ = "segments"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    segment_type = Column(String(50), default="dynamic")  # static, dynamic
    entity_type = Column(String(50), default="lead")  # lead, customer
    filters = Column(JSONB, default=dict)  # Dynamic filter criteria
    member_count = Column(Integer, default=0)
    settings = Column(JSONB, default=dict)

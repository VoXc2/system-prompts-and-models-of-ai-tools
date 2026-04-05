"""Persistence for aggregated marketing / market text intelligence (no raw message bodies)."""

from sqlalchemy import Column, String

from app.models.base import TenantModel
from app.models.compat import JSONB


class TextIntelligenceMarketInsight(TenantModel):
    """Themes extracted from reviews, competitor pages, ads, etc. — lawful, aggregate-only."""

    __tablename__ = "text_intel_market_insights"

    scope = Column(String(120), nullable=False, index=True)
    insights_json = Column(JSONB, default=dict)
    source_fingerprint = Column(String(64), nullable=True)

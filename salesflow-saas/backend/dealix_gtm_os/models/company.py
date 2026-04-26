from pydantic import BaseModel, Field
from typing import Optional

class CompanyInput(BaseModel):
    name: str
    website: Optional[str] = None
    sector: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class CompanyIntelligence(BaseModel):
    name: str
    website: Optional[str] = None
    sector: str
    city: str = ""
    business_summary: str
    products_services: list[str] = Field(default_factory=list)
    target_customers: list[str] = Field(default_factory=list)
    revenue_model: str = ""
    lead_channels: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    partnership_potential: str = ""
    opportunity_types: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    confidence: float = 0.5

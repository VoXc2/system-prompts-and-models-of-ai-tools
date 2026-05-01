"""Pydantic schemas for API requests/responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ══════════════════════════════════════════════════════════════
# Common
# ══════════════════════════════════════════════════════════════
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    env: str
    providers: list[str]


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


# ══════════════════════════════════════════════════════════════
# Leads (Phase 8)
# ══════════════════════════════════════════════════════════════
class LeadCreateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    company: str = Field(..., min_length=1, max_length=200)
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr | None = None
    phone: str | None = None
    sector: str | None = None
    company_size: str | None = None
    region: str | None = "Saudi Arabia"
    budget: float | None = None
    message: str | None = None
    locale: str | None = None
    source: str = "website"


class LeadResponse(BaseModel):
    id: str
    source: str
    company_name: str
    contact_name: str
    contact_email: str | None
    contact_phone: str | None
    sector: str | None
    region: str | None
    status: str
    fit_score: float
    urgency_score: float
    pain_points: list[str]
    locale: str
    created_at: datetime


class PipelineResponse(BaseModel):
    lead: LeadResponse
    fit_score: dict[str, Any] | None
    extraction: dict[str, Any] | None
    qualification: dict[str, Any] | None
    crm_sync: dict[str, Any] | None
    booking: dict[str, Any] | None
    proposal: dict[str, Any] | None
    warnings: list[str]


# ══════════════════════════════════════════════════════════════
# Sales
# ══════════════════════════════════════════════════════════════
class SalesScriptRequest(BaseModel):
    sector: str
    locale: str = Field(default="ar", pattern="^(ar|en)$")
    script_type: str = Field(
        default="opener",
        description="opener | follow_up_1 | follow_up_2 | demo_confirm | proposal_cover",
    )
    name: str = ""
    company: str = ""


class SalesScriptResponse(BaseModel):
    script: str
    locale: str
    script_type: str


class ProposalRequest(BaseModel):
    lead_id: str | None = None
    company_name: str
    sector: str
    pain_points: list[str] = []
    outcomes: list[str] = []
    budget_hint: float | None = None
    locale: str = "ar"
    region: str = "Saudi Arabia"


class ProposalResponse(BaseModel):
    id: str
    lead_id: str
    company_name: str
    body_markdown: str
    budget_min: float
    budget_max: float
    currency: str
    valid_until: datetime
    created_at: datetime


# ══════════════════════════════════════════════════════════════
# Sectors (Phase 9)
# ══════════════════════════════════════════════════════════════
class SectorIntelResponse(BaseModel):
    sector: str
    market_size_sar: float
    market_size_sar_formatted: str
    growth_rate: float
    key_players: list[str]
    pain_points: list[str]
    opportunities: list[str]
    ai_readiness: float
    regulations: list[str]
    trends: list[str]
    vision_2030_alignment: str


class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    content_type: str = "article"
    channel: str = "blog"
    locale: str = "ar"
    length: int | None = None


class ContentResponse(BaseModel):
    id: str
    content_type: str
    channel: str
    locale: str
    topic: str
    title: str
    body_markdown: str
    word_count: int
    tags: list[str]
    cta: str
    created_at: datetime

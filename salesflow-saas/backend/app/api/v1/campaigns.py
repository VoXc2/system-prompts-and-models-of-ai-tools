"""Campaign management and attribution API."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_active_user, get_db
from app.models.campaign import Campaign, LeadSource
from app.models.lead import Lead

router = APIRouter()


class CampaignCreate(BaseModel):
    name: str
    campaign_type: str = "manual"
    channel: Optional[str] = None
    target_industry: Optional[str] = None
    budget: Optional[float] = None
    currency: str = "SAR"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_criteria: Optional[dict] = None
    settings: Optional[dict] = None


@router.post("/")
async def create_campaign(
    req: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Create a new campaign."""
    campaign = Campaign(
        id=uuid.uuid4(),
        tenant_id=current_user["tenant_id"],
        name=req.name,
        campaign_type=req.campaign_type,
        channel=req.channel,
        target_industry=req.target_industry,
        budget=req.budget,
        currency=req.currency,
        status="draft",
        target_criteria=req.target_criteria or {},
        settings=req.settings or {},
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    return {
        "status": "created",
        "campaign": {
            "id": str(campaign.id),
            "name": campaign.name,
            "type": campaign.campaign_type,
            "channel": campaign.channel,
            "status": campaign.status,
        },
    }


@router.get("/")
async def list_campaigns(
    status_filter: Optional[str] = None,
    channel: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """List all campaigns with metrics."""
    tenant_id = current_user["tenant_id"]

    query = select(Campaign).where(Campaign.tenant_id == tenant_id)
    count_query = select(func.count(Campaign.id)).where(Campaign.tenant_id == tenant_id)

    if status_filter:
        query = query.where(Campaign.status == status_filter)
        count_query = count_query.where(Campaign.status == status_filter)
    if channel:
        query = query.where(Campaign.channel == channel)
        count_query = count_query.where(Campaign.channel == channel)

    query = query.order_by(Campaign.created_at.desc()).offset(offset).limit(limit)

    result = await db.execute(query)
    campaigns = result.scalars().all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    return {
        "campaigns": [
            {
                "id": str(c.id),
                "name": c.name,
                "campaign_type": c.campaign_type,
                "channel": c.channel,
                "status": c.status,
                "budget": float(c.budget) if c.budget else None,
                "currency": c.currency,
                "start_date": str(c.start_date) if c.start_date else None,
                "end_date": str(c.end_date) if c.end_date else None,
                "target_industry": c.target_industry,
                "impressions": c.impressions,
                "clicks": c.clicks,
                "leads_generated": c.leads_generated,
                "deals_closed": c.deals_closed,
                "revenue_generated": float(c.revenue_generated) if c.revenue_generated else 0,
                "cost_per_lead": float(c.cost_per_lead) if c.cost_per_lead else None,
                "created_at": str(c.created_at) if c.created_at else None,
            }
            for c in campaigns
        ],
        "total": total,
    }


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get campaign details with metrics."""
    tenant_id = current_user["tenant_id"]

    result = await db.execute(
        select(Campaign).where(
            Campaign.id == campaign_id,
            Campaign.tenant_id == tenant_id,
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الحملة غير موجودة",
        )

    # Count leads linked to this campaign via LeadSource
    leads_count_result = await db.execute(
        select(func.count(LeadSource.id)).where(
            LeadSource.campaign_id == campaign.id,
            LeadSource.tenant_id == tenant_id,
        )
    )
    leads_count = leads_count_result.scalar() or 0

    return {
        "campaign": {
            "id": str(campaign.id),
            "name": campaign.name,
            "campaign_type": campaign.campaign_type,
            "channel": campaign.channel,
            "status": campaign.status,
            "budget": float(campaign.budget) if campaign.budget else None,
            "currency": campaign.currency,
            "start_date": str(campaign.start_date) if campaign.start_date else None,
            "end_date": str(campaign.end_date) if campaign.end_date else None,
            "target_industry": campaign.target_industry,
            "target_criteria": campaign.target_criteria,
            "settings": campaign.settings,
            "created_at": str(campaign.created_at) if campaign.created_at else None,
            "updated_at": str(campaign.updated_at) if campaign.updated_at else None,
        },
        "metrics": {
            "impressions": campaign.impressions,
            "clicks": campaign.clicks,
            "leads_generated": campaign.leads_generated,
            "leads_linked": leads_count,
            "deals_closed": campaign.deals_closed,
            "revenue_generated": float(campaign.revenue_generated) if campaign.revenue_generated else 0,
            "cost_per_lead": float(campaign.cost_per_lead) if campaign.cost_per_lead else None,
        },
    }


@router.get("/{campaign_id}/leads")
async def get_campaign_leads(
    campaign_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
):
    """Get leads generated from a campaign."""
    tenant_id = current_user["tenant_id"]

    # Verify campaign belongs to tenant
    campaign_result = await db.execute(
        select(Campaign.id).where(
            Campaign.id == campaign_id,
            Campaign.tenant_id == tenant_id,
        )
    )
    if not campaign_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="الحملة غير موجودة",
        )

    # Get leads via LeadSource join
    query = (
        select(Lead, LeadSource)
        .join(LeadSource, Lead.id == LeadSource.lead_id)
        .where(
            LeadSource.campaign_id == campaign_id,
            LeadSource.tenant_id == tenant_id,
        )
        .order_by(Lead.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    count_query = select(func.count(LeadSource.id)).where(
        LeadSource.campaign_id == campaign_id,
        LeadSource.tenant_id == tenant_id,
    )

    result = await db.execute(query)
    rows = result.all()

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    leads = []
    for lead, source in rows:
        leads.append({
            "id": str(lead.id),
            "name": lead.name,
            "phone": lead.phone,
            "email": lead.email,
            "status": lead.status,
            "score": lead.score,
            "source": {
                "source": source.source,
                "medium": source.medium,
                "utm_source": source.utm_source,
                "utm_medium": source.utm_medium,
                "utm_campaign": source.utm_campaign,
            },
            "created_at": str(lead.created_at) if lead.created_at else None,
        })

    return {"campaign_id": campaign_id, "leads": leads, "total": total}

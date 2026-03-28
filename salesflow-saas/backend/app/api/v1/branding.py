"""Tenant branding and settings API."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.tenant import Tenant

router = APIRouter()


# --------------- Schemas ---------------

class BrandingSettings(BaseModel):
    primary_color: str = "#0D9488"
    secondary_color: str = "#F59E0B"
    logo_url: Optional[str] = None
    seal_url: Optional[str] = None
    tagline: str = "خلّي البيع يمشي بنظام"
    company_name: str = "ديليكس"
    font_family: str = "Cairo"
    email_header_bg: str = "#0D9488"
    email_footer_text: str = "مدعوم من Dealix"

    model_config = {"from_attributes": True}


class BrandingUpdate(BaseModel):
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    seal_url: Optional[str] = None
    tagline: Optional[str] = None
    company_name: Optional[str] = None
    font_family: Optional[str] = None
    email_header_bg: Optional[str] = None
    email_footer_text: Optional[str] = None


class LogoUpload(BaseModel):
    url: str


class BrandingPreview(BaseModel):
    subject: str
    html_preview: str
    branding: BrandingSettings


# --------------- Helpers ---------------

async def _get_tenant(db: AsyncSession, tenant_id: str) -> Tenant:
    """Fetch the tenant row or raise 404."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == UUID(tenant_id))
    )
    tenant = result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="المستأجر غير موجود")
    return tenant


def _extract_branding(tenant: Tenant) -> BrandingSettings:
    """Extract branding from tenant settings JSONB, using defaults for missing keys."""
    settings = tenant.settings or {}
    branding_data = settings.get("branding", {})
    # Override company_name from tenant.name if not set in branding
    if "company_name" not in branding_data and tenant.name:
        branding_data["company_name"] = tenant.name
    # Override logo_url from tenant.logo_url if not set in branding
    if "logo_url" not in branding_data and tenant.logo_url:
        branding_data["logo_url"] = tenant.logo_url
    return BrandingSettings(**branding_data)


async def _save_branding(db: AsyncSession, tenant: Tenant, branding: BrandingSettings) -> None:
    """Persist branding dict into tenant.settings['branding']."""
    settings = dict(tenant.settings or {})
    settings["branding"] = branding.model_dump()
    tenant.settings = settings
    await db.commit()
    await db.refresh(tenant)


# --------------- Endpoints ---------------

@router.get("", response_model=BrandingSettings)
async def get_branding(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get tenant branding settings (colors, logo, tagline, seal, company name)."""
    tenant_id = current_user["tenant_id"]
    tenant = await _get_tenant(db, tenant_id)
    return _extract_branding(tenant)


@router.put("", response_model=BrandingSettings)
async def update_branding(
    data: BrandingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update tenant branding settings."""
    tenant_id = current_user["tenant_id"]
    tenant = await _get_tenant(db, tenant_id)
    branding = _extract_branding(tenant)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(branding, field, value)

    await _save_branding(db, tenant, branding)
    return branding


@router.put("/logo", response_model=BrandingSettings)
async def upload_logo(
    data: LogoUpload,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Upload tenant logo (placeholder - accepts URL for now)."""
    tenant_id = current_user["tenant_id"]
    tenant = await _get_tenant(db, tenant_id)
    branding = _extract_branding(tenant)
    branding.logo_url = data.url

    # Also update the top-level logo_url on the tenant
    tenant.logo_url = data.url

    await _save_branding(db, tenant, branding)
    return branding


@router.get("/preview", response_model=BrandingPreview)
async def preview_branding(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Preview branding applied to an email template context."""
    tenant_id = current_user["tenant_id"]
    tenant = await _get_tenant(db, tenant_id)
    branding = _extract_branding(tenant)

    html_preview = f"""
    <div dir="rtl" style="font-family: {branding.font_family}, sans-serif; max-width: 600px; margin: auto;">
      <div style="background: {branding.email_header_bg}; padding: 20px; text-align: center;">
        {'<img src="' + branding.logo_url + '" alt="logo" style="max-height:60px;" />' if branding.logo_url else ''}
        <h1 style="color: #fff; margin: 8px 0 0;">{branding.company_name}</h1>
      </div>
      <div style="padding: 24px; background: #fff;">
        <p style="color: #374151;">مرحبًا،</p>
        <p style="color: #374151;">هذا عرض تجريبي لقالب البريد الإلكتروني بإعدادات علامتك التجارية.</p>
        <p style="color: {branding.primary_color}; font-weight: bold;">{branding.tagline}</p>
      </div>
      <div style="background: #F3F4F6; padding: 12px; text-align: center; font-size: 12px; color: #6B7280;">
        {branding.email_footer_text}
      </div>
    </div>
    """.strip()

    return BrandingPreview(
        subject=f"معاينة بريد {branding.company_name}",
        html_preview=html_preview,
        branding=branding,
    )

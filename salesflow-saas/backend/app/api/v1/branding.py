"""Tenant branding and settings API."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.api.v1.deps import get_current_user, get_db

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


# --------------- Mock Data ---------------

_mock_branding: dict[str, BrandingSettings] = {}


def _get_tenant_branding(tenant_id: str) -> BrandingSettings:
    if tenant_id not in _mock_branding:
        _mock_branding[tenant_id] = BrandingSettings()
    return _mock_branding[tenant_id]


# --------------- Endpoints ---------------

@router.get("", response_model=BrandingSettings)
async def get_branding(
    current_user: dict = Depends(get_current_user),
):
    """Get tenant branding settings (colors, logo, tagline, seal, company name)."""
    tenant_id = current_user["tenant_id"]
    return _get_tenant_branding(tenant_id)


@router.put("", response_model=BrandingSettings)
async def update_branding(
    data: BrandingUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update tenant branding settings."""
    tenant_id = current_user["tenant_id"]
    branding = _get_tenant_branding(tenant_id)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(branding, field, value)

    _mock_branding[tenant_id] = branding
    return branding


@router.put("/logo", response_model=BrandingSettings)
async def upload_logo(
    data: LogoUpload,
    current_user: dict = Depends(get_current_user),
):
    """Upload tenant logo (placeholder - accepts URL for now)."""
    tenant_id = current_user["tenant_id"]
    branding = _get_tenant_branding(tenant_id)
    branding.logo_url = data.url
    _mock_branding[tenant_id] = branding
    return branding


@router.get("/preview", response_model=BrandingPreview)
async def preview_branding(
    current_user: dict = Depends(get_current_user),
):
    """Preview branding applied to an email template context."""
    tenant_id = current_user["tenant_id"]
    branding = _get_tenant_branding(tenant_id)

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

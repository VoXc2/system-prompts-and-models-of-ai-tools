from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class ChannelType(str, Enum):
    EMAIL = "email"
    LINKEDIN_MANUAL = "linkedin_manual"
    WHATSAPP_WARM = "whatsapp_warm"
    INSTAGRAM_INBOUND = "instagram_inbound"
    X_POST = "x_post"
    X_REPLY = "x_reply"
    TIKTOK_CONTENT = "tiktok_content"
    PHONE = "phone"
    PARTNER_INTRO = "partner_intro"
    WEBSITE_FORM = "website_form"

class AutomationLevel(str, Enum):
    FULLY_AUTOMATED = "fully_automated"
    SEMI_AUTOMATED = "semi_automated"
    MANUAL_REQUIRED = "manual_required"
    PROHIBITED = "prohibited"

class OutreachMessage(BaseModel):
    target_company: str
    channel: ChannelType
    automation_level: AutomationLevel
    subject: Optional[str] = None
    first_line: str
    body: str
    cta: str
    follow_up_24h: str = ""
    follow_up_72h: str = ""
    stop_condition: str = "إذا ما يناسبكم، ردوا 'إيقاف'"
    approval_required: bool = True
    risk_flags: list[str] = Field(default_factory=list)

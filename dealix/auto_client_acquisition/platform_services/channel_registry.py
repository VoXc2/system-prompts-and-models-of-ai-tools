"""
Channel Registry — 11 supported channels with capabilities + risk profile.

Each channel declares: capabilities, beta_status, required_permissions,
allowed_actions, blocked_actions, risk_level. Used by the action policy
engine and the unified inbox.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Channel:
    """A connected channel + what it can / cannot do."""

    key: str
    label_ar: str
    label_en: str
    capabilities: tuple[str, ...]
    beta_status: str               # ga / beta / experimental / planned
    required_permissions: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    risk_level: str                # low / medium / high
    notes_ar: str = ""


# ── The 11 channels we model ────────────────────────────────────
ALL_CHANNELS: tuple[Channel, ...] = (
    Channel(
        key="whatsapp",
        label_ar="واتساب",
        label_en="WhatsApp Business / Cloud",
        capabilities=(
            "inbound_messages", "outbound_template_messages",
            "interactive_buttons_max_3", "media_send", "opt_out_handling",
        ),
        beta_status="ga",
        required_permissions=(
            "waba_account_id", "phone_number_id", "verified_business",
        ),
        allowed_actions=("draft_message", "send_with_approval", "track_reply"),
        blocked_actions=("cold_send_without_consent", "bulk_unsolicited_send"),
        risk_level="medium",
        notes_ar="حد 3 buttons تفاعلية. الإرسال البارد محظور بدون lawful basis.",
    ),
    Channel(
        key="gmail",
        label_ar="Gmail (إيميل العميل)",
        label_en="Gmail OAuth",
        capabilities=(
            "create_draft_only", "read_labeled_threads",
            "list_unsubscribe_header_attached",
        ),
        beta_status="ga",
        required_permissions=("gmail.compose",),
        allowed_actions=("create_draft", "read_thread"),
        blocked_actions=("send_without_user_click", "delete_messages"),
        risk_level="low",
        notes_ar="نكتفي بـ scope `gmail.compose`. المستخدم يضغط Send بنفسه.",
    ),
    Channel(
        key="google_calendar",
        label_ar="Google Calendar",
        label_en="Google Calendar API",
        capabilities=(
            "events_insert_with_meet", "events_list",
            "rfc5545_recurrence", "asia_riyadh_timezone",
        ),
        beta_status="ga",
        required_permissions=("calendar.events",),
        allowed_actions=("draft_event", "create_event_with_approval"),
        blocked_actions=("delete_other_attendees_events", "modify_external_events_silently"),
        risk_level="low",
        notes_ar="conferenceDataVersion=1 لإضافة Google Meet.",
    ),
    Channel(
        key="linkedin_lead_forms",
        label_ar="LinkedIn Lead Gen Forms",
        label_en="LinkedIn Lead Gen Forms API",
        capabilities=(
            "ingest_leads_from_ads", "hidden_field_tracking",
            "crm_sync",
        ),
        beta_status="beta",
        required_permissions=("r_marketing_leadgen_automation",),
        allowed_actions=("ingest_lead_form", "trigger_followup_draft"),
        blocked_actions=("scrape_profiles", "unsolicited_inmails_at_scale"),
        risk_level="low",
        notes_ar="مصدر رسمي لـ leads مؤهلة.",
    ),
    Channel(
        key="x_api",
        label_ar="X (Twitter)",
        label_en="X API v2",
        capabilities=(
            "post_tweet", "read_mentions",
            "user_lookups_basic", "webhooks_account_activity_paid",
        ),
        beta_status="experimental",
        required_permissions=("oauth2_user_context",),
        allowed_actions=("draft_post", "ingest_mention", "draft_dm_reply"),
        blocked_actions=("auto_dm_strangers", "scrape_user_lists"),
        risk_level="medium",
        notes_ar="بعض الـ webhooks Enterprise-only. نقتصر على ما تتيحه الخطة الحالية.",
    ),
    Channel(
        key="instagram_graph",
        label_ar="Instagram (Graph API)",
        label_en="Instagram Graph API",
        capabilities=(
            "read_business_messages", "publish_posts",
            "read_comments_on_owned_posts",
        ),
        beta_status="beta",
        required_permissions=("instagram_basic", "instagram_manage_messages"),
        allowed_actions=("draft_reply", "ingest_comment", "ingest_dm"),
        blocked_actions=("auto_dm_strangers", "scrape_unrelated_users"),
        risk_level="medium",
        notes_ar="فقط للحسابات Business + ما يخص العميل المتصل.",
    ),
    Channel(
        key="google_business_profile",
        label_ar="Google Business Profile",
        label_en="Google Business Profile API",
        capabilities=(
            "read_reviews", "post_replies",
            "publish_local_posts", "manage_location_info",
        ),
        beta_status="ga",
        required_permissions=("business.manage",),
        allowed_actions=("draft_review_reply", "draft_local_post"),
        blocked_actions=("delete_real_reviews"),
        risk_level="low",
        notes_ar="مهم للمتاجر والعيادات والفروع — السمعة المحلية.",
    ),
    Channel(
        key="google_sheets",
        label_ar="Google Sheets",
        label_en="Google Sheets API",
        capabilities=("read_range", "append_row", "watch_changes"),
        beta_status="ga",
        required_permissions=("spreadsheets.readonly", "spreadsheets",),
        allowed_actions=("import_contacts", "sync_pipeline", "log_actions"),
        blocked_actions=("delete_user_sheets"),
        risk_level="low",
        notes_ar="أداة مفيدة للتكامل مع عمليات العميل اليدوية.",
    ),
    Channel(
        key="crm",
        label_ar="CRM (Zoho/HubSpot/Salla/Odoo)",
        label_en="CRM via REST/SDK",
        capabilities=(
            "deal_sync", "contact_sync", "activity_log",
        ),
        beta_status="planned",
        required_permissions=("crm_api_token",),
        allowed_actions=("read_deals", "update_stage_with_approval"),
        blocked_actions=("delete_deals_silently"),
        risk_level="medium",
        notes_ar="بناء adapter لكل CRM في مرحلة لاحقة.",
    ),
    Channel(
        key="moyasar",
        label_ar="Moyasar (مدفوعات)",
        label_en="Moyasar Payments",
        capabilities=(
            "create_payment_link", "create_invoice",
            "webhook_paid_failed_refunded", "refund",
        ),
        beta_status="ga",
        required_permissions=("publishable_key", "secret_key"),
        allowed_actions=("draft_payment_link", "send_invoice_email"),
        blocked_actions=("charge_card_without_user_action"),
        risk_level="high",
        notes_ar="بطاقة العميل تُدخَل على Moyasar (PCI-safe). لا تخزين خانات.",
    ),
    Channel(
        key="website_forms",
        label_ar="نماذج الموقع",
        label_en="Website Forms",
        capabilities=("ingest_submission", "trigger_workflow"),
        beta_status="ga",
        required_permissions=("webhook_endpoint",),
        allowed_actions=("ingest_lead", "draft_thankyou_message"),
        blocked_actions=(),
        risk_level="low",
        notes_ar="مصدر leads مؤهَّلة بطبيعتها — أساس قانوني واضح.",
    ),
)


def get_channel(key: str) -> Channel | None:
    for c in ALL_CHANNELS:
        if c.key == key:
            return c
    return None


def channels_summary() -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    for c in ALL_CHANNELS:
        by_status[c.beta_status] = by_status.get(c.beta_status, 0) + 1
        by_risk[c.risk_level] = by_risk.get(c.risk_level, 0) + 1
    return {
        "total": len(ALL_CHANNELS),
        "by_beta_status": by_status,
        "by_risk_level": by_risk,
    }

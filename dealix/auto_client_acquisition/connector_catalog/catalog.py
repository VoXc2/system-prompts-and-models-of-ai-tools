"""The connector catalog — 12+ integrations Dealix exposes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Connector:
    """One external integration."""
    key: str
    label_ar: str
    label_en: str
    capability: str                  # short verb phrase
    required_scopes: tuple[str, ...]
    beta_status: str                 # "live" | "beta" | "coming_soon"
    allowed_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    risk_level: str                  # "low" | "medium" | "high"
    launch_phase: str                # "phase_1" | "phase_2" | "phase_3" | "phase_4"
    notes_ar: str = ""
    docs_url: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key, "label_ar": self.label_ar, "label_en": self.label_en,
            "capability": self.capability,
            "required_scopes": list(self.required_scopes),
            "beta_status": self.beta_status,
            "allowed_actions": list(self.allowed_actions),
            "blocked_actions": list(self.blocked_actions),
            "risk_level": self.risk_level,
            "launch_phase": self.launch_phase,
            "notes_ar": self.notes_ar,
            "docs_url": self.docs_url,
        }


ALL_CONNECTORS: tuple[Connector, ...] = (
    Connector(
        key="whatsapp_cloud",
        label_ar="واتساب",
        label_en="WhatsApp Business Cloud",
        capability="send/receive WA business messages",
        required_scopes=("messages_send", "messages_receive_webhook"),
        beta_status="beta",
        allowed_actions=("draft_message", "respond_to_inbound", "send_with_approval"),
        blocked_actions=("cold_send_without_consent", "scrape_groups"),
        risk_level="high",
        launch_phase="phase_1",
        notes_ar="ممنوع الإرسال البارد بدون opt-in واضح. PDPL.",
        docs_url="https://developers.facebook.com/docs/whatsapp",
    ),
    Connector(
        key="gmail",
        label_ar="Gmail",
        label_en="Gmail",
        capability="read/draft/send email",
        required_scopes=("gmail.compose", "gmail.modify"),
        beta_status="beta",
        allowed_actions=("create_draft", "read_label_inbox"),
        blocked_actions=("auto_send_without_approval", "delete_thread"),
        risk_level="high",
        launch_phase="phase_1",
        notes_ar="ابدأ بإنشاء drafts فقط — لا إرسال حي افتراضياً.",
        docs_url="https://developers.google.com/gmail/api",
    ),
    Connector(
        key="google_calendar",
        label_ar="تقويم Google",
        label_en="Google Calendar",
        capability="draft/insert calendar events",
        required_scopes=("calendar.events",),
        beta_status="beta",
        allowed_actions=("draft_event", "list_busy"),
        blocked_actions=("auto_insert_without_approval", "delete_event"),
        risk_level="medium",
        launch_phase="phase_1",
        notes_ar="إدراج الموعد يحتاج موافقة المستخدم.",
        docs_url="https://developers.google.com/workspace/calendar/api",
    ),
    Connector(
        key="google_meet",
        label_ar="Google Meet",
        label_en="Google Meet",
        capability="read transcripts",
        required_scopes=("meetings.space.readonly", "conferenceRecords.readonly"),
        beta_status="beta",
        allowed_actions=("read_transcript_with_consent",),
        blocked_actions=("realtime_listen_without_consent",),
        risk_level="high",
        launch_phase="phase_2",
        notes_ar="قراءة transcripts فقط بعد موافقة كل المشاركين.",
        docs_url="https://developers.google.com/meet/api",
    ),
    Connector(
        key="moyasar",
        label_ar="مدفوعات Moyasar",
        label_en="Moyasar",
        capability="payment links + invoices",
        required_scopes=("payments.create", "invoices.create", "webhook.subscribe"),
        beta_status="beta",
        allowed_actions=("create_payment_link_draft", "create_invoice_draft"),
        blocked_actions=("auto_charge_card", "store_card_number"),
        risk_level="high",
        launch_phase="phase_1",
        notes_ar="لا يخزّن بطاقات. payment link أو invoice فقط.",
        docs_url="https://docs.moyasar.com",
    ),
    Connector(
        key="linkedin_lead_forms",
        label_ar="LinkedIn Lead Forms",
        label_en="LinkedIn Lead Gen Forms",
        capability="ingest qualified leads from ads/events",
        required_scopes=("r_ads_leadgen_automation",),
        beta_status="coming_soon",
        allowed_actions=("ingest_form_lead",),
        blocked_actions=("auto_dm_without_opt_in", "scrape_profiles"),
        risk_level="medium",
        launch_phase="phase_2",
        notes_ar="leads مصرّح بها — مدخل آمن.",
        docs_url="https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/leads",
    ),
    Connector(
        key="google_business_profile",
        label_ar="Google Business Profile",
        label_en="Google Business Profile",
        capability="manage reviews + posts",
        required_scopes=("business.manage", "reviews.read"),
        beta_status="coming_soon",
        allowed_actions=("read_reviews", "draft_review_reply"),
        blocked_actions=("auto_publish_review_reply",),
        risk_level="medium",
        launch_phase="phase_2",
        notes_ar="أساسي للمتاجر/العيادات والسمعة المحلية.",
        docs_url="https://developers.google.com/my-business",
    ),
    Connector(
        key="x_api",
        label_ar="X (Twitter)",
        label_en="X API",
        capability="ingest mentions + DMs (with permission)",
        required_scopes=("tweet.read", "users.read", "dm.read"),
        beta_status="coming_soon",
        allowed_actions=("read_mentions", "ingest_dm_with_consent"),
        blocked_actions=("scrape_firehose", "auto_dm_strangers"),
        risk_level="high",
        launch_phase="phase_3",
        notes_ar="حسب خطة الـ API — لا scraping.",
        docs_url="https://docs.x.com/x-api/overview",
    ),
    Connector(
        key="instagram_graph",
        label_ar="Instagram",
        label_en="Instagram Graph API",
        capability="ingest comments + DMs",
        required_scopes=("instagram_manage_comments", "instagram_manage_messages"),
        beta_status="coming_soon",
        allowed_actions=("read_comments", "draft_reply"),
        blocked_actions=("auto_publish_reply",),
        risk_level="high",
        launch_phase="phase_3",
        notes_ar="الموافقة على الرد قبل النشر.",
        docs_url="https://developers.facebook.com/docs/instagram-api",
    ),
    Connector(
        key="google_sheets",
        label_ar="Google Sheets",
        label_en="Google Sheets",
        capability="read/write structured lists",
        required_scopes=("sheets.read", "sheets.write_with_approval"),
        beta_status="beta",
        allowed_actions=("read_sheet", "append_with_approval"),
        blocked_actions=("auto_overwrite_without_approval",),
        risk_level="low",
        launch_phase="phase_1",
        notes_ar="مصدر leads ووجهة لتقارير ProofPack.",
        docs_url="https://developers.google.com/sheets/api",
    ),
    Connector(
        key="crm_generic",
        label_ar="CRM",
        label_en="CRM (HubSpot/Salesforce/Zoho/etc)",
        capability="sync contacts + opportunities",
        required_scopes=("crm.contacts", "crm.opportunities"),
        beta_status="beta",
        allowed_actions=("read_contacts", "draft_opportunity"),
        blocked_actions=("delete_contact", "auto_overwrite_owner"),
        risk_level="medium",
        launch_phase="phase_2",
        notes_ar="مصدر pipeline — متوافق مع CRM متعددة.",
        docs_url="",
    ),
    Connector(
        key="website_forms",
        label_ar="نماذج الموقع",
        label_en="Website Forms",
        capability="ingest form submissions",
        required_scopes=("webhook.receive",),
        beta_status="live",
        allowed_actions=("ingest_form_submission",),
        blocked_actions=(),
        risk_level="low",
        launch_phase="phase_1",
        notes_ar="مصدر leads مملوك للعميل — أكثر أماناً.",
        docs_url="",
    ),
    Connector(
        key="composio",
        label_ar="Composio (اختياري)",
        label_en="Composio Integration Backend",
        capability="managed auth + 500+ toolkits",
        required_scopes=("composio.toolkit",),
        beta_status="coming_soon",
        allowed_actions=("delegated_tool_call_with_approval",),
        blocked_actions=("bypass_dealix_policy",),
        risk_level="medium",
        launch_phase="phase_4",
        notes_ar="يُستخدم خلف Dealix Tool Gateway فقط — لا يُفتح مباشرة.",
        docs_url="https://docs.composio.dev",
    ),
    Connector(
        key="mcp_gateway",
        label_ar="MCP Gateway (اختياري)",
        label_en="Model Context Protocol Gateway",
        capability="standardized tool/data access",
        required_scopes=("mcp.tools",),
        beta_status="coming_soon",
        allowed_actions=("delegated_tool_call_with_approval",),
        blocked_actions=("execute_arbitrary_command", "open_unrestricted_tools"),
        risk_level="high",
        launch_phase="phase_4",
        notes_ar="MCP مفتوحة خطرة — تُستخدم بـ allowlist صارم فقط.",
        docs_url="https://modelcontextprotocol.io",
    ),
)


def get_connector(key: str) -> Connector | None:
    return next((c for c in ALL_CONNECTORS if c.key == key), None)


def list_connectors() -> dict[str, object]:
    return {
        "total": len(ALL_CONNECTORS),
        "connectors": [c.to_dict() for c in ALL_CONNECTORS],
    }


def catalog_summary() -> dict[str, object]:
    by_phase: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    for c in ALL_CONNECTORS:
        by_phase[c.launch_phase] = by_phase.get(c.launch_phase, 0) + 1
        by_status[c.beta_status] = by_status.get(c.beta_status, 0) + 1
        by_risk[c.risk_level] = by_risk.get(c.risk_level, 0) + 1
    return {
        "total": len(ALL_CONNECTORS),
        "by_launch_phase": by_phase,
        "by_beta_status": by_status,
        "by_risk_level": by_risk,
    }

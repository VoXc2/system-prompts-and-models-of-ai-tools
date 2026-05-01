"""Per-connector risk dossier — Arabic, deterministic."""

from __future__ import annotations

from .catalog import ALL_CONNECTORS, get_connector

CONNECTOR_RISKS_AR: dict[str, list[str]] = {
    "whatsapp_cloud": [
        "PDPL: لا تواصل بدون opt-in واضح.",
        "نسبة بلاغ مرتفعة قد توقف الرقم.",
        "Pricing per-conversation — راقب التكلفة.",
    ],
    "gmail": [
        "إرسال خاطئ يضر سمعة الـ domain.",
        "scopes واسعة قد تكشف بيانات حساسة.",
        "ابدأ بإنشاء drafts فقط.",
    ],
    "google_calendar": [
        "إدراج موعد بدون موافقة يخرّب جدول العميل.",
        "احذر تسريب بيانات الحضور.",
    ],
    "google_meet": [
        "قراءة transcripts بدون موافقة الجميع تنتهك الخصوصية.",
        "PDPL + توافق دولي للضيوف.",
    ],
    "moyasar": [
        "لا يخزّن بيانات بطاقة داخل Dealix.",
        "أي charge بدون user_confirmed يجب أن يُحظر.",
    ],
    "linkedin_lead_forms": [
        "Compliance with LinkedIn lead automation T&Cs.",
        "اعرف source كل lead قبل التواصل.",
    ],
    "google_business_profile": [
        "ردود تلقائية على reviews تخلق مشاكل قانونية.",
        "احتفظ بـ review/reply ledger.",
    ],
    "x_api": [
        "خطة الـ API تحدد ما هو متاح فعلاً.",
        "scraping مخالف للـ ToS.",
    ],
    "instagram_graph": [
        "DMs الباردة محظورة.",
        "Comments العامة آمنة، DMs تحتاج صلاحيات.",
    ],
    "google_sheets": [
        "كتابة عشوائية تتلف بيانات العميل.",
        "اطلب موافقة قبل overwrite.",
    ],
    "crm_generic": [
        "مزامنة مفتوحة قد تكتب owner خاطئ.",
        "اقرأ أولاً، اكتب draft فقط.",
    ],
    "website_forms": [
        "بيانات تأتي من جهة العميل — أقل خطر.",
    ],
    "composio": [
        "أي tool خلف Composio يجب أن يمر من Dealix policy أولاً.",
    ],
    "mcp_gateway": [
        "MCP مفتوحة + tools بدون allowlist = تنفيذ أوامر خطر.",
        "حافظ على allowlist + audit + approval.",
    ],
}


def connector_risks(key: str) -> list[str]:
    """Risks for a single connector. Empty if connector unknown."""
    if get_connector(key) is None:
        return []
    return list(CONNECTOR_RISKS_AR.get(key, []))


def all_risks() -> dict[str, list[str]]:
    """Risks for every catalogued connector."""
    return {c.key: list(CONNECTOR_RISKS_AR.get(c.key, [])) for c in ALL_CONNECTORS}

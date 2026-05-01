"""
Safe Actions — proposed actions the user can take with one click.

Every proposed action passes through the same Orchestrator policy
gates as autonomous workflows. The Copilot never runs an action
without going through that approval flow.

Each action has:
  - title_ar (Arabic button label)
  - intent (which intent triggered it)
  - workflow_id (which orchestrator workflow to invoke, if any)
  - parameters (filled into the orchestrator request)
  - safety_class (read_only / draft_only / write_with_approval / autonomous)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.copilot.intent_router import Intent


@dataclass
class SafeAction:
    """A proposed action — user clicks → orchestrator decides whether to execute."""

    action_id: str
    title_ar: str
    description_ar: str
    safety_class: str           # read_only / draft_only / write_with_approval / autonomous
    workflow_id: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    expected_outcome_ar: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "title_ar": self.title_ar,
            "description_ar": self.description_ar,
            "safety_class": self.safety_class,
            "workflow_id": self.workflow_id,
            "parameters": self.parameters,
            "expected_outcome_ar": self.expected_outcome_ar,
        }


# ── The catalog of safe actions Copilot can propose ─────────────
SAFE_ACTIONS: tuple[SafeAction, ...] = (
    SafeAction(
        action_id="run_daily_growth",
        title_ar="شغّل Autopilot Daily Run الآن",
        description_ar="ابدأ workflow اليوم الكامل (8 خطوات) — يقف عند الإرسال للموافقة.",
        safety_class="write_with_approval",
        workflow_id="daily_growth_run",
        expected_outcome_ar="200 lead، 40 مؤهل، 38 draft جاهز للموافقة",
    ),
    SafeAction(
        action_id="show_at_risk",
        title_ar="أعرض الصفقات المعرضة للخطر",
        description_ar="استدعاء DealHealthProjection لكل الصفقات المفتوحة + ترتيب حسب المخاطر.",
        safety_class="read_only",
        expected_outcome_ar="قائمة مرتبة بالمخاطر + الإجراء الموصى به",
    ),
    SafeAction(
        action_id="generate_proof_pack",
        title_ar="ولّد Proof Pack هذا الشهر",
        description_ar="استخراج ROI proof pack شهري قابل للإرسال للإدارة.",
        safety_class="read_only",
        expected_outcome_ar="ملف Markdown + PDF جاهز للتحميل",
    ),
    SafeAction(
        action_id="draft_multi_thread",
        title_ar="اكتب رسالة multi-thread للصفقات الجامدة",
        description_ar="إعداد drafts لـ DM آخر داخل كل حساب جامد — تتطلب مراجعتك.",
        safety_class="draft_only",
        workflow_id=None,
        expected_outcome_ar="Drafts بالعربي معدّة لكل صفقة — لن تُرسل بدون موافقتك",
    ),
    SafeAction(
        action_id="show_market_radar",
        title_ar="افتح Market Radar",
        description_ar="عرض القطاعات الصاعدة + أعلى 20 شركة في السوق هذا الأسبوع.",
        safety_class="read_only",
        expected_outcome_ar="لوحة Saudi Buying Intent Map + opportunity feed",
    ),
    SafeAction(
        action_id="explain_block",
        title_ar="اشرح لماذا حُظر هذا التواصل",
        description_ar="استدعاء سجل Compliance + lawful basis check للقائمة المحظورة.",
        safety_class="read_only",
        expected_outcome_ar="تقرير سبب كل حظر + كيفية معالجته",
    ),
    SafeAction(
        action_id="forecast_30d",
        title_ar="توقعات 30 يوم القادمة",
        description_ar="حساب forecast best/likely/worst + المخاطر المؤثرة.",
        safety_class="read_only",
        expected_outcome_ar="3 سيناريوهات + قائمة المخاطر",
    ),
    SafeAction(
        action_id="pause_autopilot",
        title_ar="أوقف Autopilot مؤقتاً",
        description_ar="إيقاف كل الـ workflows الآلية حتى إعادة تشغيلها يدوياً.",
        safety_class="autonomous",
        expected_outcome_ar="كل الـ pending tasks تُلغى، لا تواصل خارجي حتى تتم إعادة التشغيل",
    ),
    SafeAction(
        action_id="find_lookalikes",
        title_ar="ابحث عن شركات مشابهة لأفضل عملائنا",
        description_ar="تشغيل lookalike engine على top-20 customers + إشارات شراء حالية.",
        safety_class="read_only",
        expected_outcome_ar="قائمة 50 شركة مشابهة + Why-Now لكل منها",
    ),
)


# ── Mapping intents → likely-relevant actions ────────────────────
_INTENT_TO_ACTIONS: dict[str, tuple[str, ...]] = {
    "what_to_do_today": ("run_daily_growth", "show_at_risk", "show_market_radar"),
    "show_revenue_leaks": ("show_at_risk", "draft_multi_thread", "explain_block"),
    "show_at_risk_deals": ("show_at_risk", "draft_multi_thread"),
    "show_market_radar": ("show_market_radar", "find_lookalikes"),
    "forecast_revenue": ("forecast_30d", "show_at_risk"),
    "explain_compliance_block": ("explain_block",),
    "find_lookalikes": ("find_lookalikes",),
    "stop_or_disable": ("pause_autopilot",),
    "generate_proof_pack": ("generate_proof_pack",),
}


def propose_actions(
    *,
    intent: Intent,
    customer_id: str,
    context: dict[str, Any],
    max_actions: int = 3,
) -> list[SafeAction]:
    """Return up to N actions relevant to the intent, in priority order."""
    action_ids = _INTENT_TO_ACTIONS.get(intent.intent_id, ())
    if not action_ids:
        # General help — always offer the 3 most useful read-only actions
        action_ids = ("show_at_risk", "show_market_radar", "forecast_30d")
    by_id = {a.action_id: a for a in SAFE_ACTIONS}
    return [by_id[aid] for aid in action_ids[:max_actions] if aid in by_id]


def get_action(action_id: str) -> SafeAction | None:
    for a in SAFE_ACTIONS:
        if a.action_id == action_id:
            return a
    return None

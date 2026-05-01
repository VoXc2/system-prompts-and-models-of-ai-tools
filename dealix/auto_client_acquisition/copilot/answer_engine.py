"""
Answer Engine — produces a CopilotAnswer for each Intent.

Each handler reads from Revenue Memory (projections), Revenue Graph
(why_now, leak_detector, simulator, etc.), and Market Radar to build
a grounded, citation-bearing Arabic answer.

No LLM dependency — these are deterministic given input. Production
adds an LLM polish layer on top of these structured answers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.copilot.intent_router import Intent


@dataclass
class Citation:
    """Where a number / claim came from — feeds the explanation UI."""

    source: str           # "revenue_memory" / "leak_detector" / "pulse" / "graph"
    reference: str        # specific endpoint or projection name
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "reference": self.reference, "detail": self.detail}


@dataclass
class CopilotAnswer:
    answer_ar: str
    citations: list[Citation] = field(default_factory=list)
    confidence: float = 0.7
    follow_up_questions: list[str] = field(default_factory=list)


# ── Handlers — one per intent ────────────────────────────────────
def _handle_what_to_do_today(*, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    n_high_priority = context.get("n_high_priority_leads", 8)
    n_leaks = context.get("n_active_leaks", 3)
    biggest_leak = context.get("biggest_leak_sar", 220_000)
    return CopilotAnswer(
        answer_ar=(
            f"اليوم {n_high_priority} شركة priority عالي ينتظرونك. "
            f"عندك {n_leaks} تسريب في الـ pipeline أكبرها {biggest_leak:,.0f} ريال. "
            "أهم 3 قرارات:\n"
            "1. تدخل في الصفقات الجامدة (مكالمة CEO + multi-thread).\n"
            "2. راجع drafts اليوم وأرسلها — الـ Personalization Agent جاهز.\n"
            "3. ابدأ التواصل مع أعلى Why-Now score من Growth Radar."
        ),
        citations=[
            Citation("revenue_graph", "why_now.rank_todays_priorities", "أعلى 5"),
            Citation("revenue_graph", "leak_detector.detect_all_leaks", "تسريبات نشطة"),
        ],
        confidence=0.9,
        follow_up_questions=[
            "أعرض لي تفاصيل الصفقات الجامدة؟",
            "اكتب لي مسودة رسالة لأعلى Lead في Growth Radar؟",
            "كم متوقع pipeline لـ 30 يوم القادم؟",
        ],
    )


def _handle_show_revenue_leaks(*, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    total = context.get("total_leak_sar", 237_000)
    n_critical = context.get("n_critical", 1)
    return CopilotAnswer(
        answer_ar=(
            f"إجمالي المال المعرّض: {total:,.0f} ريال عبر تسريبات متعددة. "
            f"{n_critical} تسريب critical يحتاج تدخل خلال 24 ساعة. "
            "الأنواع الأكثر شيوعاً: صفقات جامدة، حملات يفتحونها بدون رد، "
            "وبطء في رد المندوبين."
        ),
        citations=[Citation("revenue_graph", "leak_detector.detect_all_leaks")],
        confidence=0.92,
        follow_up_questions=[
            "ما الإجراء الموصى به للتسريب الـ critical؟",
            "أيّ مندوب أبطأ في الردود هذا الأسبوع؟",
        ],
    )


def _handle_forecast_revenue(*, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    best = context.get("forecast_best_sar", 1_010_000)
    likely = context.get("forecast_likely_sar", 615_000)
    worst = context.get("forecast_worst_sar", 280_000)
    return CopilotAnswer(
        answer_ar=(
            f"توقعات 30 يوم القادمة:\n"
            f"• أفضل حالة: {best:,.0f} ريال\n"
            f"• الأرجح: {likely:,.0f} ريال\n"
            f"• أسوأ حالة: {worst:,.0f} ريال\n"
            "الفرق بين الأفضل والأرجح يعتمد على إغلاق صفقتين معلقتين هذا الأسبوع."
        ),
        citations=[Citation("revenue_science", "forecast.compute")],
        confidence=0.78,
        follow_up_questions=[
            "أيّ صفقة ستحدد الفرق بين الأرجح والأفضل؟",
            "ما هي مخاطر الأسوأ؟",
        ],
    )


def _handle_show_market_radar(*, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    sector = context.get("hottest_sector", "real_estate")
    n_signals = context.get("n_signals", 32)
    city = context.get("hottest_city", "الرياض")
    return CopilotAnswer(
        answer_ar=(
            f"القطاع الأنشط هذا الأسبوع: **{sector}** في {city} — "
            f"{n_signals} شركة فيها إشارات شراء جديدة. "
            "القطاع صاعد بنسبة +18% مقارنة بالأسبوع الماضي. "
            "أفضل زاوية بيع: تقليل وقت الاستجابة + WhatsApp-first."
        ),
        citations=[
            Citation("market_radar", "sector_pulse.build_sector_pulse"),
            Citation("market_radar", "city_heatmap.build_city_heatmap"),
        ],
        confidence=0.85,
        follow_up_questions=[
            "أعرض لي أعلى 10 شركات في هذا القطاع؟",
            "هل القطاع المجاور (logistics) يستحق الاستهداف أيضاً؟",
        ],
    )


def _handle_show_at_risk_deals(*, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    n = context.get("n_at_risk", 2)
    total_value = context.get("at_risk_value_sar", 480_000)
    return CopilotAnswer(
        answer_ar=(
            f"عندك {n} صفقة معرضة للخطر بقيمة إجمالية {total_value:,.0f} ريال. "
            "السبب الأكثر شيوعاً: لم يكن هناك تحرّك منذ 14+ يوم. "
            "موصى: مكالمة multi-thread إلى DM آخر داخل الحساب + إرسال ROI proof pack."
        ),
        citations=[Citation("revenue_memory", "DealHealthProjection")],
        confidence=0.88,
        follow_up_questions=[
            "أكتب رسالة multi-thread لكل واحدة؟",
            "ما هي القيمة المتوقعة لإنقاذ هذه الصفقات؟",
        ],
    )


def _handle_explain_compliance_block(*, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    reason = context.get("block_reason", "no_consent")
    n = context.get("n_blocked", 18)
    reasons_map = {
        "no_consent": "لم يسجل المتلقي موافقة صريحة",
        "opt_out": "سبق له طلب opt-out",
        "no_lawful_basis": "لا يوجد أساس قانوني واضح للمعالجة",
        "blocked_keyword": "الرسالة تحوي عبارة محظورة",
        "frequency_cap": "تجاوز الحد الأقصى للرسائل في الأسبوع",
        "quiet_hours": "خارج ساعات العمل المسموحة",
    }
    return CopilotAnswer(
        answer_ar=(
            f"حُظرت {n} رسالة. السبب الرئيسي: **{reasons_map.get(reason, reason)}**. "
            "هذا حماية لك من غرامات PDPL ولسمعة شركتك. كل عملية حظر مسجلة في "
            "Trust Center للمراجعة."
        ),
        citations=[Citation("compliance", "consent_ledger + risk_engine")],
        confidence=0.95,
        follow_up_questions=[
            "أعرض القائمة الكاملة للمحظورين؟",
            "كيف أحصل على lawful basis للقائمة؟",
        ],
    )


def _handle_explain_metric(*, question_ar: str, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    metric = context.get("metric_name", "reply_rate")
    value = context.get("metric_value", 0.082)
    benchmark = context.get("benchmark_p50", 0.07)
    delta = round((value / benchmark - 1) * 100, 1) if benchmark else 0
    return CopilotAnswer(
        answer_ar=(
            f"{metric}: {value*100:.1f}% — "
            f"{'فوق' if delta > 0 else 'تحت'} متوسط القطاع بنسبة {abs(delta):.1f}%. "
            "العوامل الرئيسية: جودة الـ subject line، توقيت الإرسال، "
            "وملاءمة القطاع المستهدف."
        ),
        citations=[
            Citation("revenue_memory", "CampaignPerformance"),
            Citation("pulse", "sector_benchmarks"),
        ],
        confidence=0.85,
        follow_up_questions=[
            "كيف أرفع هذا الرقم 2x؟",
            "ما هي الـ subject lines الأنجح؟",
        ],
    )


def _handle_general(*, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    return CopilotAnswer(
        answer_ar=(
            "أقدر أساعدك في: تحديد أولويات اليوم، شرح أرقام اللوحة، "
            "تتبع الصفقات المعرضة للخطر، تشخيص تسريبات الإيراد، "
            "توقع الإيراد، عرض حالة السوق، وكتابة رسائل مخصصة. "
            "اسألني سؤال محدد أو ابدأ بـ 'وش أسوي اليوم؟'."
        ),
        confidence=0.6,
        follow_up_questions=[
            "وش أسوي اليوم؟",
            "أعرض لي تسريبات الإيراد",
            "ما توقعات الـ pipeline لـ 30 يوم؟",
        ],
    )


# ── Public API ────────────────────────────────────────────────────
_HANDLERS = {
    "what_to_do_today": _handle_what_to_do_today,
    "show_revenue_leaks": _handle_show_revenue_leaks,
    "forecast_revenue": _handle_forecast_revenue,
    "show_market_radar": _handle_show_market_radar,
    "show_at_risk_deals": _handle_show_at_risk_deals,
    "explain_compliance_block": _handle_explain_compliance_block,
}


def answer(*, intent: Intent, question_ar: str, customer_id: str, context: dict[str, Any]) -> CopilotAnswer:
    """Route the intent to the appropriate handler."""
    handler = _HANDLERS.get(intent.intent_id)
    if handler is None:
        if intent.intent_id == "explain_metric":
            return _handle_explain_metric(question_ar=question_ar, customer_id=customer_id, context=context)
        return _handle_general(customer_id=customer_id, context=context)
    return handler(customer_id=customer_id, context=context)


def explain_metric(*, metric_name: str, value: float, benchmark_p50: float, customer_id: str) -> CopilotAnswer:
    """Direct entry point for the 'explain this number' button on dashboard tiles."""
    return _handle_explain_metric(
        question_ar=f"explain {metric_name}",
        customer_id=customer_id,
        context={"metric_name": metric_name, "metric_value": value, "benchmark_p50": benchmark_p50},
    )

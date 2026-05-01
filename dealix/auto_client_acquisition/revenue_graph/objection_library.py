"""
Saudi Sales Objection Library — every objection + best response (Arabic + English).

Curated from real B2B sales calls + WhatsApp threads. Each objection comes with:
  - Saudi cultural context
  - Best WhatsApp response
  - Best formal response
  - When to follow up
  - Whether the lead is actually interested
  - Score impact on lead priority
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# ── Objection taxonomy ────────────────────────────────────────────
OBJECTION_CATEGORIES: tuple[str, ...] = (
    "price",
    "timing",
    "authority",
    "trust",
    "competitor",
    "fit",
    "process",
    "channel_preference",
    "skepticism",
)


@dataclass
class ObjectionResponse:
    """One objection with everything needed to respond."""

    objection_id: str
    category: str
    objection_ar: str            # the exact phrase the prospect uses
    objection_en: str
    saudi_context: str           # cultural read — what they actually mean
    whatsapp_response_ar: str
    formal_response_ar: str      # for email
    follow_up_days: int
    likely_intent: str           # "interested" / "polite_no" / "needs_education"
    priority_score_delta: float  # how much to bump or drop the lead score
    next_action: str


# ── The library — initial 25 objections, designed to grow ─────────
SAUDI_B2B_OBJECTIONS: list[ObjectionResponse] = [
    ObjectionResponse(
        objection_id="OBJ_PRICE_001",
        category="price",
        objection_ar="السعر عالي",
        objection_en="The price is high",
        saudi_context=(
            "في السعودية هذه عبارة tactical في 70% من الأحيان — لا تعني فعلاً "
            "أن السعر عالي، بل تعني 'لم تقنعني بعد بالقيمة'. لا تخصم فوراً."
        ),
        whatsapp_response_ar=(
            "حقك تركز على القيمة. خليني أوضح: في الـ 30 يوم الأولى Dealix "
            "يجيب لك من 50-80 lead مؤهل — تكلفة كل lead أقل من 60 ريال. "
            "في وكالات التسويق، نفس اللد يكلف 250+ ريال. هل نشوف الأرقام معاً؟"
        ),
        formal_response_ar=(
            "نتفهم اهتمامكم بالعائد على الاستثمار. نسعد بإرسال ROI breakdown "
            "مفصل يوضح كلفة الـ lead المؤهل لدى Dealix مقارنة بالخيارات البديلة "
            "(وكالات + أدوات أخرى). هل توافقون على إرسال الملف؟"
        ),
        follow_up_days=3,
        likely_intent="interested",
        priority_score_delta=+5,
        next_action="send_roi_breakdown",
    ),
    ObjectionResponse(
        objection_id="OBJ_PRICE_002",
        category="price",
        objection_ar="ميزانيتنا الشهر الجاي",
        objection_en="Our budget is next month",
        saudi_context=(
            "في 80% من الحالات هذه إشارة 'نعم لكن ليس الآن' — "
            "احتفظ بالتواصل لأن الميزانية تصير حقيقة في 30-45 يوم."
        ),
        whatsapp_response_ar=(
            "ممتاز — نسجلكم في تذكير 25 من الشهر القادم. وحتى ذاك الوقت، "
            "نرسل لكم Pulse الشهري مجاناً + 3 leads عينة لقطاعكم تحديداً. "
            "هل نتواصل في {next_month_date}؟"
        ),
        formal_response_ar=(
            "نتفهم تماماً. تم تسجيل تذكير للتواصل في بداية الشهر القادم. "
            "حتى ذلك الوقت، نسعد بمشاركتكم تقرير Saudi B2B Pulse الشهري + "
            "نموذج من 3 leads مؤهلة لقطاعكم بدون التزام."
        ),
        follow_up_days=30,
        likely_intent="interested",
        priority_score_delta=+3,
        next_action="schedule_followup_30d_with_pulse",
    ),
    ObjectionResponse(
        objection_id="OBJ_PRICE_003",
        category="price",
        objection_ar="ابغى خصم",
        objection_en="I want a discount",
        saudi_context=(
            "ثقافياً مهم — لكن لا تخصم مباشرة. اقترح زيادة قيمة بدلاً من تقليل سعر."
        ),
        whatsapp_response_ar=(
            "أقدر اللي تطلبه. عوضاً عن الخصم، أعطيك أكثر: "
            "أول 30 يوم تدفع على النتائج فقط — 25 ريال لكل lead مؤهل، "
            "بدون اشتراك ثابت. لو راضي، تحول للباقة الشهرية. عادل؟"
        ),
        formal_response_ar=(
            "نقدّر طلبكم. بدلاً من خصم، نقترح عرضاً أفضل: تجربة 30 يوم "
            "بنموذج Pay-per-Qualified-Lead (25 ريال/lead) — تدفعون فقط "
            "على المحقق. بعدها تحوّلون للاشتراك الشهري إذا أعجبتكم النتائج."
        ),
        follow_up_days=2,
        likely_intent="interested",
        priority_score_delta=+4,
        next_action="propose_pay_per_result_pilot",
    ),
    ObjectionResponse(
        objection_id="OBJ_TIMING_001",
        category="timing",
        objection_ar="مشغولين هذي الفترة",
        objection_en="We're busy right now",
        saudi_context=(
            "إشارة polite no في 60% من الأحيان. لكن 40% فعلاً مشغولين — "
            "اعطهم خيار اللاأحتكاكي."
        ),
        whatsapp_response_ar=(
            "متفهم تماماً. لا حاجة لاجتماع الآن — نرسل لكم 5 leads مؤهلة "
            "من قطاعكم كعينة (مجاناً) + ملف PDF يقرأه المدير في 5 دقائق "
            "حين فراغه. توافق؟"
        ),
        formal_response_ar=(
            "نقدر ظروفكم. نسعد بإرسال one-pager + قائمة بـ 5 leads مؤهلة "
            "كنموذج للقطاع، يمكن مراجعتها وقت يناسبكم بدون أي اجتماع."
        ),
        follow_up_days=14,
        likely_intent="polite_no",
        priority_score_delta=-2,
        next_action="send_lowfriction_value_pack",
    ),
    ObjectionResponse(
        objection_id="OBJ_AUTHORITY_001",
        category="authority",
        objection_ar="كلم المحاسب",
        objection_en="Talk to the accountant",
        saudi_context=(
            "في الشركات السعودية الصغيرة، المحاسب أحياناً = decision-maker الفعلي "
            "للميزانية. لكن لو الشركة كبيرة، هذه delegation غير مفيد."
        ),
        whatsapp_response_ar=(
            "تمام — قبل ما أكلم المحاسب، أحتاج فقط 5 دقائق منك لأفهم: "
            "هل المسألة في السعر؟ في القناع الزمني؟ أم في الـ ROI؟ "
            "حتى أعد للمحاسب أرقام واضحة من البداية."
        ),
        formal_response_ar=(
            "بالطبع نتواصل مع المحاسب مباشرة. للسرعة، نسعد بمشاركتنا اسم/جوال "
            "الجهة المسؤولة في القسم المالي + موافقتكم المبدئية على إرسال "
            "ROI breakdown نيابةً عنكم."
        ),
        follow_up_days=4,
        likely_intent="needs_education",
        priority_score_delta=+1,
        next_action="diagnose_objection_then_arm_internal_champion",
    ),
    ObjectionResponse(
        objection_id="OBJ_AUTHORITY_002",
        category="authority",
        objection_ar="نحتاج موافقة الإدارة/الشريك",
        objection_en="We need management/partner approval",
        saudi_context=(
            "في الشركات العائلية السعودية، 'الشريك' غالباً الأب أو الأخ الأكبر. "
            "احترام هذه الديناميكية ضروري — لا تتجاوز الشخص الذي تتحدث معه."
        ),
        whatsapp_response_ar=(
            "محترم تماماً. خليني أساعدك في التقديم: ارسل لك ملف من صفحتين "
            "بالعربي يشرح Dealix بـ ROI واضح — تقرأه أنت ثم تشاركه مع "
            "الإدارة. وإن أحبوا، نعمل اجتماع جماعي مع 3 من فريقهم. توافق؟"
        ),
        formal_response_ar=(
            "نقدّر بنية القرار لديكم. نرفق ملف تنفيذي بصفحتين باللغة "
            "العربية يلخص العرض + الـ ROI، مهيأ للعرض على الإدارة. "
            "نسعد بالتواجد في أي اجتماع داخلي لتوضيح أي استفسار."
        ),
        follow_up_days=7,
        likely_intent="interested",
        priority_score_delta=+3,
        next_action="arm_champion_with_2page_brief",
    ),
    ObjectionResponse(
        objection_id="OBJ_TRUST_001",
        category="trust",
        objection_ar="وش يضمن النتائج؟",
        objection_en="What guarantees the results?",
        saudi_context=(
            "Saudi buyer cautious بطبعه — يبحث عن منصة مع referrals. "
            "لا تعطه ضمانات بلاغية — اعطه نموذج risk-free."
        ),
        whatsapp_response_ar=(
            "سؤال ممتاز — لا أحد يضمن نتائج 100%، أي كذلك من يفعل خداع. "
            "لكن ندخل بنموذج Pay-per-Result: تدفع فقط على الـ qualified leads "
            "اللي نسلمها. لو ما جلبنا أحد، ما تدفع. هذا الـ guarantee الوحيد المعقول."
        ),
        formal_response_ar=(
            "نقدّر الحرص. نعرض عليكم نموذج Pay-per-Qualified-Lead: "
            "الدفع فقط على الـ leads المؤهلة المسلمة (25 ريال/lead). "
            "ضمان الأداء = هيكل الدفع نفسه. بدون اشتراك شهري في البداية."
        ),
        follow_up_days=2,
        likely_intent="interested",
        priority_score_delta=+5,
        next_action="propose_pay_per_result_pilot",
    ),
    ObjectionResponse(
        objection_id="OBJ_TRUST_002",
        category="trust",
        objection_ar="جربنا قبل وما نفع",
        objection_en="We tried before, didn't work",
        saudi_context=(
            "غالباً تجربتهم السابقة كانت مع agency أو أداة عامة. "
            "احصل على التفاصيل — تكشف الـ pain points الحقيقية."
        ),
        whatsapp_response_ar=(
            "متفهم — أكثر الشركات السعودية جربت أدوات لا تناسب السوق المحلي. "
            "ممكن تخبرني: مع من جربت؟ ووش كان السبب الرئيسي للفشل؟ "
            "حتى أعرف لو Dealix فعلاً يحل لك المشكلة أم لا."
        ),
        formal_response_ar=(
            "نتفهم تجربتكم السابقة. للمساعدة في التشخيص الصحيح، نسعد بفهم: "
            "(1) المزود السابق، (2) المدة، (3) السبب الجذري للنتائج. "
            "بعدها نحدد بصدق هل Dealix يعالج المشكلة فعلاً."
        ),
        follow_up_days=3,
        likely_intent="interested",
        priority_score_delta=+4,
        next_action="diagnostic_call_to_extract_root_cause",
    ),
    ObjectionResponse(
        objection_id="OBJ_TRUST_003",
        category="trust",
        objection_ar="ما اعرفكم",
        objection_en="I don't know you",
        saudi_context=(
            "Ultra-common في B2B السعودي — الثقة تأتي من معارف مشتركة. "
            "اعرض referrals + تواجد محلي."
        ),
        whatsapp_response_ar=(
            "منطقي تماماً. نحن في Dealix من السعودية، فريق 12، اشتركوا "
            "معنا 47+ شركة سعودية حالياً. تبغى نشوي 3 case studies من "
            "قطاعك تحديداً؟ + تقدر تكلم 2 من العملاء الحاليين."
        ),
        formal_response_ar=(
            "نتفهم تماماً. كمؤسسة سعودية ناشئة، نقدّر أهمية الثقة. "
            "نشاركم 3 case studies من قطاعكم + موافقة عميلين حاليين "
            "على مكالمة مرجعية مباشرة."
        ),
        follow_up_days=2,
        likely_intent="interested",
        priority_score_delta=+3,
        next_action="send_3_case_studies_plus_2_references",
    ),
    ObjectionResponse(
        objection_id="OBJ_COMPETITOR_001",
        category="competitor",
        objection_ar="عندنا مزود",
        objection_en="We have a vendor",
        saudi_context=(
            "نادراً ما يكون 'مزود' كامل — غالباً adoption ضعيف أو أداة قديمة. "
            "اسأل أسئلة محددة لتكتشف الـ gap."
        ),
        whatsapp_response_ar=(
            "ممتاز — مع مَن؟ واللي يهمني أعرفه: "
            "هل الـ leads التي يجيبها مؤهلة فعلاً (مش مجرد form fill)؟ "
            "ولو فيه فجوة، Dealix يكمّل ولا يستبدل. مجاناً نعمل audit."
        ),
        formal_response_ar=(
            "ممتاز — وجود مزود حالي يعكس النضج. نسعد بإجراء audit مجاني "
            "لمصدر الـ leads الحالي + توضيح أي فجوة محتملة. "
            "غالباً Dealix يكمّل البنية الحالية بدلاً من استبدالها."
        ),
        follow_up_days=4,
        likely_intent="needs_education",
        priority_score_delta=+2,
        next_action="offer_free_audit_position_as_complement",
    ),
    ObjectionResponse(
        objection_id="OBJ_CHANNEL_001",
        category="channel_preference",
        objection_ar="أرسل العرض واتساب",
        objection_en="Send the offer on WhatsApp",
        saudi_context=(
            "الواقع السعودي — WhatsApp = القناة الرسمية. "
            "إرسال PDF عبر WhatsApp ليس عيب، بل هو الطريقة الصحيحة."
        ),
        whatsapp_response_ar=(
            "تمام — أرسل الآن: PDF صفحتين بالعربي + voice note 90 ثانية "
            "أشرح فيه أهم 3 نقاط. أي وقت في الأسبوع القادم تفضل المتابعة؟"
        ),
        formal_response_ar=(
            "نرسل لكم العرض على WhatsApp مباشرة (PDF). للمتابعة لاحقاً، "
            "نقترح مكالمة 15 دقيقة في الأسبوع القادم لاستيضاح أي نقطة."
        ),
        follow_up_days=3,
        likely_intent="interested",
        priority_score_delta=+2,
        next_action="send_pdf_and_voice_note_via_whatsapp",
    ),
    ObjectionResponse(
        objection_id="OBJ_FIT_001",
        category="fit",
        objection_ar="مو هذا اللي نبيه",
        objection_en="Not what we want",
        saudi_context=(
            "غالباً سوء فهم في التقديم — الرسالة وصلت كأنها CRM وهم يبحثون عن agency. "
            "اعد التموضع بسرعة."
        ),
        whatsapp_response_ar=(
            "أعتذر إذا فهمت خطأ — وش اللي كنت تبحث عنه تحديداً؟ "
            "لأن Dealix ليس CRM ولا agency — هو نظام يجيب لك العملاء "
            "ويوصلهم لاجتماع. لكن خليني أتأكد قبل أكثر."
        ),
        formal_response_ar=(
            "نتفهم — يبدو أن هناك سوء فهم في التقديم. "
            "نسعد بتوضيح Dealix بطريقة مختصرة بناءً على احتياجاتكم الفعلية. "
            "ما هي الأولوية الأولى لديكم حالياً؟"
        ),
        follow_up_days=2,
        likely_intent="needs_education",
        priority_score_delta=-1,
        next_action="re_qualify_and_reposition",
    ),
    ObjectionResponse(
        objection_id="OBJ_TIMING_002",
        category="timing",
        objection_ar="بعد رمضان نشوف",
        objection_en="After Ramadan we'll see",
        saudi_context=(
            "Cultural — لكن في Q2 و Q3 السعودية تنشط بقوة بعد رمضان. "
            "اعطه قيمة الآن، تابع بعد العيد."
        ),
        whatsapp_response_ar=(
            "إن شاء الله — نسجل تذكير لـ بعد العيد بأسبوع. "
            "حتى ذاك الحين، تستلم Pulse الشهري مجاناً + benchmark قطاعك. "
            "كل عام وأنتم بخير."
        ),
        formal_response_ar=(
            "نتفهم تماماً. نسجل تذكيراً للتواصل بعد عيد الفطر بأسبوع. "
            "نسعد خلال الفترة بمشاركتكم تقرير Pulse الشهري + benchmark "
            "قطاعكم. تقبل الله طاعتكم."
        ),
        follow_up_days=35,
        likely_intent="interested",
        priority_score_delta=+1,
        next_action="schedule_post_eid_followup",
    ),
]


# ── Lookup utilities ──────────────────────────────────────────────
def find_by_keyword(keyword_ar: str) -> ObjectionResponse | None:
    """Match a free-text reply to the closest objection."""
    keyword = keyword_ar.strip()
    for obj in SAUDI_B2B_OBJECTIONS:
        if keyword in obj.objection_ar or obj.objection_ar in keyword:
            return obj
    # Fuzzy: any token overlap
    keyword_tokens = set(keyword.split())
    best: tuple[ObjectionResponse, int] | None = None
    for obj in SAUDI_B2B_OBJECTIONS:
        obj_tokens = set(obj.objection_ar.split())
        overlap = len(keyword_tokens & obj_tokens)
        if overlap == 0:
            continue
        if best is None or overlap > best[1]:
            best = (obj, overlap)
    return best[0] if best else None


def list_by_category(category: str) -> list[ObjectionResponse]:
    return [o for o in SAUDI_B2B_OBJECTIONS if o.category == category]


def category_summary() -> dict[str, int]:
    """Count objections per category — for the Library landing tile."""
    out: dict[str, int] = {}
    for o in SAUDI_B2B_OBJECTIONS:
        out[o.category] = out.get(o.category, 0) + 1
    return out

#!/usr/bin/env python3
"""
Dealix Reply Classifier — classify a prospect reply and print the matching
Khaliji Arabic response + next action + tracker fields.

Works offline (no LLM key). Based on reply_playbooks_ar.md 16 categories.

Usage:
  python scripts/dealix_reply_classifier.py "نبي نجرب"
  python scripts/dealix_reply_classifier.py < reply.txt
"""

from __future__ import annotations
import re
import sys

CALENDLY = "https://calendly.com/sami-assiri11/dealix-demo"

RULES = [
    ("interested", re.compile(r"يهم|مهم|تمام|ممتاز|أبي\s*أعرف|ابي\s*اعرف|ارسل\s*التفاصيل|interested", re.I|re.S)),
    ("wants_demo", re.compile(r"demo|ديمو|عرض|تجربة\s*مباشر", re.I|re.S)),
    ("price",      re.compile(r"كم\s*(السعر|يكلف|المبلغ)|السعر|كم\s*ريال|price|pricing", re.I|re.S)),
    ("send_details", re.compile(r"ارسل\s*(التفاصيل|deck|عرض)|تفاصيل|details|deck|presentation", re.I|re.S)),
    ("later",      re.compile(r"بعدين|لاحقاً|لاحقا|later|not\s*now|رمضان|Q\d|next\s*quarter|later|نهاية\s*السنة", re.I|re.S)),
    ("not_relevant", re.compile(r"ما\s*يناسب|مو\s*مناسب|ليس\s*لنا|not\s*relevant|غير\s*مناسب|لا\s*نحتاج", re.I|re.S)),
    ("budget_objection", re.compile(r"budget|ميزانية|ما\s*عندنا\s*فلوس|غالي|عالي", re.I|re.S)),
    ("trust_objection", re.compile(r"ما\s*نثق|مخاوف|نخاف|risk|مجازف", re.I|re.S)),
    ("already_has_crm", re.compile(r"عندنا\s*crm|have\s*crm|salesforce|hubspot|zoho", re.I|re.S)),
    ("ai_quality_concern", re.compile(r"عربي\s*مو\s*طبيعي|arabic\s*quality|chatgpt|ترجمة|ذكاء\s*اصطناعي\s*مو", re.I|re.S)),
    ("privacy_concern", re.compile(r"خصوصية|pdpl|privacy|gdpr|بيانات\s*العملاء", re.I|re.S)),
    ("arabic_concern", re.compile(r"لهجة|خليجي|مضبوط|accurate\s*arabic", re.I|re.S)),
    ("integration_concern", re.compile(r"تكامل|integration|api|webhook|zapier", re.I|re.S)),
    ("partnership_interest", re.compile(r"شراكة|partner|وكالة|reseller|affiliate", re.I|re.S)),
    ("referral_opportunity", re.compile(r"أعرف|اعرف|رشح|referral|intro|تقدر\s*تتواصل\s*مع", re.I|re.S)),
    ("timing_objection", re.compile(r"توقيت|timing|الحين|الان\s*مش|not\s*the\s*time", re.I|re.S)),
]

RESPONSES = {
    "interested": (
        "رائع. أقترح 20 دقيقة مكالمة Zoom أوضح لك كيف يشتغل. اختر موعد مناسب:\n📅 " + CALENDLY,
        "BOOK_DEMO", "reply_status=interested",
    ),
    "wants_demo": (
        "ممتاز، نسويها خلال الساعة القادمة إذا وقتك مناسب، أو اختر:\n📅 " + CALENDLY,
        "BOOK_DEMO", "reply_status=demo_requested",
    ),
    "price": (
        "3 باقات: Starter 999/شهر، Growth 2,999، Scale 7,999. الاختيار يعتمد على حجم leads عندكم. "
        "في pilot بريال واحد لمدة 7 أيام — تجرّب قبل القرار. 20 دقيقة demo وأفصّل الباقة المناسبة:\n📅 " + CALENDLY,
        "BOOK_DEMO", "reply_status=pricing_inquiry",
    ),
    "send_details": (
        "أرسلت لك one-pager سريع: https://dealix.me\n"
        "الأفضل 20 دقيقة demo — أفصّلها لـ شركتكم تحديداً. PDF generic ما يخدم قراركم:\n📅 " + CALENDLY,
        "PREPARE_DEMO_FLOW", "reply_status=info_requested",
    ),
    "later": (
        "تمام أفهم. سؤال واحد: متى الوقت المناسب يحتمل يكون؟ سأرجع لك في نفس اليوم بالظبط.",
        "FOLLOW_UP", "reply_status=deferred",
    ),
    "not_relevant": (
        "أحترم. سؤال أخير: هل عندكم شركات B2B سعودية ترون تستفيد من AI sales rep بالعربي؟ "
        "10% من MRR لـ 12 شهر لكل عميل يجي عبركم.",
        "STOP_CONTACT", "reply_status=not_interested",
    ),
    "budget_objection": (
        "صح، شهر Starter 999 صعب بدون إثبات. عرضنا الـ pilot بريال واحد لمدة 7 أيام — يدوي، "
        "قابل للاسترداد، هدفه يثبت ROI قبل أي التزام. مناسب؟",
        "ROUTE_TO_MANUAL_PAYMENT", "reply_status=budget_objection",
    ),
    "trust_objection": (
        "موقف عادل. نبدأ assist mode — AI يجهّز الرد، موظفكم يوافق قبل الإرسال. بعد 2-3 أسابيع "
        "من الجودة، تتحولون autopilot تدريجياً. صفر مخاطرة سمعة.",
        "PREPARE_DEMO_FLOW", "reply_status=trust_objection",
    ),
    "already_has_crm": (
        "CRM عندكم يخزّن leads. Dealix يرد عليهم خلال 45 ثانية بالعربي قبل ما ينسون اسم شركتكم. "
        "هم يشتغلون مع بعض. تكامل مع HubSpot/Salesforce/Zoho/أي webhook.",
        "BOOK_DEMO", "reply_status=crm_concern",
    ),
    "ai_quality_concern": (
        "صح، معظم AI العربي سيء. Dealix مبني على prompts خليجية مخصصة — ما يكتب 'حضرتك'. "
        "أرسل لك 3 أمثلة من ردود فعلية الآن. لو ما أعجبك، ما نكمل.",
        "PREPARE_DEMO_FLOW", "reply_status=ai_quality_concern",
    ),
    "privacy_concern": (
        "مصمم PDPL-compliant: بياناتكم في سيرفرات السعودية، opt-out في كل email، audit log كامل، "
        "processor agreement جاهز. أرسل compliance sheet للقانوني؟",
        "PREPARE_DEMO_FLOW", "reply_status=privacy_concern",
    ),
    "arabic_concern": (
        "خليجي حقيقي، ما يترجم. 3 أمثلة حية من conversations فعلية — أرسلها الآن. "
        "أفضل: 20 دقيقة demo تختبرها على سيناريو شركتكم:\n📅 " + CALENDLY,
        "PREPARE_DEMO_FLOW", "reply_status=arabic_concern",
    ),
    "integration_concern": (
        "HubSpot + Salesforce + Zoho + Bitrix = تكامل مباشر. أي شي ثاني = webhooks. "
        "قل لي أداتكم وأفصّل خطة الربط.",
        "RESEARCH_MORE", "reply_status=integration_concern",
    ),
    "partnership_interest": (
        "ممتاز. 3 tiers:\n"
        "- Referral: 10% MRR × 12 شهر (بدون setup)\n"
        "- Agency: setup 3-15K + 20-30% MRR دائم\n"
        "- White-label (Scale): منتج باسمكم\n"
        "20 دقيقة partner call نحدد الأنسب؟\n🤝 https://dealix.me/partners.html",
        "PREPARE_PARTNER_PITCH", "opportunity_type=AGENCY_PARTNER",
    ),
    "referral_opportunity": (
        "شكراً! 10% من MRR لـ 12 شهر لأي عميل يجي عبركم. ممكن تذكرني بمعلومات الشركة والشخص "
        "المناسب للتواصل معه؟",
        "FOLLOW_UP", "reply_status=referral_opportunity",
    ),
    "timing_objection": (
        "أفهمك. سؤال: هل عندكم كل شهر شركات جايبة leads كثيرة وتتأخرون بالرد؟ إذا نعم، كل يوم تأخير = leads تذبل. "
        "الـ pilot بريال 7 أيام — إذا شفت أثر، نكمل. إذا ما شفت، نوقف.",
        "ROUTE_TO_MANUAL_PAYMENT", "reply_status=timing_objection",
    ),
}


def classify(text: str) -> list[str]:
    text = (text or "").strip()
    matches = [name for name, rx in RULES if rx.search(text)]
    if not matches:
        matches = ["interested"]  # default — invite to demo
    return matches[:2]


def main():
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = sys.stdin.read()
    if not text.strip():
        print("usage: dealix_reply_classifier.py '<prospect reply text>'")
        sys.exit(1)

    categories = classify(text)
    print(f"━━━ CLASSIFICATION ━━━")
    for cat in categories:
        resp, action, tracker = RESPONSES.get(cat, RESPONSES["interested"])
        print(f"\n▸ Category: {cat}")
        print(f"  Next action:    {action}")
        print(f"  Tracker update: {tracker}")
        print(f"  Follow-up:      schedule +2 days if no reply")
        print(f"\n  📨 SUGGESTED RESPONSE (Khaliji):")
        print("  " + resp.replace("\n", "\n  "))
        print()


if __name__ == "__main__":
    main()

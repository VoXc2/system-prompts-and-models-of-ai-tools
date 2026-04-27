"""Content Engine — generates daily multi-platform content."""
import yaml
from pathlib import Path

_pillars_path = Path(__file__).parent.parent / "config" / "content_pillars.yaml"
_pillars = {}
if _pillars_path.exists():
    with open(_pillars_path) as f:
        _pillars = yaml.safe_load(f) or {}

LINKEDIN_TEMPLATES = [
    "كل حملة تجيب leads ثم تضيع بسبب بطء المتابعة هي ميزانية محترقة.\n\nالعميل يرسل واتساب. يتأخر الرد. ما فيه follow-up.\n\nهذا الفراغ اللي Dealix يحله.\n\n#السعودية #B2B #مبيعات",
    "60% من استفسارات العملاء في السعودية ما تُتابع خلال أول ساعة.\n\nكلّمت 50+ شركة. النتيجة واحدة: 'ما عندنا وقت نرد على الكل'\n\nالحل مو توظيف أكثر. الحل رد أذكى.",
    "سألت مدير مبيعات: 'كم lead تجيك بالشهر؟' قال 200.\n'كم ترد عليه خلال ساعة؟' قال 80.\n120 عميل محتمل ← ضاعوا.\n\nDealix يحفظ 40% منها.",
    "الوكالات اللي تقدم lead follow-up كخدمة:\n- Client retention أعلى 40%\n- إيراد إضافي 2,000+ ريال/شهر\n\nبدل ما تنتهي خدمتكم عند الإعلان، أضيفوا متابعة وتحويل.",
    "بنيت Dealix بالعربي أولاً. مو ترجمة.\nيفهم 'أبي أعرف السعر' و'وريني' و'كم؟'\n\nلأن العميل السعودي يستاهل منتج مبني له.",
]

X_TEMPLATES = [
    "الـlead ما يضيع في الإعلان. يضيع في أول 10 دقائق بعد الإعلان.",
    "مو AI يستبدل البشر. AI يرد الساعة 2 بالليل.",
    "CRM يسجّل بعد المحادثة. بس مين يبدأ المحادثة؟",
    "Pilot: 499 ريال. 7 أيام. ضمان استرداد. لأننا نثق بالمنتج.",
    "تكلفة SDR: 8,000 ريال/شهر. Dealix: 990 ريال. 24/7. بالعربي.",
]

IG_STORIES = [
    "إذا عندك واتساب مليان استفسارات — رد بكلمة Demo",
    "كم تاخذ ترد على استفسار عميل؟ (poll)",
    "قبل Dealix: 60% ضائع. بعد: 5%.",
    "Pilot 499 ريال — 7 أيام — ضمان استرداد",
    "أطلقت Dealix — يرد على عملائك خلال 45 ثانية 🚀",
]

def generate_daily_content(day_number: int = 1, theme: str = "") -> dict:
    idx = (day_number - 1) % len(LINKEDIN_TEMPLATES)
    pillars = _pillars.get("pillars", [])
    pillar = pillars[idx % len(pillars)] if pillars else {"name_ar": theme}

    return {
        "day": day_number,
        "theme": pillar.get("name_ar", theme),
        "linkedin": {"post": LINKEDIN_TEMPLATES[idx], "cta": "رد بكلمة Demo أو احجز calendly.com/sami-assiri11/dealix-demo", "approval_required": False},
        "x": {"post": X_TEMPLATES[idx % len(X_TEMPLATES)], "approval_required": False},
        "instagram_story": {"text": IG_STORIES[idx % len(IG_STORIES)], "approval_required": False},
        "whatsapp_status": {"text": f"Dealix يرد على عملائك خلال 45 ثانية 🚀 جرّب: 499 ريال", "approval_required": False},
        "instagram_carousel": {"topic": pillar.get("name_ar", ""), "slides": 5, "status": "idea"},
        "reel_script": {"hook": pillar.get("hook", ""), "duration": "30 sec", "status": "idea"},
        "no_auto_post": True,
    }

#!/usr/bin/env python3
"""
Dealix — Daily Growth Pack Generator
Generates today's outreach targets, messages, content ideas, and follow-ups.
DRY-RUN ONLY — does NOT send any messages automatically.
"""
import json, os, sys
from datetime import datetime, timedelta

API_BASE = os.getenv("DEALIX_API", "https://api.dealix.me")

SECTORS = [
    {"id": "real_estate", "name": "عقارات", "pain": "استفسارات أسعار ومواقع ضائعة"},
    {"id": "agency", "name": "وكالة تسويق", "pain": "عملاء يخسرون leads بعد الإعلان"},
    {"id": "saas", "name": "SaaS", "pain": "leads من الموقع تبرد"},
    {"id": "clinic", "name": "عيادة/خدمات", "pain": "حجوزات ضائعة من واتساب"},
    {"id": "ecommerce", "name": "متجر إلكتروني", "pain": "استفسارات واتساب ما تُتابع"},
    {"id": "construction", "name": "مقاولات", "pain": "طلبات أسعار بدون متابعة"},
]

LINKEDIN_HOOKS = [
    "60% من استفسارات العملاء في السعودية ما تُتابع خلال أول ساعة.",
    "تكلفة SDR: 8,000 ريال/شهر. Dealix: 990 ريال. 24/7. بالعربي.",
    "Harvard: الرد خلال 5 دقائق = 21x أعلى تحويل.",
    "سألت 20 مدير مبيعات: أكبر مشكلة = ما عندهم وقت يردون.",
    "الوكالات الذكية ما تبيع إعلانات بس — تبيع نتائج.",
]

X_HOOKS = [
    "كل يوم شركات سعودية تخسر عملاء بسبب شي بسيط: بطء الرد.",
    "مو AI يستبدل البشر. AI يرد الساعة 2 بالليل.",
    "CRM يسجّل بعد المحادثة. بس مين يبدأ المحادثة؟",
    "Pilot: 499 ريال. 7 أيام. ضمان استرداد. لأننا نثق بالمنتج.",
    "بنيت Dealix بالعربي أولاً. مو ترجمة. مبني من الصفر.",
]


def generate_daily_pack():
    today = datetime.now()
    day_num = today.day % len(SECTORS)

    pack = {
        "date": today.strftime("%Y-%m-%d"),
        "day_of_week": ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"][today.weekday()],
        "targets": [],
        "messages": [],
        "content": {},
        "followups_due": [],
        "partner_target": None,
        "scorecard": {},
    }

    # 10 targets for today (rotate sectors)
    for i in range(10):
        sector = SECTORS[(day_num + i) % len(SECTORS)]
        pack["targets"].append({
            "slot": i + 1,
            "sector": sector["name"],
            "pain": sector["pain"],
            "channel": "email" if i < 5 else "whatsapp",
            "company": f"[{sector['name']}_{i+1}]",
            "status": "draft",
            "action": "Sami: fill real company name and send",
        })

    # 10 message drafts
    for i, t in enumerate(pack["targets"]):
        pack["messages"].append({
            "slot": i + 1,
            "to": t["company"],
            "channel": t["channel"],
            "type": "sector_outreach" if i < 5 else "warm_intro",
            "subject": f"فريق {t['company']} — فرصة توفير في {t['sector']}",
            "preview": f"السلام عليكم. تواصلت لأن {t['pain']}. Dealix يحل هالمشكلة...",
            "status": "DRAFT — requires Sami approval before sending",
        })

    # Content for today
    li_idx = today.day % len(LINKEDIN_HOOKS)
    x_idx = today.day % len(X_HOOKS)
    pack["content"] = {
        "linkedin_post": {
            "hook": LINKEDIN_HOOKS[li_idx],
            "action": "Sami: copy, personalize, post on LinkedIn",
        },
        "x_tweet": {
            "hook": X_HOOKS[x_idx],
            "action": "Sami: copy, personalize, post on X",
        },
        "instagram": {
            "type": ["story", "carousel", "reel"][today.day % 3],
            "topic": f"اليوم: {SECTORS[day_num]['pain']}",
            "action": "Sami: create and post",
        },
        "whatsapp_status": {
            "text": f"Dealix يرد على عملائك خلال 45 ثانية 🚀 جرّب: 499 ريال",
            "action": "Sami: update WhatsApp status",
        },
    }

    # Partner target of the day
    pack["partner_target"] = {
        "type": "وكالة تسويق",
        "hook": "خدمة lead follow-up تبيعونها لعملائكم — 20% لكم",
        "channel": "LinkedIn DM" if today.day % 2 == 0 else "Email",
        "action": "Sami: find real agency and send partner pitch",
    }

    # Scorecard template
    pack["scorecard"] = {
        "messages_sent": {"target": 10, "actual": 0},
        "replies": {"target": "-", "actual": 0},
        "demos_booked": {"target": "-", "actual": 0},
        "followups_sent": {"target": 5, "actual": 0},
        "linkedin_post": {"target": 1, "actual": 0},
        "x_post": {"target": 1, "actual": 0},
        "instagram": {"target": 1, "actual": 0},
        "partner_conversation": {"target": 1, "actual": 0},
    }

    return pack


def main():
    pack = generate_daily_pack()

    print("=" * 60)
    print(f"📋 DEALIX DAILY GROWTH PACK — {pack['date']} ({pack['day_of_week']})")
    print("=" * 60)
    print(f"\n⚠️  DRY-RUN MODE — لا يرسل رسائل تلقائياً\n")

    print("━" * 40)
    print("🎯 أهداف اليوم (10)")
    print("━" * 40)
    for t in pack["targets"]:
        print(f"  {t['slot']:2d}. [{t['channel']:8s}] {t['company']:25s} | {t['pain']}")

    print(f"\n{'━' * 40}")
    print("📝 رسائل جاهزة (10 drafts)")
    print("━" * 40)
    for m in pack["messages"]:
        print(f"  {m['slot']:2d}. {m['to']:25s} | {m['subject'][:50]}...")
        print(f"      Status: {m['status']}")

    print(f"\n{'━' * 40}")
    print("📢 محتوى اليوم")
    print("━" * 40)
    c = pack["content"]
    print(f"  LinkedIn: {c['linkedin_post']['hook'][:60]}...")
    print(f"  X/Tweet:  {c['x_tweet']['hook'][:60]}...")
    print(f"  Instagram: {c['instagram']['type']} — {c['instagram']['topic']}")
    print(f"  WhatsApp Status: {c['whatsapp_status']['text']}")

    print(f"\n{'━' * 40}")
    print("🤝 شريك اليوم")
    print("━" * 40)
    p = pack["partner_target"]
    print(f"  النوع: {p['type']}")
    print(f"  Hook: {p['hook']}")
    print(f"  القناة: {p['channel']}")

    print(f"\n{'━' * 40}")
    print("📊 Scorecard")
    print("━" * 40)
    for k, v in pack["scorecard"].items():
        print(f"  {k:25s} | هدف: {v['target']:>3} | فعلي: {v['actual']}")

    print(f"\n{'━' * 40}")
    print("⚡ Sami Actions المطلوبة:")
    print("━" * 40)
    print("  1. استبدل [placeholders] بأسماء شركات حقيقية")
    print("  2. انشر LinkedIn post")
    print("  3. انشر X tweet")
    print("  4. أرسل 10 رسائل يدوياً")
    print("  5. أرسل 5 follow-ups")
    print("  6. تواصل مع وكالة/شريك واحد")
    print("  7. حدّث WhatsApp Status")
    print("  8. سجّل الأرقام في scorecard")
    print(f"\n{'=' * 60}")
    print("📌 القاعدة: يوم فيه أقل من 10 رسائل = يوم ضائع")
    print("=" * 60)

    # Save JSON for programmatic use
    out_file = f"/tmp/dealix_daily_pack_{pack['date']}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON saved: {out_file}")


if __name__ == "__main__":
    main()

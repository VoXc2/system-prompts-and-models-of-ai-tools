#!/usr/bin/env python3
"""
seed_demo_data.py — populate a fresh Dealix Postgres with realistic Saudi
demo data so dashboards look alive on first deploy.

Inserts (idempotent — uses fixed IDs):
    - 10 sample AccountRecord rows across 5 sectors
    - 12 ContactRecord rows (mix of business + personal emails)
    - 18 SignalRecord rows (whatsapp/forms/booking/CRM)
    - 10 LeadScoreRecord rows
    - 6 GmailDraftRecord rows
    - 4 LinkedInDraftRecord rows
    - 8 EmailSendLog rows (mix of sent/replied/bounced)
    - 3 SuppressionRecord rows
    - 1 RawLeadImport with 12 RawLeadRow

Use:
    python scripts/seed_demo_data.py                    # local DB (DATABASE_URL)
    DEALIX_DEMO_PURGE=true python scripts/seed_demo_data.py   # purges then reseeds

Safety: only deletes rows whose id starts with "demo_" — never touches real data.
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Make src importable when running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

# These imports will fail without proper env — that's intentional
try:
    from db.session import async_session_factory, init_db
    from db.models import (
        AccountRecord, ContactRecord, SignalRecord, LeadScoreRecord,
        GmailDraftRecord, LinkedInDraftRecord, EmailSendLog,
        SuppressionRecord, RawLeadImport, RawLeadRow,
    )
except ImportError as e:
    print(f"ERROR: cannot import models. Run from project root with DATABASE_URL set.\n  {e}")
    sys.exit(2)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


SECTORS = [
    ("real_estate_developer", "تطوير عقاري"),
    ("hospitality", "فنادق وقاعات"),
    ("logistics", "شحن ولوجستيات"),
    ("training_center", "مراكز تدريب"),
    ("marketing_agency", "وكالة تسويق"),
]

SAMPLE_ACCOUNTS = [
    ("demo_acc_001", "شركة الراجحي للتطوير العقاري", "alrajhi-development.sa", "Riyadh", "real_estate_developer", 85),
    ("demo_acc_002", "شركة الإعمار للمشاريع", "emaar-projects.sa", "Riyadh", "real_estate_developer", 78),
    ("demo_acc_003", "فندق برج الرياض", "burjriyadh.com", "Riyadh", "hospitality", 72),
    ("demo_acc_004", "قاعة الياسمين للحفلات", "yasmin-events.sa", "Jeddah", "hospitality", 68),
    ("demo_acc_005", "شركة خليج الشحن السعودي", "gulf-shipping.sa", "Dammam", "logistics", 75),
    ("demo_acc_006", "نقل الإمداد السريع", "fastlogistics.sa", "Jeddah", "logistics", 70),
    ("demo_acc_007", "أكاديمية المعرفة للتدريب", "knowledge-academy.sa", "Riyadh", "training_center", 65),
    ("demo_acc_008", "مركز تطوير القيادات", "leadership-saudi.sa", "Riyadh", "training_center", 62),
    ("demo_acc_009", "وكالة فعل التسويق الرقمي", "fail-marketing.sa", "Riyadh", "marketing_agency", 80),
    ("demo_acc_010", "وكالة Rafal للإبداع", "rafal-creative.sa", "Jeddah", "marketing_agency", 76),
]

SAMPLE_CONTACTS = [
    ("demo_ct_001", "demo_acc_001", "عبدالله الزهراني", "Sales Director", "abdullah@alrajhi-development.sa", "+966500001001"),
    ("demo_ct_002", "demo_acc_001", "منى السبيعي", "Marketing Lead", "mona@alrajhi-development.sa", "+966500001002"),
    ("demo_ct_003", "demo_acc_002", "خالد العتيبي", "Founder", "khalid@emaar-projects.sa", "+966500001003"),
    ("demo_ct_004", "demo_acc_003", "Mr. Ahmed", "GM", "gm@burjriyadh.com", "+966500001004"),
    ("demo_ct_005", "demo_acc_004", "نوال الحربي", "Events Manager", "nawal@yasmin-events.sa", "+966500001005"),
    ("demo_ct_006", "demo_acc_005", "Ali Al-Qahtani", "Operations", "ali@gulf-shipping.sa", "+966500001006"),
    ("demo_ct_007", "demo_acc_006", "Sultan Al-Mutairi", "Sales", "sultan@fastlogistics.sa", "+966500001007"),
    ("demo_ct_008", "demo_acc_007", "Layla Al-Ghamdi", "Director", "layla@knowledge-academy.sa", "+966500001008"),
    ("demo_ct_009", "demo_acc_009", "Yousef Al-Dosari", "CEO", "yousef@fail-marketing.sa", "+966500001009"),
    ("demo_ct_010", "demo_acc_010", "Rana Khaled", "Partner", "rana@rafal-creative.sa", "+966500001010"),
    # 2 personal-email demos (will be demoted to phone-only at outreach time)
    ("demo_ct_011", "demo_acc_006", "Saad Personal", None, "saad.personal@gmail.com", "+966500001011"),
    ("demo_ct_012", "demo_acc_008", "Trainer", None, "trainer.demo@hotmail.com", "+966500001012"),
]

SAMPLE_SIGNALS = [
    ("demo_sig_001", "demo_acc_001", "whatsapp_button", "wa.me/966500001001", 0.9),
    ("demo_sig_002", "demo_acc_001", "website_form", "/contact", 0.85),
    ("demo_sig_003", "demo_acc_001", "booking_link", "/معاينة", 0.8),
    ("demo_sig_004", "demo_acc_001", "high_review_count", "127", 0.75),
    ("demo_sig_005", "demo_acc_002", "website_form", "/quote-request", 0.85),
    ("demo_sig_006", "demo_acc_002", "careers_hiring", "/careers", 0.7),
    ("demo_sig_007", "demo_acc_003", "booking_link", "/reservations", 0.9),
    ("demo_sig_008", "demo_acc_003", "high_rating", "4.6", 0.7),
    ("demo_sig_009", "demo_acc_004", "whatsapp_button", "wa.me/966500001005", 0.85),
    ("demo_sig_010", "demo_acc_005", "website_form", "/rfq", 0.85),
    ("demo_sig_011", "demo_acc_005", "crm_in_use", "hubspot", 0.9),
    ("demo_sig_012", "demo_acc_006", "ads_pixel", "meta_pixel", 0.7),
    ("demo_sig_013", "demo_acc_007", "pricing_page", "/الباقات", 0.7),
    ("demo_sig_014", "demo_acc_008", "booking_link", "/تسجيل", 0.8),
    ("demo_sig_015", "demo_acc_009", "ecom_mena", "salla", 0.8),
    ("demo_sig_016", "demo_acc_010", "chat_widget", "intercom", 0.75),
    ("demo_sig_017", "demo_acc_001", "multi_branch", "3", 0.85),
    ("demo_sig_018", "demo_acc_003", "sector_urgency", "high:hospitality", 0.85),
]


async def _purge_demo() -> int:
    """Delete only rows whose ID starts with 'demo_'."""
    count = 0
    async with async_session_factory() as session:
        for model in [
            EmailSendLog, GmailDraftRecord, LinkedInDraftRecord,
            LeadScoreRecord, SignalRecord, ContactRecord,
            SuppressionRecord, RawLeadRow, RawLeadImport, AccountRecord,
        ]:
            try:
                rows = (await session.execute(
                    select(model).where(model.id.like("demo_%"))
                )).scalars().all()
                for r in rows:
                    await session.delete(r)
                    count += 1
            except Exception as exc:  # noqa: BLE001
                print(f"  warn: skip {model.__name__}: {exc}")
        try:
            await session.commit()
        except Exception:
            await session.rollback()
    return count


async def main() -> int:
    print("📦 Dealix demo data seeder")
    print(f"   DATABASE_URL set: {bool(os.getenv('DATABASE_URL'))}")

    # Try init_db (creates tables if not exist)
    try:
        await init_db()
        print("   ✓ DB tables ensured")
    except Exception as exc:  # noqa: BLE001
        print(f"   ✗ init_db failed: {exc}")
        return 2

    if os.getenv("DEALIX_DEMO_PURGE", "").lower() in {"true", "1", "yes"}:
        print("\n🗑️  purging existing demo_* rows...")
        purged = await _purge_demo()
        print(f"   purged {purged} rows")

    now = _utcnow()

    async with async_session_factory() as session:
        # Accounts
        for aid, name, domain, city, sector, dq in SAMPLE_ACCOUNTS:
            existing = (await session.execute(
                select(AccountRecord).where(AccountRecord.id == aid)
            )).scalar_one_or_none()
            if existing:
                continue
            session.add(AccountRecord(
                id=aid, company_name=name,
                normalized_name=name.lower().replace(" ", "")[:120],
                domain=domain, website=f"https://{domain}",
                city=city, country="SA", sector=sector,
                google_place_id=f"ChIJ_demo_{aid[-3:]}",
                source_count=2, best_source="seed_demo",
                risk_level="medium", status="enriched",
                data_quality_score=float(dq),
                extra={
                    "allowed_use": "business_contact_research_only",
                    "consent_status": "legitimate_interest_business_directory",
                    "is_demo": True,
                },
            ))
        print(f"   ✓ accounts: {len(SAMPLE_ACCOUNTS)} prepared")

        # Contacts
        for cid, acc_id, name, role, email, phone in SAMPLE_CONTACTS:
            existing = (await session.execute(
                select(ContactRecord).where(ContactRecord.id == cid)
            )).scalar_one_or_none()
            if existing:
                continue
            is_personal = email and any(p in email.lower() for p in ["@gmail.com", "@hotmail.com"])
            session.add(ContactRecord(
                id=cid, account_id=acc_id,
                name=name, role=role, email=email, phone=phone,
                source="seed_demo",
                consent_status="legitimate_interest",
                opt_out=False,
                risk_level="high" if is_personal else "medium",
            ))
        print(f"   ✓ contacts: {len(SAMPLE_CONTACTS)} prepared")

        # Signals
        for sid, acc_id, stype, sval, conf in SAMPLE_SIGNALS:
            existing = (await session.execute(
                select(SignalRecord).where(SignalRecord.id == sid)
            )).scalar_one_or_none()
            if existing:
                continue
            session.add(SignalRecord(
                id=sid, account_id=acc_id,
                signal_type=stype, signal_value=sval,
                source_url=f"https://demo.example.sa/{sid}",
                confidence=conf,
                detected_at=now - timedelta(days=2),
            ))
        print(f"   ✓ signals: {len(SAMPLE_SIGNALS)} prepared")

        # Lead scores (one per account)
        for i, (aid, name, _, _, sector, _) in enumerate(SAMPLE_ACCOUNTS):
            sid = f"demo_ls_{i+1:03d}"
            existing = (await session.execute(
                select(LeadScoreRecord).where(LeadScoreRecord.id == sid)
            )).scalar_one_or_none()
            if existing:
                continue
            fit = 25 + (i * 2)  # 25-43
            intent = 18 + (i * 1.5)
            urgency = 15 + i
            risk = 10
            total = fit + intent + urgency + 8 - (risk * 0.1)
            priority = "P0" if total >= 80 else "P1" if total >= 65 else "P2"
            session.add(LeadScoreRecord(
                id=sid, account_id=aid,
                fit_score=fit, intent_score=intent, urgency_score=urgency,
                risk_score=risk, total_score=total, priority=priority,
                recommended_channel="phone_task" if i % 2 == 0 else "email_warm",
                reason=f"demo: fit={fit} intent={intent} → {priority}",
            ))
        print(f"   ✓ lead_scores: {len(SAMPLE_ACCOUNTS)} prepared")

        # Gmail drafts (last 24h, status=created)
        for i in range(6):
            did = f"demo_gd_{i+1:03d}"
            existing = (await session.execute(
                select(GmailDraftRecord).where(GmailDraftRecord.id == did)
            )).scalar_one_or_none()
            if existing:
                continue
            acc = SAMPLE_ACCOUNTS[i]
            ct = SAMPLE_CONTACTS[i]
            session.add(GmailDraftRecord(
                id=did, account_id=acc[0], queue_id=None,
                to_email=ct[4], subject=f"Dealix — تجربة لـ {acc[1][:50]}",
                body_plain=f"السلام عليكم،\n\nنرى لشركتكم فرصة في {acc[1]}. Pilot 7 أيام بـ 499 ريال — استرجاع كامل لو لم نرد على lead عربي.\n\nسامي\nDealix",
                sender_email="sami@dealix.me", status="created",
            ))
        print("   ✓ gmail_drafts: 6 prepared")

        # LinkedIn drafts
        for i in range(4):
            did = f"demo_ld_{i+1:03d}"
            existing = (await session.execute(
                select(LinkedInDraftRecord).where(LinkedInDraftRecord.id == did)
            )).scalar_one_or_none()
            if existing:
                continue
            acc = SAMPLE_ACCOUNTS[i]
            session.add(LinkedInDraftRecord(
                id=did, account_id=acc[0],
                company_name=acc[1][:200], contact_name=None,
                profile_search_query=f'"{acc[1]}" {acc[3]} site:linkedin.com',
                company_context=f"Saudi {acc[4]} in {acc[3]}",
                reason_for_outreach="signal: high inbound + WhatsApp present",
                message_ar=f"أهلاً [اسم المسؤول]، نقترح Pilot 499 ريال على {acc[1]}.",
                followup_day_3="متابعة سريعة — هل أعرض على فريقكم؟",
                followup_day_7="آخر متابعة. لو لاحقاً يناسب، أنا هنا.",
                status="draft",
            ))
        print("   ✓ linkedin_drafts: 4 prepared")

        # Email send log (mix of sent/replied/bounced) — 3 days history
        statuses = [
            ("sent", 2),
            ("sent", 1),
            ("replied", 0),  # today reply
            ("replied", 1),
            ("bounced", 1),
            ("sent", 3),
            ("sent", 2),
            ("queued", 0),
        ]
        for i, (status, days_ago) in enumerate(statuses):
            lid = f"demo_es_{i+1:03d}"
            existing = (await session.execute(
                select(EmailSendLog).where(EmailSendLog.id == lid)
            )).scalar_one_or_none()
            if existing:
                continue
            acc = SAMPLE_ACCOUNTS[i % len(SAMPLE_ACCOUNTS)]
            ct = SAMPLE_CONTACTS[i % len(SAMPLE_CONTACTS)]
            sent_at = now - timedelta(days=days_ago, hours=i)
            replied_at = (now - timedelta(hours=days_ago * 4)) if status == "replied" else None
            classification = None
            if status == "replied":
                classification = ["interested", "ask_price", "ask_demo"][i % 3]
            session.add(EmailSendLog(
                id=lid, account_id=acc[0], queue_id=None,
                to_email=ct[4], subject=f"Pilot Dealix — {acc[1][:40]}",
                body_preview="نقترح Pilot 7 أيام...",
                sender_email="sami@dealix.me",
                status=status,
                gmail_message_id=f"demo_msg_{i:04d}" if status != "queued" else None,
                bounce_reason="bounced_test_only" if status == "bounced" else None,
                reply_classification=classification,
                reply_received_at=replied_at,
                sent_at=sent_at if status != "queued" else None,
                sequence_step=0,
                compliance_check={"allowed": True, "blocked_reasons": []},
            ))
        print(f"   ✓ email_send_log: {len(statuses)} prepared")

        # Suppression list
        sup_rows = [
            ("demo_sup_001", "test-stop@example.com", None, None, "opt_out_via_reply"),
            ("demo_sup_002", None, "+966500099999", None, "manual_complaint"),
            ("demo_sup_003", None, None, "blocked-domain.com", "domain_blocked"),
        ]
        for sid, email, phone, domain, reason in sup_rows:
            existing = (await session.execute(
                select(SuppressionRecord).where(SuppressionRecord.id == sid)
            )).scalar_one_or_none()
            if existing:
                continue
            session.add(SuppressionRecord(
                id=sid, email=email, phone=phone, domain=domain, reason=reason,
            ))
        print(f"   ✓ suppression: {len(sup_rows)} prepared")

        # Commit
        try:
            await session.commit()
            print("\n✅ all demo data committed")
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            print(f"\n❌ commit failed: {exc}")
            return 3

    print("\n📊 Verify with:")
    print("   GET /api/v1/dashboard/dominance")
    print("   GET /api/v1/data/accounts?limit=10")
    print("   GET /api/v1/gmail/drafts/today")
    print("   GET /api/v1/linkedin/drafts/today")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

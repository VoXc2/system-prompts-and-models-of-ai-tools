"""Seed a demo tenant with realistic data for executive simulation demos.

Usage:
    DATABASE_URL=sqlite+aiosqlite:///./demo.db python revenue-activation/demo/seed_demo_tenant.py

Creates a complete demo environment with:
- 1 tenant (demo company)
- 3 users (admin, sales, manager)
- 15 leads across sectors
- 8 deals at various stages
- 3 pending approvals with SLA
- 5 compliance controls
- Sample connector states
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./demo.db")
os.environ.setdefault("DEALIX_INTERNAL_API_TOKEN", "")


async def seed():
    from app.sqlite_patch import apply_patch
    apply_patch()

    from app.database import engine, Base, async_session
    from app.models import (
        Tenant, User, Lead, Deal, ApprovalRequest,
        IntegrationSyncState, Contradiction, EvidencePack, ComplianceControl,
    )
    from app.models.evidence_pack import EvidencePackType, EvidencePackStatus

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Tenant
        tenant_id = uuid.uuid4()
        db.add(Tenant(id=tenant_id, name="شركة النخبة للتقنية", slug="nokhba-tech",
                       plan="strategic", domain="nokhba.sa"))

        # Users
        admin_id, sales_id, manager_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
        for uid, name, role, email in [
            (admin_id, "سامي", "admin", "sami@nokhba.sa"),
            (sales_id, "محمد", "sales", "mohammed@nokhba.sa"),
            (manager_id, "فهد", "manager", "fahad@nokhba.sa"),
        ]:
            db.add(User(id=uid, tenant_id=tenant_id, name=name, role=role,
                        email=email, hashed_password="demo", language="ar"))

        # Leads
        now = datetime.now(timezone.utc)
        sectors = [
            ("شركة البناء المتقدم", "عقارات", 85),
            ("مجموعة الصحة الأولى", "صحة", 72),
            ("تقنيات الخليج", "تقنية", 91),
            ("المستشارون العرب", "استشارات", 68),
            ("شركة السيارات الحديثة", "سيارات", 77),
            ("الأغذية السعودية", "أغذية", 45),
            ("بنك الابتكار", "مالية", 88),
            ("تعليم المستقبل", "تعليم", 55),
            ("الطاقة الخضراء", "طاقة", 63),
            ("لوجستيات الشرق", "لوجستيات", 80),
            ("فندق الريتز العربي", "ضيافة", 42),
            ("مصنع الحديد", "صناعة", 73),
            ("اتصالات الجيل", "اتصالات", 66),
            ("شركة التأمين السعودية", "تأمين", 58),
            ("مجموعة الترفيه", "ترفيه", 39),
        ]
        lead_ids = []
        for name, sector, score in sectors:
            lid = uuid.uuid4()
            lead_ids.append(lid)
            status = "qualified" if score >= 70 else "new" if score >= 50 else "cold"
            db.add(Lead(id=lid, tenant_id=tenant_id, company_name=name,
                        source="whatsapp", status=status, score=score,
                        assigned_to=sales_id))

        # Deals
        stages = [
            ("صفقة البناء المتقدم", 250000, "negotiation", 0),
            ("مشروع الصحة الرقمي", 180000, "proposal", 1),
            ("شراكة تقنيات الخليج", 500000, "closed_won", 2),
            ("استشارات المجموعة", 120000, "discovery", 3),
            ("توريد السيارات", 350000, "negotiation", 4),
            ("نظام البنك", 800000, "proposal", 6),
            ("منصة التعليم", 150000, "closed_won", 7),
            ("مشروع الطاقة", 420000, "closed_lost", 8),
        ]
        for title, value, stage, lead_idx in stages:
            db.add(Deal(id=uuid.uuid4(), tenant_id=tenant_id, title=title,
                        value=value, stage=stage, lead_id=lead_ids[lead_idx],
                        assigned_to=sales_id))

        # Approvals with SLA
        for i, (channel, resource, hours_ago) in enumerate([
            ("whatsapp", "outreach_campaign", 6),
            ("email", "proposal_send", 20),
            ("whatsapp", "partner_term_sheet", 30),
        ]):
            created = now - timedelta(hours=hours_ago)
            level = 0 if hours_ago < 8 else (1 if hours_ago < 24 else 2)
            db.add(ApprovalRequest(
                id=uuid.uuid4(), tenant_id=tenant_id, channel=channel,
                resource_type=resource, resource_id=uuid.uuid4(),
                status="pending", requested_by_id=sales_id,
                payload={
                    "category": "message" if channel == "whatsapp" else "deal",
                    "_dealix_sla": {
                        "escalation_level": level,
                        "escalation_label_ar": ["ضمن المهلة", "تحذير", "تجاوز SLA"][level],
                        "age_hours": hours_ago,
                        "warn_threshold_hours": 8,
                        "breach_threshold_hours": 24,
                    }
                }
            ))

        # Connectors
        for key, name_ar, status in [
            ("whatsapp_cloud", "واتساب Cloud API", "ok"),
            ("crm_salesforce", "Salesforce CRM", "degraded"),
            ("stripe_billing", "Stripe — الفوترة", "ok"),
            ("email_sync", "مزامنة البريد", "error"),
        ]:
            db.add(IntegrationSyncState(
                id=uuid.uuid4(), tenant_id=tenant_id,
                connector_key=key, display_name_ar=name_ar, status=status,
                last_attempt_at=now - timedelta(minutes=15),
                last_success_at=now - timedelta(minutes=15) if status == "ok" else None,
                last_error="SMTP connection refused" if status == "error" else None,
            ))

        # Evidence Pack
        import hashlib, json
        contents = [
            {"type": "deal_summary", "source": "deals", "data": {"total": 8, "won": 2, "value": 2770000}},
            {"type": "approval_audit", "source": "approval_requests", "data": {"total": 3, "pending": 3}},
            {"type": "consent_status", "source": "consents", "data": {"coverage": "85%"}},
        ]
        db.add(EvidencePack(
            id=uuid.uuid4(), tenant_id=tenant_id,
            title="Q1 2026 Board Pack", title_ar="حزمة أدلة الربع الأول 2026",
            pack_type=EvidencePackType.BOARD_REPORT,
            status=EvidencePackStatus.READY,
            contents=contents,
            hash_signature=hashlib.sha256(json.dumps(contents, sort_keys=True).encode()).hexdigest(),
        ))

        await db.commit()
        print(f"Demo tenant seeded: {tenant_id}")
        print(f"  15 leads, 8 deals, 3 approvals, 4 connectors, 1 evidence pack")
        print(f"  Admin: sami@nokhba.sa / demo")


if __name__ == "__main__":
    asyncio.run(seed())

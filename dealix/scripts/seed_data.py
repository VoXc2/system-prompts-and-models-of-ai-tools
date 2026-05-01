"""
Seed the database with sample leads for testing/development.
بذر قاعدة البيانات ببيانات تجريبية.

Usage: python scripts/seed_data.py
"""

from __future__ import annotations

import asyncio

from rich.console import Console

from auto_client_acquisition.agents.intake import IntakeAgent, LeadSource
from db.models import LeadRecord
from db.session import async_session_factory, init_db

console = Console()


SAMPLE_PAYLOADS = [
    {
        "source": LeadSource.WEBSITE,
        "payload": {
            "company": "Al Rajhi Properties",
            "name": "Faisal Al Rajhi",
            "email": "faisal@alrajhi-props.sa",
            "phone": "+966501111111",
            "sector": "real_estate",
            "region": "Saudi Arabia",
            "budget": 75000,
            "message": "We want AI for tenant management",
        },
    },
    {
        "source": LeadSource.WHATSAPP,
        "payload": {
            "company": "Dr. Sulaiman Clinics",
            "name": "د. سليمان",
            "phone": "+966502222222",
            "sector": "healthcare",
            "region": "Saudi Arabia",
            "budget": 40000,
            "message": "نحتاج نظام لجدولة المواعيد عاجل",
        },
    },
    {
        "source": LeadSource.LINKEDIN,
        "payload": {
            "company": "Nesma Logistics",
            "name": "Khalid",
            "email": "khalid@nesma-log.com",
            "sector": "logistics",
            "region": "Saudi Arabia",
            "budget": 150000,
            "message": "Manual route planning is killing us",
        },
    },
    {
        "source": LeadSource.EMAIL,
        "payload": {
            "company": "EduTech Riyadh",
            "name": "Noura",
            "email": "noura@edutech.sa",
            "sector": "education",
            "region": "Saudi Arabia",
            "budget": 30000,
            "message": "AI tutor for our K-12 platform",
        },
    },
    {
        "source": LeadSource.REFERRAL,
        "payload": {
            "company": "Saudi Retail Group",
            "name": "Ahmed",
            "email": "ahmed@srg.sa",
            "phone": "+966503333333",
            "sector": "retail",
            "region": "Saudi Arabia",
            "budget": 90000,
            "message": "Need demand forecasting",
        },
    },
]


async def main() -> None:
    console.print("[cyan]Initializing database...[/cyan]")
    await init_db()

    intake = IntakeAgent()
    session_factory = async_session_factory()

    async with session_factory() as session:
        for i, item in enumerate(SAMPLE_PAYLOADS, 1):
            lead = await intake.run(payload=item["payload"], source=item["source"])
            record = LeadRecord(
                id=lead.id,
                source=lead.source.value,
                company_name=lead.company_name,
                contact_name=lead.contact_name,
                contact_email=lead.contact_email,
                contact_phone=lead.contact_phone,
                sector=lead.sector,
                region=lead.region,
                company_size=lead.company_size,
                budget=lead.budget,
                status=lead.status.value,
                fit_score=lead.fit_score,
                urgency_score=lead.urgency_score,
                locale=lead.locale,
                message=lead.message,
                pain_points=lead.pain_points,
                meta_json=lead.metadata,
                dedup_hash=lead.dedup_hash,
            )
            session.add(record)
            console.print(f"  [green]✓[/green] {i}/{len(SAMPLE_PAYLOADS)}  {lead.company_name}")
        await session.commit()

    console.print(f"\n[green]Done![/green] {len(SAMPLE_PAYLOADS)} leads seeded.")


if __name__ == "__main__":
    asyncio.run(main())

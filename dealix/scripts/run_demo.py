"""
Run an end-to-end demo of the acquisition pipeline.
Usage: python scripts/run_demo.py
"""

from __future__ import annotations

import asyncio
import json

from rich.console import Console

from auto_client_acquisition.agents.intake import LeadSource
from auto_client_acquisition.pipeline import AcquisitionPipeline

console = Console()


SAMPLE_LEADS = [
    {
        "source": LeadSource.WEBSITE,
        "payload": {
            "company": "شركة التقنية المتقدمة",
            "name": "أحمد محمد",
            "email": "ahmed@techadvanced.sa",
            "phone": "+966501234567",
            "sector": "technology",
            "company_size": "medium",
            "region": "Saudi Arabia",
            "budget": 50000,
            "message": "نحتاج نظام AI لأتمتة إدارة المبيعات، المشكلة عندنا بطء في الرد على العملاء عاجل",
        },
    },
    {
        "source": LeadSource.WEBSITE,
        "payload": {
            "company": "Saudi Logistics Co",
            "name": "John Smith",
            "email": "john@saudilogistics.com",
            "sector": "logistics",
            "company_size": "large",
            "region": "Saudi Arabia",
            "budget": 120000,
            "message": "We need help with route optimization - manual process is slow and expensive",
        },
    },
    {
        "source": LeadSource.WHATSAPP,
        "payload": {
            "company": "",
            "name": "عبدالله",
            "phone": "+966555123456",
            "message": "السلام عليكم، نبي حل ذكي لجدولة المواعيد في عيادتنا، عندنا فوضى",
        },
    },
]


async def main() -> None:
    pipeline = AcquisitionPipeline()
    for i, lead in enumerate(SAMPLE_LEADS, 1):
        console.rule(f"[bold cyan]Lead {i}/{len(SAMPLE_LEADS)}[/bold cyan]")
        console.print(f"Source: {lead['source'].value}")
        console.print(f"Payload: {json.dumps(lead['payload'], ensure_ascii=False, indent=2)}")

        with console.status("[cyan]Running pipeline...[/cyan]"):
            result = await pipeline.run(
                payload=lead["payload"],
                source=lead["source"],
                use_llm_pain=False,  # keyword-only for fast demo
                auto_book=False,
            )

        console.print(f"\n[green]✓[/green] Lead ID: {result.lead.id}")
        console.print(f"   Company: {result.lead.company_name}")
        console.print(f"   Locale: {result.lead.locale}")
        console.print(f"   Status: {result.lead.status.value}")
        if result.fit_score:
            console.print(
                f"   Fit tier: [bold]{result.fit_score.tier}[/bold] "
                f"(score {result.fit_score.overall_score:.2f})"
            )
        if result.extraction:
            console.print(
                f"   Pain points: {len(result.extraction.pain_points)} found, "
                f"urgency {result.extraction.urgency_score:.1f}"
            )
        if result.warnings:
            console.print(f"   [yellow]Warnings: {len(result.warnings)}[/yellow]")

    console.rule("[bold green]Demo complete[/bold green]")


if __name__ == "__main__":
    asyncio.run(main())

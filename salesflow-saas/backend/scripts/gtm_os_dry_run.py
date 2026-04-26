#!/usr/bin/env python3
"""
Dealix GTM OS — Dry Run CLI
Analyzes a company and generates a complete GTM pack.
DRY-RUN ONLY — does NOT send any messages.
"""
import asyncio
import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dealix_gtm_os.agents.supervisor_agent import SupervisorAgent


async def run(company_name: str, website: str, sector: str, city: str, email: str):
    supervisor = SupervisorAgent()
    result = await supervisor.run({
        "name": company_name,
        "website": website,
        "sector": sector,
        "city": city,
        "email": email,
    })

    print("=" * 60)
    print(f"  DEALIX GTM OS — DRY RUN")
    print(f"  Company: {company_name}")
    print(f"  ⚠️  DRY-RUN ONLY — لا يرسل رسائل")
    print("=" * 60)

    intel = result["intelligence"]
    print(f"\n{'━' * 40}")
    print("1. COMPANY INTELLIGENCE")
    print(f"{'━' * 40}")
    print(f"  Sector: {intel.get('sector', '?')}")
    print(f"  Summary: {intel.get('business_summary', '?')}")
    print(f"  Services: {', '.join(intel.get('products_services', []))}")
    print(f"  Customers: {', '.join(intel.get('target_customers', []))}")
    print(f"  Pain Points: {', '.join(intel.get('pain_points', []))}")
    print(f"  Partnership: {intel.get('partnership_potential', '?')}")
    print(f"  Opportunity: {', '.join(intel.get('opportunity_types', []))}")
    print(f"  Confidence: {intel.get('confidence', 0):.0%}")

    score = result["score"]
    print(f"\n{'━' * 40}")
    print("2. TARGET SCORE")
    print(f"{'━' * 40}")
    print(f"  Fit: {score['fit']}/5 | Urgency: {score['urgency']}/5 | Access: {score['access']}/5")
    print(f"  Partner: {score['partner']}/5 | Payment: {score['payment']}/5 | Case Study: {score['case_study']}/5")
    print(f"  Risk: {score['risk']}/5")
    print(f"  TOTAL: {score['total']} → Priority: {score['priority']}")

    channel = result["channel_plan"]
    print(f"\n{'━' * 40}")
    print("3. CHANNEL STRATEGY")
    print(f"{'━' * 40}")
    print(f"  Primary: {channel['primary_channel']}")
    print(f"  Secondary: {channel['secondary_channel']}")
    print(f"  Automation: {channel['automation_level']}")
    print(f"  Reason: {channel['reason']}")
    if channel.get("risk_flags"):
        print(f"  Risk Flags: {', '.join(channel['risk_flags'])}")

    comp = result["compliance"]
    print(f"\n{'━' * 40}")
    print("4. COMPLIANCE")
    print(f"{'━' * 40}")
    print(f"  Allowed: {'✅' if comp['allowed'] else '❌'}")
    print(f"  Level: {comp['level']}")
    print(f"  Reason: {comp['reason']}")

    msg = result["message"]
    print(f"\n{'━' * 40}")
    print("5. MESSAGE (DRAFT — NOT SENT)")
    print(f"{'━' * 40}")
    print(f"  Channel: {msg['channel']}")
    print(f"  Subject: {msg.get('subject', 'N/A')}")
    print(f"  Approval Required: {'✅ YES' if msg['approval_required'] else 'No'}")
    print(f"\n  --- BODY ---")
    for line in msg["body"].split("\n"):
        print(f"  {line}")
    print(f"  --- END ---")
    print(f"\n  Follow-up 24h: {msg['follow_up_24h'][:80]}...")
    print(f"  Follow-up 72h: {msg['follow_up_72h'][:80]}...")
    print(f"  Stop: {msg['stop_condition']}")

    print(f"\n{'━' * 40}")
    print("6. NEXT ACTION")
    print(f"{'━' * 40}")
    print(f"  Action: {result['next_action']}")
    print(f"  Approval Required: {'✅ YES — Sami must approve before sending' if result['approval_required'] else 'No'}")

    prohibited = []
    if "linkedin" in channel["primary_channel"]:
        prohibited.append("LinkedIn scraping")
        prohibited.append("LinkedIn auto-DM")
    prohibited.extend(["WhatsApp cold blast", "Instagram mass DM", "Fake accounts"])
    print(f"\n{'━' * 40}")
    print("7. PROHIBITED ACTIONS")
    print(f"{'━' * 40}")
    for p in prohibited:
        print(f"  ❌ {p}")

    print(f"\n{'=' * 60}")
    print("  ⚠️  DRY-RUN COMPLETE — NO MESSAGES SENT")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Dealix GTM OS Dry Run")
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--website", default="")
    parser.add_argument("--sector", default="agency")
    parser.add_argument("--city", default="الرياض")
    parser.add_argument("--email", default="")
    args = parser.parse_args()
    asyncio.run(run(args.company_name, args.website, args.sector, args.city, args.email))


if __name__ == "__main__":
    main()

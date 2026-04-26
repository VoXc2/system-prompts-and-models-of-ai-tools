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
    print(f"  Trace ID: {result.get('trace_id', 'N/A')}")
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

    partnership = result.get("partnership", {})
    print(f"\n{'━' * 40}")
    print("3. PARTNERSHIP CLASSIFICATION")
    print(f"{'━' * 40}")
    print(f"  Primary: {partnership.get('primary_type', 'N/A')}")
    print(f"  All types: {', '.join(partnership.get('opportunity_types', []))}")
    print(f"  Model: {partnership.get('recommended_model', 'N/A')}")

    channel = result["channel_plan"]
    print(f"\n{'━' * 40}")
    print("4. CHANNEL STRATEGY")
    print(f"{'━' * 40}")
    print(f"  Primary: {channel['primary_channel']}")
    print(f"  Secondary: {channel['secondary_channel']}")
    print(f"  Automation: {channel['automation_level']}")

    comp = result["compliance"]
    print(f"\n{'━' * 40}")
    print("5. COMPLIANCE GATE")
    print(f"{'━' * 40}")
    print(f"  Allowed: {'✅' if comp['allowed'] else '❌'}")
    print(f"  Level: {comp['level']}")
    print(f"  Reason: {comp['reason']}")

    msg = result["message"]
    print(f"\n{'━' * 40}")
    print("6. MESSAGE (DRAFT)")
    print(f"{'━' * 40}")
    print(f"  Subject: {msg.get('subject', 'N/A')}")
    print(f"  Approval: {'✅ REQUIRED' if msg.get('approval_required') else 'No'}")
    body_preview = msg.get("body", "")[:150]
    print(f"  Preview: {body_preview}...")

    proof = result.get("proof_pack", {})
    print(f"\n{'━' * 40}")
    print("7. PROOF PACK")
    print(f"{'━' * 40}")
    print(f"  Confidence: {proof.get('intelligence_confidence', 0):.0%}")
    print(f"  Scoring: {proof.get('scoring_method', '?')}")
    print(f"  Channel reason: {proof.get('channel_reason', '?')}")
    print(f"  Message validated: {proof.get('message_validated', '?')}")
    print(f"  No real send: {proof.get('no_real_send', True)}")
    print(f"  Sources: {', '.join(proof.get('sources', []))}")

    val = result.get("output_validation", {})
    print(f"\n{'━' * 40}")
    print("8. AI COST & QUALITY")
    print(f"{'━' * 40}")
    print(f"  Model: {result.get('model_selected', '?')}")
    tokens = result.get("estimated_tokens", {})
    print(f"  Tokens: {tokens.get('input', 0)} in / {tokens.get('output', 0)} out")
    print(f"  Cost: {result.get('estimated_cost_sar', 0)} SAR")
    print(f"  Cache: {result.get('cache_status', '?')}")
    print(f"  Output valid: {val.get('valid', '?')} ({val.get('issue_count', 0)} issues)")

    trace = result.get("trace", {})
    print(f"\n{'━' * 40}")
    print("9. TRACE")
    print(f"{'━' * 40}")
    print(f"  Trace ID: {trace.get('trace_id', result.get('trace_id', '?'))}")
    print(f"  Time: {trace.get('total_time_s', '?')}s")
    print(f"  Steps: {trace.get('steps', '?')}")
    print(f"  Cost: {trace.get('total_cost_sar', '?')} SAR")

    print(f"\n{'━' * 40}")
    print("10. NEXT ACTION")
    print(f"{'━' * 40}")
    print(f"  Action: {result.get('next_action', '?')}")
    print(f"  Approval Required: {'✅ YES — Sami must approve' if result.get('approval_required') else 'No'}")

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

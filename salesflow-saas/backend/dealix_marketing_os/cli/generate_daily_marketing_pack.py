#!/usr/bin/env python3
"""Generate daily marketing pack — dry-run only."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dealix_marketing_os.pipelines.daily_marketing_pack_pipeline import generate_daily_marketing_pack

def main():
    day = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    pack = generate_daily_marketing_pack(day_number=day)
    print(f"=== DEALIX DAILY MARKETING PACK — Day {day} ===")
    print(f"Strategy: {pack['strategy']['strategy_summary']}")
    print(f"Theme: {pack['content']['theme']}")
    print(f"LinkedIn: {pack['content']['linkedin']['post'][:60]}...")
    print(f"X: {pack['content']['x']['post'][:60]}...")
    print(f"IG Story: {pack['content']['instagram_story']['text'][:60]}...")
    print(f"WA Status: {pack['content']['whatsapp_status']['text'][:60]}...")
    print(f"Partner: {pack['partner_assets']['agency_pitch'][:60]}...")
    print(f"Auto-post: {pack['no_auto_post']} (manual only)")
    print(f"Auto-send: {pack['no_auto_send']} (manual only)")

if __name__ == "__main__":
    main()

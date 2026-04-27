"""Strategy Engine — generates daily marketing strategy based on current state."""

SECTOR_PRIORITY = {
    "agency": {"priority": 1, "offer": "Agency Add-on Pilot", "channel": "email+linkedin"},
    "real_estate": {"priority": 2, "offer": "Speed-to-Lead Audit", "channel": "email+whatsapp"},
    "clinic": {"priority": 3, "offer": "Booking Follow-up Pilot", "channel": "whatsapp+email"},
    "ecommerce": {"priority": 4, "offer": "Inquiry-to-Order Pilot", "channel": "email+instagram"},
    "website_agency": {"priority": 5, "offer": "Website-to-Lead Add-on", "channel": "linkedin+email"},
}

def generate_daily_strategy(verdict: str = "market_execution_ready", day_number: int = 1) -> dict:
    themes = ["lost_leads", "whatsapp_followup", "speed_to_lead", "agency_addon", "partner_earning",
              "arabic_first", "build_in_public", "revenue_ops", "customer_delivery", "proof_and_safety"]
    theme = themes[(day_number - 1) % len(themes)]
    sector_keys = sorted(SECTOR_PRIORITY.keys(), key=lambda k: SECTOR_PRIORITY[k]["priority"])
    primary_sector = sector_keys[(day_number - 1) % len(sector_keys)]
    sector = SECTOR_PRIORITY[primary_sector]

    return {
        "date_index": day_number,
        "verdict": verdict,
        "strategy_summary": f"يوم {day_number}: ركّز على {primary_sector} مع عرض {sector['offer']}",
        "target_segment": primary_sector,
        "primary_offer": sector["offer"],
        "secondary_offer": "Pilot 499 SAR",
        "priority_channels": sector["channel"].split("+"),
        "content_theme": theme,
        "campaign_goal": "أول 3 ردود إيجابية" if day_number <= 7 else "أول demo",
        "daily_minimum": {"touches": 10, "followups": 5, "content": 3, "partner": 1},
        "risks": ["لا إرسال بدون مراجعة", "لا ادعاءات مبالغ فيها"],
        "next_actions": [
            f"أرسل 5 إيميلات لقطاع {primary_sector}",
            "انشر LinkedIn + X + Instagram",
            "تواصل مع وكالة واحدة",
            "سجّل في scorecard",
        ],
    }

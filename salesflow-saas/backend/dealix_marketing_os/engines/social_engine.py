"""Social Engine — manages multi-platform social media strategy."""

PLATFORM_RULES = {
    "linkedin": {"frequency": "daily", "type": "founder-led B2B", "automation": "manual only", "dm": "manual max 5/day", "scraping": "PROHIBITED"},
    "x": {"frequency": "daily", "type": "build in public", "automation": "posts allowed, replies manual", "dm": "manual only"},
    "instagram": {"frequency": "3x/week", "type": "visual trust", "automation": "stories manual, no mass DM", "dm": "inbound only"},
    "tiktok": {"frequency": "2x/week", "type": "education/awareness", "automation": "content only, no DM scraping"},
    "whatsapp_status": {"frequency": "daily", "type": "warm network", "automation": "manual"},
}

def generate_social_plan(day_number: int = 1) -> dict:
    return {
        "day": day_number,
        "platforms": PLATFORM_RULES,
        "daily_tasks": {
            "linkedin": "1 post + 5 comments + 3 manual DMs max",
            "x": "1 tweet + 5 replies",
            "instagram": "1 story (or carousel/reel if scheduled)",
            "whatsapp": "update status + 3-5 warm messages",
        },
        "prohibited": ["linkedin_scraping", "linkedin_auto_dm", "instagram_mass_dm", "whatsapp_cold_blast", "x_auto_mention"],
        "no_auto_post": True,
    }

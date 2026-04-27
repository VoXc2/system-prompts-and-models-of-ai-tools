"""Daily Marketing Pack — generates complete marketing execution pack."""
from dealix_marketing_os.engines.strategy_engine import generate_daily_strategy
from dealix_marketing_os.engines.content_engine import generate_daily_content
from dealix_marketing_os.engines.social_engine import generate_social_plan
from dealix_marketing_os.engines.partner_marketing_engine import generate_partner_assets

def generate_daily_marketing_pack(day_number: int = 1) -> dict:
    strategy = generate_daily_strategy(day_number=day_number)
    content = generate_daily_content(day_number=day_number, theme=strategy["content_theme"])
    social = generate_social_plan(day_number=day_number)
    partner = generate_partner_assets()

    return {
        "day": day_number,
        "strategy": strategy,
        "content": content,
        "social": social,
        "partner_assets": partner,
        "approval_tasks": [
            "LinkedIn post: review before posting",
            "Partner pitch: review terms before sending",
            "WhatsApp: only send to warm contacts",
        ],
        "no_auto_post": True,
        "no_auto_send": True,
    }

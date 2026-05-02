"""Revenue Company OS — events to cards, RWU, merged command feed."""

from auto_client_acquisition.revenue_company_os.card_factory import (
    build_role_command_feed,
    build_whatsapp_daily_brief_lines,
)
from auto_client_acquisition.revenue_company_os.cards import (
    MAX_CARD_BUTTONS,
    UserRole,
    normalize_card,
    normalize_role_param,
)
from auto_client_acquisition.revenue_company_os.command_feed_engine import build_company_os_command_feed
from auto_client_acquisition.revenue_company_os.event_to_card import event_to_card

__all__ = [
    "MAX_CARD_BUTTONS",
    "UserRole",
    "build_company_os_command_feed",
    "build_role_command_feed",
    "build_whatsapp_daily_brief_lines",
    "event_to_card",
    "normalize_card",
    "normalize_role_param",
]

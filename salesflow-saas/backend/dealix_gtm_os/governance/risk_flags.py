"""Risk flags — identifies risky actions before they happen."""
HIGH_RISK = {"whatsapp_cold", "linkedin_scraping", "linkedin_auto_dm", "instagram_mass_dm", "fake_claim", "guaranteed_revenue", "send_without_approval"}

def check_risk(action: str) -> dict:
    is_high = action in HIGH_RISK
    return {"action": action, "risk": "HIGH" if is_high else "LOW", "blocked": is_high, "reason": f"{action} is {'HIGH RISK — blocked' if is_high else 'acceptable'}"}

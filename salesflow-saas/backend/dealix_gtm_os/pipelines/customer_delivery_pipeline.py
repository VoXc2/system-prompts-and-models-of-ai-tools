"""Customer Delivery Pipeline — creates workspace and manages onboarding."""
from dealix_gtm_os.models.customer_workspace import CustomerWorkspace

def create_workspace(company_name: str, sector: str, plan: str = "pilot", whatsapp: str = "", email: str = "", questions: list[str] = None) -> dict:
    ws = CustomerWorkspace(
        company_name=company_name,
        sector=sector,
        plan=plan,
        lead_sources=[s for s in [whatsapp, email] if s],
        qualification_questions=questions or [],
        channels=["whatsapp" if whatsapp else "email"],
    )
    return ws.model_dump()

def get_onboarding_status(workspace: dict) -> dict:
    checklist = workspace.get("onboarding_checklist", [])
    done = sum(1 for t in checklist if t.get("done"))
    return {"total": len(checklist), "done": done, "remaining": len(checklist) - done, "complete": done == len(checklist)}

def generate_weekly_report(workspace: dict) -> dict:
    return {
        "company": workspace.get("company_name"),
        "plan": workspace.get("plan"),
        "channels_active": workspace.get("channels", []),
        "recommendations": [
            "راجع سرعة الرد — هل تحت 45 ثانية؟",
            "شيك الردود وصنّفها",
            "تابع الاستفسارات اللي ما انحلت",
        ],
    }

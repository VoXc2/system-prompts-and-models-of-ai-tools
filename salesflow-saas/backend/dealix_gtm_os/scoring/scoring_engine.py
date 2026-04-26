"""Unified scoring engine for targets, channels, and partners."""
from dealix_gtm_os.models.score import TargetScore

SECTOR_DEFAULTS = {
    "agency": {"fit": 5, "urgency": 4, "partner": 5, "payment": 3, "case_study": 4, "risk": 2},
    "real_estate": {"fit": 5, "urgency": 5, "partner": 2, "payment": 4, "case_study": 3, "risk": 2},
    "saas": {"fit": 4, "urgency": 4, "partner": 3, "payment": 3, "case_study": 3, "risk": 2},
    "clinic": {"fit": 4, "urgency": 4, "partner": 1, "payment": 4, "case_study": 3, "risk": 1},
    "ecommerce": {"fit": 4, "urgency": 3, "partner": 2, "payment": 3, "case_study": 2, "risk": 2},
    "construction": {"fit": 3, "urgency": 3, "partner": 1, "payment": 3, "case_study": 2, "risk": 2},
    "training": {"fit": 3, "urgency": 3, "partner": 1, "payment": 3, "case_study": 2, "risk": 1},
    "consulting": {"fit": 3, "urgency": 2, "partner": 3, "payment": 3, "case_study": 2, "risk": 1},
    "website_agency": {"fit": 4, "urgency": 3, "partner": 4, "payment": 3, "case_study": 3, "risk": 1},
}

def score_target(company_name: str, sector: str, has_contact: bool = False) -> TargetScore:
    sector_key = sector.lower().replace(" ", "_").replace("marketing_", "")
    defaults = SECTOR_DEFAULTS.get(sector_key, {"fit": 3, "urgency": 3, "partner": 2, "payment": 3, "case_study": 2, "risk": 2})
    return TargetScore(
        company_name=company_name,
        fit=defaults["fit"],
        urgency=defaults["urgency"],
        access=4 if has_contact else 2,
        partner=defaults["partner"],
        payment=defaults["payment"],
        case_study=defaults["case_study"],
        risk=defaults["risk"],
    )

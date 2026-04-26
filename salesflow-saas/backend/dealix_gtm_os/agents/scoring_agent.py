from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.models.score import TargetScore

SECTOR_SCORES = {
    "agency": {"fit": 5, "urgency": 4, "partner": 5, "payment": 3, "case_study": 4},
    "real_estate": {"fit": 5, "urgency": 5, "partner": 2, "payment": 4, "case_study": 3},
    "saas": {"fit": 4, "urgency": 4, "partner": 3, "payment": 3, "case_study": 3},
    "clinic": {"fit": 4, "urgency": 4, "partner": 1, "payment": 4, "case_study": 3},
    "ecommerce": {"fit": 4, "urgency": 3, "partner": 2, "payment": 3, "case_study": 2},
    "construction": {"fit": 3, "urgency": 3, "partner": 1, "payment": 3, "case_study": 2},
}

class ScoringAgent(BaseAgent):
    name = "scoring"
    description = "Scores a target company"

    async def run(self, input_data: dict) -> dict:
        sector = input_data.get("sector", "").lower().replace(" ", "_")
        defaults = SECTOR_SCORES.get(sector, {"fit": 3, "urgency": 3, "partner": 2, "payment": 3, "case_study": 2})
        has_email = bool(input_data.get("email") or input_data.get("website"))
        score = TargetScore(
            company_name=input_data.get("name", "Unknown"),
            fit=defaults["fit"],
            urgency=defaults["urgency"],
            access=4 if has_email else 2,
            partner=defaults["partner"],
            payment=defaults["payment"],
            case_study=defaults["case_study"],
            risk=2,
        )
        return score.model_dump()

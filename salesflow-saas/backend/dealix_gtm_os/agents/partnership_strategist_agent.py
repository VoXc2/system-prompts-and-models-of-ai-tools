from dealix_gtm_os.agents.base_agent import BaseAgent
from dealix_gtm_os.models.opportunity import OpportunityType

PARTNERSHIP_MAP = {
    "agency": [OpportunityType.AGENCY_PARTNER, OpportunityType.CO_SELLING_PARTNER, OpportunityType.REFERRAL_PARTNER],
    "website_agency": [OpportunityType.IMPLEMENTATION_PARTNER, OpportunityType.AGENCY_PARTNER],
    "consulting": [OpportunityType.REFERRAL_PARTNER, OpportunityType.IMPLEMENTATION_PARTNER],
    "saas": [OpportunityType.INTEGRATION_PARTNER, OpportunityType.DIRECT_CUSTOMER],
}

class PartnershipStrategistAgent(BaseAgent):
    name = "partnership_strategist"
    description = "Classifies partnership opportunities"

    async def run(self, input_data: dict) -> dict:
        sector = input_data.get("sector", "").lower().replace(" ", "_")
        types = PARTNERSHIP_MAP.get(sector, [OpportunityType.DIRECT_CUSTOMER])
        primary = types[0] if types else OpportunityType.DIRECT_CUSTOMER
        return {
            "opportunity_types": [t.value for t in types],
            "primary_type": primary.value,
            "partner_potential": "high" if len(types) > 1 else "low",
            "recommended_model": "agency_addon" if primary == OpportunityType.AGENCY_PARTNER else "pilot",
            "negotiation_angle": "خدمة جديدة تبيعونها" if primary == OpportunityType.AGENCY_PARTNER else "حل لمشكلة الـleads",
        }

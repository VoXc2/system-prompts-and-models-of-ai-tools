from enum import Enum
from pydantic import BaseModel, Field

class OpportunityType(str, Enum):
    DIRECT_CUSTOMER = "direct_customer"
    AGENCY_PARTNER = "agency_partner"
    REFERRAL_PARTNER = "referral_partner"
    CO_SELLING_PARTNER = "co_selling_partner"
    IMPLEMENTATION_PARTNER = "implementation_partner"
    SERVICE_EXCHANGE = "service_exchange"
    INTEGRATION_PARTNER = "integration_partner"
    CONTENT_PARTNER = "content_partner"
    RESELLER_LATER = "reseller_later"
    WHITELABEL_LATER = "whitelabel_later"

class Opportunity(BaseModel):
    company_name: str
    opportunity_type: OpportunityType
    fit_score: int = Field(ge=1, le=5)
    urgency_score: int = Field(ge=1, le=5)
    access_score: int = Field(ge=1, le=5)
    partner_score: int = Field(ge=1, le=5)
    payment_score: int = Field(ge=1, le=5)
    risk_score: int = Field(ge=1, le=5)
    total_score: int = 0
    reason: str = ""
    recommended_offer: str = ""
    recommended_channel: str = ""

    def model_post_init(self, __context):
        self.total_score = (self.fit_score + self.urgency_score + self.access_score +
                           self.partner_score + self.payment_score - self.risk_score)

from pydantic import BaseModel, Field, computed_field

class TargetScore(BaseModel):
    company_name: str
    fit: int = Field(ge=1, le=5)
    urgency: int = Field(ge=1, le=5)
    access: int = Field(ge=1, le=5)
    partner: int = Field(ge=1, le=5)
    payment: int = Field(ge=1, le=5)
    case_study: int = Field(ge=1, le=5)
    risk: int = Field(ge=1, le=5)

    @computed_field
    @property
    def total(self) -> int:
        return self.fit + self.urgency + self.access + self.partner + self.payment + self.case_study - self.risk

    @computed_field
    @property
    def priority(self) -> str:
        if self.total >= 24:
            return "send_today"
        elif self.total >= 18:
            return "send_this_week"
        elif self.total >= 12:
            return "send_this_month"
        return "backlog"

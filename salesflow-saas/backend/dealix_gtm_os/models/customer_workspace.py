from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CustomerWorkspace(BaseModel):
    company_name: str
    sector: str
    plan: str = "pilot"
    status: str = "onboarding"
    lead_sources: list[str] = Field(default_factory=list)
    qualification_questions: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    onboarding_checklist: list[dict] = Field(default_factory=lambda: [
        {"task": "استلام الدفع", "done": False},
        {"task": "استلام رقم واتساب/إيميل", "done": False},
        {"task": "استلام 3 أسئلة تأهيل", "done": False},
        {"task": "تفعيل النظام", "done": False},
        {"task": "إرسال تأكيد للعميل", "done": False},
    ])
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

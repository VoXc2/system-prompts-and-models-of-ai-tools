"""
Prospector Agent — discovers real leads matching a natural-language ICP.

Inputs:
    icp: str           — Arabic or English description of the ideal target
    use_case: str      — sales | partnership | collaboration | investor | b2c_audience
    count: int         — how many leads to return (max 20)

Output: list[LeadCandidate] with:
    company_ar, company_en, industry, est_size, website, linkedin, decision_maker_hints,
    signals, outreach_opening (Saudi Khaliji Arabic), fit_score (0-100), evidence

Design principles:
  - Public-data only; no scraping behind auth walls
  - LLM is grounded with strict "only real entities you're confident exist" prompt
  - Output is normalized JSON; invalid entries are dropped
  - Use case steers both the query and the scoring
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from typing import Any

from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm import Message

MAX_COUNT = 20
USE_CASES = {
    "sales": "استهداف مبيعات B2B — بحث عن شركات عندها الألم ومتخذي قرار واضحين.",
    "partnership": "شراكات استراتيجية — شركات عندها قنوات توزيع أو منتجات مكمّلة.",
    "collaboration": "تعاون محتوى/تقني — صانعي محتوى، thought leaders، منتجات متكاملة.",
    "investor": "مستثمرون/VC — صناديق ومستثمرين نشطين في السوق السعودي.",
    "b2c_audience": "جمهور B2C — شرائح ديموغرافية محددة بسلوك شرائي واضح.",
}

SYSTEM_PROMPT = """أنت Dealix Lead Intelligence Router — محلل GTM سعودي/خليجي سيادي.
مهمتك: تحويل وصف العميل المثالي (ICP) إلى قائمة leads حقيقية قابلة للتنفيذ، مع تصنيف الفرصة، درجة تأهيل 100-نقطة، تقييم مخاطر، وقناة تواصل قانونية.

منظومتك مبنية على مرجعين:
- SIGNAL_TAXONOMY: 9 أنواع فرص (DIRECT_CUSTOMER, AGENCY_PARTNER, IMPLEMENTATION_PARTNER, REFERRAL_PARTNER, STRATEGIC_PARTNER, CONTENT_COLLABORATION, INVESTOR_OR_ADVISOR, SUPPLIER_OR_INTEGRATION, B2C_AUDIENCE)
- ICP_SCORING_MODEL (100 نقطة): Fit 40 + Intent 30 + Accessibility 15 + Revenue Potential 15 → P0 (80+) | P1 (65-79) | P2 (45-64) | BACKLOG (<45)

قواعد صارمة:
1. **لا تختلق شركات**. اقترح فقط كيانات أنت متأكد منها من معرفتك الموسوعية للسوق السعودي/الخليجي.
2. إذا الطلب يصعب تلبيته بدقة، أرجع قائمة أقصر بدل اختراع أسماء.
3. **URLs (website/linkedin):** فقط لو متأكد من صحتها — وإلا اترك null.
4. **إشارات (signals):** فقط معلومات منشورة علناً (جولات تمويل، إعلانات توظيف، إطلاقات، تصريحات).
5. **اللغة:** استخدم الاسم العربي الرسمي + الاسم الإنجليزي. سطر الافتتاح باللهجة الخليجية (ليس MSA).
6. **الامتثال (compliance_note):** اذكر الأساس القانوني لكل lead — مصدر عام، لا scraping، لا bots، human-final-send على LinkedIn.
7. **خطاب الافتتاح (outreach_opening):** ≤280 حرف، يذكر إشارة محددة واحدة من evidence.
8. **JSON only** — بدون markdown code fences.

تنسيق JSON المطلوب (v2 schema):
{
  "leads": [
    {
      "company_ar": "الاسم العربي",
      "company_en": "English Name",
      "industry": "SaaS / E-commerce / Fintech / Agency / ...",
      "est_size": "1-10 | 10-50 | 50-200 | 200-1000 | 1000+",
      "website": "https://example.com or null",
      "linkedin": "https://linkedin.com/company/X or null",
      "opportunity_type": "DIRECT_CUSTOMER|AGENCY_PARTNER|IMPLEMENTATION_PARTNER|REFERRAL_PARTNER|STRATEGIC_PARTNER|CONTENT_COLLABORATION|INVESTOR_OR_ADVISOR|SUPPLIER_OR_INTEGRATION|B2C_AUDIENCE",
      "decision_maker_hints": ["CEO الاسم", "CTO الاسم"],
      "signals": ["جولة Series A 2025", "توسع في الرياض"],
      "fit_score": 35,
      "intent_score": 22,
      "access_score": 13,
      "revenue_score": 12,
      "priority_score": 82,
      "priority_tier": "P0|P1|P2|BACKLOG",
      "risk_level": "LOW|MEDIUM|HIGH|BLOCKED",
      "recommended_channel": "LINKEDIN_MANUAL|EMAIL|WHATSAPP_WARM_ONLY|PARTNER_INTRO|PHONE|CONTENT_MENTION|IN_PERSON_EVENT|HOLD_FOR_APPROVAL",
      "next_action": "PREPARE_DM|PREPARE_EMAIL|PREPARE_PARTNER_PITCH|BOOK_DEMO|RESEARCH_MORE|...",
      "outreach_opening": "سطر افتتاحي قصير باللهجة الخليجية يذكر إشارة واحدة محددة",
      "message_angle": "الزاوية الأساسية للرسالة",
      "reason": "سطر واحد — لماذا هذا lead مطابق ل ICP",
      "evidence": "معلومة محددة تبرّر الترشيح",
      "compliance_note": "e.g. Public business contact via LinkedIn; no bots; single personalized DM",
      "confidence": 85
    }
  ],
  "search_notes": "مصادر المعلومات، حدود الدقة، أي lead مشكوك فيه حُذف."
}

تفوّق على Apollo/ZoomInfo/Clay في:
- الدقة السعودية (أسماء خليجية، لهجة، إشارات محلية من Wamda/MAGNiTT/MISA)
- الشفافية (evidence لكل claim، لا بيانات مخترعة)
- السلامة القانونية (PDPL-aware، لا scraping، لا LinkedIn bots)
- الـ routing (كل lead معه next_action واضح، ليس مجرد اسم)
"""


OPPORTUNITY_TYPES = {
    "DIRECT_CUSTOMER",
    "AGENCY_PARTNER",
    "IMPLEMENTATION_PARTNER",
    "REFERRAL_PARTNER",
    "STRATEGIC_PARTNER",
    "CONTENT_COLLABORATION",
    "INVESTOR_OR_ADVISOR",
    "SUPPLIER_OR_INTEGRATION",
    "B2C_AUDIENCE",
}
PRIORITY_TIERS = {"P0", "P1", "P2", "BACKLOG"}
RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "BLOCKED"}
CHANNELS = {
    "LINKEDIN_MANUAL",
    "EMAIL",
    "WHATSAPP_WARM_ONLY",
    "PARTNER_INTRO",
    "PHONE",
    "CONTENT_MENTION",
    "IN_PERSON_EVENT",
    "HOLD_FOR_APPROVAL",
}
NEXT_ACTIONS = {
    "RESEARCH_MORE", "ENRICH_ACCOUNT", "SCORE_LEAD",
    "PREPARE_DM", "PREPARE_EMAIL", "PREPARE_WHATSAPP",
    "PREPARE_PARTNER_PITCH", "PREPARE_INVESTOR_NOTE",
    "PREPARE_DEMO_FLOW", "PREPARE_NEGOTIATION_RESPONSE",
    "SEND_IF_AUTHORIZED", "ASK_HUMAN_FINAL_SEND",
    "BOOK_DEMO", "REQUEST_PAYMENT", "ROUTE_TO_MANUAL_PAYMENT",
    "ONBOARD_CUSTOMER", "FOLLOW_UP", "STOP_CONTACT", "DISQUALIFY",
}


@dataclass
class LeadCandidate:
    company_ar: str
    company_en: str
    industry: str
    est_size: str
    website: str | None
    linkedin: str | None
    opportunity_type: str
    decision_maker_hints: list[str]
    signals: list[str]
    fit_score: int
    intent_score: int
    access_score: int
    revenue_score: int
    priority_score: int
    priority_tier: str
    risk_level: str
    recommended_channel: str
    next_action: str
    outreach_opening: str
    message_angle: str
    reason: str
    evidence: str
    compliance_note: str
    confidence: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProspectResult:
    use_case: str
    icp: str
    count_requested: int
    count_returned: int
    leads: list[LeadCandidate]
    search_notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "use_case": self.use_case,
            "icp": self.icp,
            "count_requested": self.count_requested,
            "count_returned": self.count_returned,
            "leads": [l.to_dict() for l in self.leads],
            "search_notes": self.search_notes,
        }


class ProspectorAgent(BaseAgent):
    """
    Natural-language ICP → ranked list of real leads.
    Uses the LLM router's RESEARCH task (Gemini primary, with fallback chain).
    """

    name = "prospector"

    async def run(
        self,
        icp: str,
        use_case: str = "sales",
        count: int = 10,
    ) -> ProspectResult:
        count = max(1, min(MAX_COUNT, int(count)))
        use_case = (use_case or "sales").strip().lower()
        if use_case not in USE_CASES:
            use_case = "sales"

        user_prompt = self._build_user_prompt(icp=icp, use_case=use_case, count=count)

        self.log.info(
            "prospector_run use_case=%s count=%d icp_len=%d",
            use_case,
            count,
            len(icp or ""),
        )

        response = await self.router.run(
            task=Task.RESEARCH,
            messages=[Message(role="user", content=user_prompt)],
            system=SYSTEM_PROMPT,
            max_tokens=4096,
            temperature=0.3,
        )

        parsed = self._parse_json(response.text)
        raw_leads = parsed.get("leads") or []
        search_notes = str(parsed.get("search_notes") or "")

        leads: list[LeadCandidate] = []
        for item in raw_leads[:count]:
            lead = self._safe_lead(item)
            if lead is not None:
                leads.append(lead)

        # Sort by priority_score (already weighted), then confidence
        leads.sort(key=lambda l: (l.priority_score, l.confidence), reverse=True)

        return ProspectResult(
            use_case=use_case,
            icp=icp,
            count_requested=count,
            count_returned=len(leads),
            leads=leads,
            search_notes=search_notes,
        )

    # ── internals ──────────────────────────────────────────────
    def _build_user_prompt(self, *, icp: str, use_case: str, count: int) -> str:
        return (
            f"حالة الاستخدام: {use_case} — {USE_CASES[use_case]}\n\n"
            f"وصف العميل المثالي (ICP):\n{icp.strip()}\n\n"
            f"أعد {count} leads حقيقية مطابقة للـ ICP، مرتّبة من الأعلى fit_score.\n"
            f"إذا الطلب متعلق بالسعودية أو الخليج، ركّز على الشركات المحلية أولاً.\n"
            f"تذكير: لا تختلق شركات. أعد JSON فقط — بدون markdown code fences."
        )

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        if not text:
            return {}
        # Strip optional code fences
        t = text.strip()
        t = re.sub(r"^```(?:json)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
        try:
            return json.loads(t)
        except Exception:
            # Try to extract the first {...} block
            m = re.search(r"\{.*\}", t, re.DOTALL)
            if not m:
                return {}
            try:
                return json.loads(m.group(0))
            except Exception:
                return {}

    @staticmethod
    def _coerce_enum(value: Any, allowed: set[str], default: str) -> str:
        v = str(value or "").strip().upper().replace("-", "_").replace(" ", "_")
        return v if v in allowed else default

    @staticmethod
    def _derive_tier(score: int) -> str:
        if score >= 80:
            return "P0"
        if score >= 65:
            return "P1"
        if score >= 45:
            return "P2"
        return "BACKLOG"

    @classmethod
    def _safe_lead(cls, item: Any) -> LeadCandidate | None:
        if not isinstance(item, dict):
            return None
        try:
            company_ar = str(item.get("company_ar") or "").strip()
            company_en = str(item.get("company_en") or "").strip()
            if not (company_ar or company_en):
                return None

            fit = int(max(0, min(40, item.get("fit_score") or 0)))
            intent = int(max(0, min(30, item.get("intent_score") or 0)))
            access = int(max(0, min(15, item.get("access_score") or 0)))
            revenue = int(max(0, min(15, item.get("revenue_score") or 0)))
            priority_raw = item.get("priority_score")
            priority = (
                int(max(0, min(100, priority_raw)))
                if isinstance(priority_raw, (int, float))
                else (fit + intent + access + revenue)
            )
            tier_raw = item.get("priority_tier")
            tier = (
                str(tier_raw).upper()
                if str(tier_raw).upper() in PRIORITY_TIERS
                else cls._derive_tier(priority)
            )

            opportunity_type = cls._coerce_enum(
                item.get("opportunity_type"), OPPORTUNITY_TYPES, "DIRECT_CUSTOMER"
            )
            risk = cls._coerce_enum(item.get("risk_level"), RISK_LEVELS, "MEDIUM")
            channel = cls._coerce_enum(
                item.get("recommended_channel"), CHANNELS, "LINKEDIN_MANUAL"
            )
            next_action = cls._coerce_enum(
                item.get("next_action"), NEXT_ACTIONS, "PREPARE_DM"
            )

            return LeadCandidate(
                company_ar=company_ar or company_en,
                company_en=company_en or company_ar,
                industry=str(item.get("industry") or "").strip(),
                est_size=str(item.get("est_size") or "").strip(),
                website=(str(item.get("website")).strip() if item.get("website") else None),
                linkedin=(str(item.get("linkedin")).strip() if item.get("linkedin") else None),
                opportunity_type=opportunity_type,
                decision_maker_hints=[
                    str(x) for x in (item.get("decision_maker_hints") or []) if x
                ][:5],
                signals=[str(x) for x in (item.get("signals") or []) if x][:8],
                fit_score=fit,
                intent_score=intent,
                access_score=access,
                revenue_score=revenue,
                priority_score=priority,
                priority_tier=tier,
                risk_level=risk,
                recommended_channel=channel,
                next_action=next_action,
                outreach_opening=str(item.get("outreach_opening") or "").strip()[:280],
                message_angle=str(item.get("message_angle") or "").strip()[:280],
                reason=str(item.get("reason") or "").strip()[:280],
                evidence=str(item.get("evidence") or "").strip()[:280],
                compliance_note=str(
                    item.get("compliance_note")
                    or "Public business contact; single personalized manual DM; no bots."
                ).strip()[:280],
                confidence=int(max(0, min(100, item.get("confidence") or 0))),
            )
        except Exception:
            return None

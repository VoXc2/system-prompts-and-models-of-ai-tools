"""
5-Dimension Lead Scoring Engine
Fit | Intent | Access | Value | Urgency

Master Priority Score = weighted sum → P1/P2/P3/P4 tier
Each dimension returns 0-100. Final score 0-100.
"""
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass


@dataclass
class ScoreBreakdown:
    fit_score: int = 0          # Is this company our ICP?
    intent_score: int = 0       # Are they showing buying signals?
    access_score: int = 0       # Can we reach the right person?
    value_score: int = 0        # What's the potential deal value?
    urgency_score: int = 0      # Is now the right moment?
    master_score: int = 0       # Weighted composite
    priority_tier: str = "P4"  # P1 | P2 | P3 | P4
    priority_label_ar: str = "أرشيف"
    score_reasons: List[str] = None
    next_action: str = ""
    next_action_ar: str = ""

    def __post_init__(self):
        if self.score_reasons is None:
            self.score_reasons = []


# Signal → intent score contribution
INTENT_SIGNAL_WEIGHTS = {
    "hiring": 25,
    "expansion": 20,
    "funding": 30,
    "digital_transformation": 20,
    "partnership": 15,
    "ipo": 35,
    "new_product": 10,
    "pain_point_crm": 25,
    "pain_point_outreach": 20,
    "regulation": 15,
}

# Industry → fit contribution (for Dealix ICP)
INDUSTRY_FIT = {
    "technology": 100, "tech": 100, "تقنية": 100, "software": 95, "saas": 95,
    "banking": 90, "financial": 90, "مالية": 90, "بنوك": 90, "fintech": 95,
    "healthcare": 85, "رعاية صحية": 85, "hospital": 80,
    "real estate": 80, "عقارات": 80,
    "manufacturing": 75, "تصنيع": 75, "industrial": 70,
    "retail": 70, "تجزئة": 70, "e-commerce": 80,
    "logistics": 75, "لوجستيات": 75, "supply chain": 75,
    "education": 65, "تعليم": 65,
    "government": 60, "حكومة": 60,
    "media": 60, "إعلام": 60,
}

# Company size → value score
SIZE_VALUE = {
    "1-50": 30,
    "50-200": 55,
    "200-1000": 80,
    "1000+": 100,
    "unknown": 40,
}

# Seniority → access score
SENIORITY_ACCESS = {
    range(90, 101): 100,   # C-level
    range(80, 90): 85,     # VP
    range(70, 80): 70,     # Director
    range(55, 70): 55,     # Manager
    range(0, 55): 30,      # Individual contributor
}

PRIORITY_THRESHOLDS = {
    "P1": 70,   # Outreach now
    "P2": 50,   # Enrich more
    "P3": 35,   # Nurture
}

PRIORITY_LABELS_AR = {
    "P1": "وصول فوري",
    "P2": "إثراء إضافي",
    "P3": "تغذية ورعاية",
    "P4": "قائمة انتظار",
}

NEXT_ACTIONS = {
    "P1": ("Send personalized outreach — high-priority lead", "أرسل رسالة مخصصة — ليد أولوية عالية"),
    "P2": ("Enrich contact data, find decision maker", "أثرِ بيانات الاتصال وحدد صانع القرار"),
    "P3": ("Add to nurture sequence, monitor signals", "أضف إلى تسلسل التغذية وراقب الإشارات"),
    "P4": ("Archive and watch for trigger", "أرشف وراقب الإشارات المستقبلية"),
}


def get_seniority_access_score(decision_maker_score: int) -> int:
    for r, score in SENIORITY_ACCESS.items():
        if decision_maker_score in r:
            return score
    return 30


def score_fit(enriched_lead) -> Tuple[int, List[str]]:
    """Score how well this company matches ICP"""
    reasons = []
    score = 0

    # Industry fit
    industry = (enriched_lead.industry or enriched_lead.raw_snippet or "").lower()
    best_industry_score = 0
    for kw, val in INDUSTRY_FIT.items():
        if kw in industry:
            best_industry_score = max(best_industry_score, val)
    if best_industry_score > 0:
        score += best_industry_score * 0.5
        reasons.append(f"Industry match: {best_industry_score}%")

    # Company size fit
    size_score = SIZE_VALUE.get(enriched_lead.company_size, 40)
    score += size_score * 0.3
    if enriched_lead.company_size != "unknown":
        reasons.append(f"Size '{enriched_lead.company_size}': {size_score}%")

    # Has website / domain
    if enriched_lead.domain:
        score += 8
        reasons.append("Has domain")

    # Saudi / Gulf region
    text = f"{enriched_lead.headquarters} {enriched_lead.region} {enriched_lead.raw_snippet}".lower()
    if any(kw in text for kw in ["saudi", "ksa", "السعودية", "الرياض", "riyadh", "جدة", "jeddah", "الخليج", "gulf"]):
        score += 12
        reasons.append("Saudi/Gulf region")

    return min(100, int(score)), reasons


def score_intent(enriched_lead) -> Tuple[int, List[str]]:
    """Score buying intent based on signals"""
    reasons = []
    score = 0

    for signal in enriched_lead.signals:
        contribution = INTENT_SIGNAL_WEIGHTS.get(signal, 5)
        score += contribution
        reasons.append(f"Signal '{signal}': +{contribution}")

    # Recent news adds intent
    if enriched_lead.recent_news:
        score += min(20, len(enriched_lead.recent_news) * 5)
        reasons.append(f"{len(enriched_lead.recent_news)} recent news items")

    # Pain point keywords in snippet
    text = (enriched_lead.raw_snippet or "").lower()
    pain_keywords = ["struggling", "challenge", "problem", "need", "looking for",
                     "تحدي", "مشكلة", "نحتاج", "نبحث عن"]
    if any(kw in text for kw in pain_keywords):
        score += 15
        reasons.append("Pain point language detected")

    return min(100, score), reasons


def score_access(enriched_lead) -> Tuple[int, List[str]]:
    """Score reachability — can we actually contact the right person?"""
    reasons = []
    score = 0

    if enriched_lead.contact_email:
        score += 40
        reasons.append("Has email")
    if enriched_lead.contact_phone:
        score += 20
        reasons.append("Has phone")
    if enriched_lead.contact_linkedin:
        score += 25
        reasons.append("Has LinkedIn profile")
    if enriched_lead.domain:
        score += 20
        reasons.append("Has domain (email inferable)")

    # Decision maker seniority
    seniority_score = get_seniority_access_score(enriched_lead.decision_maker_score)
    score = int(score * 0.6 + seniority_score * 0.4)
    if enriched_lead.contact_title:
        reasons.append(f"Title seniority: {seniority_score}%")

    return min(100, score), reasons


def score_value(enriched_lead) -> Tuple[int, List[str]]:
    """Estimate potential deal value"""
    reasons = []

    # Company size as proxy for revenue potential
    size_score = SIZE_VALUE.get(enriched_lead.company_size, 40)

    # Revenue estimate
    rev = enriched_lead.annual_revenue_sar
    if rev > 100_000_000:
        size_score = max(size_score, 100)
        reasons.append(f"Revenue >100M SAR")
    elif rev > 10_000_000:
        size_score = max(size_score, 80)
        reasons.append(f"Revenue >10M SAR")
    elif rev > 0:
        reasons.append(f"Revenue data available")

    # Tech stack indicates budget
    if len(enriched_lead.tech_stack) >= 3:
        size_score = min(100, size_score + 10)
        reasons.append(f"Rich tech stack ({len(enriched_lead.tech_stack)} tools)")

    reasons.append(f"Size-based value score: {size_score}%")
    return min(100, size_score), reasons


def score_urgency(enriched_lead) -> Tuple[int, List[str]]:
    """Score how urgent the timing is"""
    reasons = []
    score = 0

    # Time-sensitive signals
    urgent_signals = {"funding": 40, "ipo": 50, "expansion": 30, "hiring": 20, "new_product": 25}
    for sig in enriched_lead.signals:
        if sig in urgent_signals:
            score += urgent_signals[sig]
            reasons.append(f"Urgent signal '{sig}': +{urgent_signals[sig]}")

    # Fresh news
    if len(enriched_lead.recent_news) >= 2:
        score += 15
        reasons.append("Multiple recent news items")

    # If just discovered (high source confidence)
    if enriched_lead.enrichment_confidence >= 0.7:
        score += 10
        reasons.append("High confidence data")

    return min(100, score), reasons


def score_lead(enriched_lead, weights: Dict[str, float] = None) -> ScoreBreakdown:
    """
    Compute full 5-dimension score for an enriched lead.
    Returns ScoreBreakdown with tier and next action.
    """
    if weights is None:
        weights = {"fit": 0.30, "intent": 0.25, "access": 0.15, "value": 0.20, "urgency": 0.10}

    fit, fit_reasons = score_fit(enriched_lead)
    intent, intent_reasons = score_intent(enriched_lead)
    access, access_reasons = score_access(enriched_lead)
    value, value_reasons = score_value(enriched_lead)
    urgency, urgency_reasons = score_urgency(enriched_lead)

    master = int(
        fit * weights["fit"] +
        intent * weights["intent"] +
        access * weights["access"] +
        value * weights["value"] +
        urgency * weights["urgency"]
    )

    if master >= PRIORITY_THRESHOLDS["P1"]:
        tier = "P1"
    elif master >= PRIORITY_THRESHOLDS["P2"]:
        tier = "P2"
    elif master >= PRIORITY_THRESHOLDS["P3"]:
        tier = "P3"
    else:
        tier = "P4"

    all_reasons = (
        [f"[Fit {fit}]"] + fit_reasons[:2] +
        [f"[Intent {intent}]"] + intent_reasons[:2] +
        [f"[Access {access}]"] + access_reasons[:2] +
        [f"[Value {value}]"] + value_reasons[:1] +
        [f"[Urgency {urgency}]"] + urgency_reasons[:1]
    )

    en_action, ar_action = NEXT_ACTIONS[tier]

    return ScoreBreakdown(
        fit_score=fit,
        intent_score=intent,
        access_score=access,
        value_score=value,
        urgency_score=urgency,
        master_score=master,
        priority_tier=tier,
        priority_label_ar=PRIORITY_LABELS_AR[tier],
        score_reasons=all_reasons,
        next_action=en_action,
        next_action_ar=ar_action,
    )


def score_batch(enriched_leads: List, weights: Dict[str, float] = None) -> List[Dict]:
    """Score a batch of enriched leads and return sorted results"""
    results = []
    for lead in enriched_leads:
        breakdown = score_lead(lead, weights)
        results.append({
            "lead": lead.to_dict(),
            "score": {
                "fit": breakdown.fit_score,
                "intent": breakdown.intent_score,
                "access": breakdown.access_score,
                "value": breakdown.value_score,
                "urgency": breakdown.urgency_score,
                "master": breakdown.master_score,
                "tier": breakdown.priority_tier,
                "tier_label_ar": breakdown.priority_label_ar,
                "reasons": breakdown.score_reasons,
                "next_action": breakdown.next_action,
                "next_action_ar": breakdown.next_action_ar,
            }
        })
    # Sort by master score descending
    results.sort(key=lambda x: x["score"]["master"], reverse=True)
    return results

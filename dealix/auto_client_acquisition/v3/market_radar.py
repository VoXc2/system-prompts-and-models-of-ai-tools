"""Saudi Market Radar for Dealix v3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from math import exp
from typing import Any


@dataclass(frozen=True)
class MarketSignal:
    company: str
    sector: str
    city: str
    signal_type: str
    strength: float
    days_old: int = 0
    evidence: str = ""

    def score(self) -> float:
        freshness = exp(-self.days_old / 21)
        sector_boost = {
            "clinics": 1.20,
            "real_estate": 1.15,
            "logistics": 1.10,
            "training": 1.08,
            "hospitality": 1.05,
        }.get(self.sector, 1.0)
        return round(max(0.0, min(100.0, self.strength * freshness * sector_boost)), 2)

    def why_now_ar(self) -> str:
        labels = {
            "hiring_sales": "الشركة توظف في المبيعات، وهذا غالباً يعني توسع أو ضغط على توليد الطلب.",
            "new_branch": "يوجد مؤشر توسع/فرع جديد، وهذا وقت ممتاز لعرض نظام نمو أسرع.",
            "booking_link": "لديهم مسار حجز واضح، ويمكن تحسين الردود والتحويل عبر واتساب.",
            "website_change": "تغير في الموقع يدل على تحديث عرض أو حملة جديدة.",
            "event_participation": "مشاركتهم في فعالية تعني استعداد أعلى لعلاقات وشراكات جديدة.",
            "website_updated": "تحديث الموقع يعني حملة أو منتج جديد يستحق رسالة ذات سياق.",
            "new_ad_activity": "نشاط إعلاني جديد يعني استثمار في الطلب.",
            "new_funding": "تمويل جديد يعني نافذة شراء وتوسع.",
            "tender_opportunity": "مناقصة أو فرصة توريد تفتح باب B2B مباشر.",
            "review_spike": "تغير في التقييمات قد يعني ضغط تشغيل أو نمو حركة.",
            "job_posts": "وظائف متعددة تشير إلى نمو تنظيمي.",
            "crm_detected": "أثر تقني/CRM يعني نضج عمليات المبيعات.",
            "whatsapp_heavy_business": "أعمال تعتمد واتساب بشكل كبير — قناة مناسبة لكن بموافقة.",
            "slow_response_risk": "بطء الرد قد يعني تسريب فرص — فرصة لتحسين SLA.",
            "competitor_campaign": "حركة منافس تستدعي رداً استراتيجياً وليس تقليداً أعمى.",
            "new_product_launch": "إطلاق منتج يفتح محادثات شراكة أو توسعة.",
            "new_partnership": "شراكة جديدة تدل على انفتاح على قنوات.",
        }
        return labels.get(self.signal_type, "يوجد مؤشر سوق يستحق المتابعة الآن.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "company": self.company,
            "sector": self.sector,
            "city": self.city,
            "signal_type": self.signal_type,
            "strength": self.strength,
            "days_old": self.days_old,
            "score": self.score(),
            "evidence": self.evidence,
            "why_now_ar": self.why_now_ar(),
        }


def rank_opportunities(signals: list[MarketSignal], limit: int = 20) -> list[dict[str, Any]]:
    ranked = sorted(signals, key=lambda item: item.score(), reverse=True)
    return [item.to_dict() for item in ranked[:limit]]


def demo_signals() -> list[MarketSignal]:
    return [
        MarketSignal("عيادة نمو الرياض", "clinics", "Riyadh", "hiring_sales", 92, 2, "3 sales roles posted"),
        MarketSignal("وسيط عقار جدة", "real_estate", "Jeddah", "new_branch", 85, 5, "new branch page"),
        MarketSignal("أكاديمية تدريب الشرقية", "training", "Dammam", "booking_link", 80, 1, "public booking link"),
    ]


def signal_catalog() -> list[dict[str, Any]]:
    """Deterministic metadata for GTM/docs — confidence is illustrative until wired to data feeds."""
    types = [
        ("hiring_sales", "توسع فريق المبيعات غالباً يعني ضغط على الأنابيب.", ["b2b_saas", "logistics"], 0.72),
        ("opening_branch", "فرع جديد = توسع جغرافي وشراء.", ["real_estate", "hospitality"], 0.68),
        ("website_updated", "تحديث الموقع = حملة أو تموضع جديد.", ["agencies", "b2b_saas"], 0.55),
        ("booking_link_found", "رابط حجز واضح يسهّل متابعة منظمة.", ["clinics", "training"], 0.7),
        ("new_ad_activity", "إعلانات جديدة = استثمار في الطلب.", ["restaurants", "real_estate"], 0.5),
        ("new_funding", "تمويل يفتح ميزانية ومبادرات.", ["b2b_saas"], 0.8),
        ("event_participation", "فعاليات = networking وفرص شراكة.", ["training", "agencies"], 0.62),
        ("new_partnership", "شراكة تدل على قنوات جديدة.", ["logistics", "construction"], 0.58),
        ("new_product_launch", "منتج جديد يحتاج رسائل تفعيل.", ["b2b_saas"], 0.65),
        ("tender_opportunity", "مناقصات تتطلب دقة وامتثال.", ["construction", "logistics"], 0.75),
        ("review_spike", "تقييمات متغيرة تستدعي متابعة تجربة.", ["restaurants", "hospitality"], 0.45),
        ("job_posts", "وظائف متعددة = نمو.", ["b2b_saas", "training"], 0.52),
        ("crm_detected", "نضج عمليات = فرصة لطبقة إيرادات.", ["b2b_saas"], 0.48),
        ("whatsapp_heavy_business", "اعتماد واتساب عالٍ — مناسب لكن بموافقة.", ["clinics", "real_estate"], 0.6),
        ("slow_response_risk", "بطء ردود = تسريب فرص.", ["agencies", "b2b_saas"], 0.5),
        ("competitor_campaign", "حركة منافس — رد استراتيجي.", ["b2b_saas"], 0.55),
    ]
    out: list[dict[str, Any]] = []
    for st, why, sectors, conf in types:
        out.append(
            {
                "signal_type": st,
                "why_it_matters_ar": why,
                "applicable_sectors": sectors,
                "suggested_message_angle_ar": "ركّز على «لماذا الآن» بدون مبالغة؛ اربط الإشارة بحل Dealix.",
                "confidence_demo": conf,
                "risk_compliance_notes_ar": "تأكد من opt-in قبل واتساب تسويقي؛ لا إرسال بارد.",
            }
        )
    return out


def sector_heatmap(signals: list[MarketSignal]) -> list[dict[str, Any]]:
    buckets: dict[str, list[float]] = {}
    for signal in signals:
        buckets.setdefault(signal.sector, []).append(signal.score())
    return [
        {"sector": sector, "avg_intent": round(sum(scores) / len(scores), 2), "signals": len(scores)}
        for sector, scores in sorted(buckets.items(), key=lambda item: sum(item[1]) / len(item[1]), reverse=True)
    ]

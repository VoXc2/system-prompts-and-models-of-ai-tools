"""
Trigger Alert System — Real-time intent signal detection
Monitors: job postings, news, funding, expansion, partnerships, regulatory changes.
Runs as background scan and emits trigger events per lead/company.
"""
import re
import time
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class TriggerEvent:
    """A detected trigger event for a company"""
    company_name: str
    trigger_type: str           # hiring | funding | expansion | ipo | partnership | regulation | news
    trigger_label_ar: str
    signal_strength: int        # 0-100
    evidence: str               # snippet or description
    source_url: str
    detected_at: str
    recommended_action_ar: str
    recommended_action_en: str


TRIGGER_DEFINITIONS = {
    "hiring": {
        "label_ar": "توظيف نشط",
        "queries": ["{company} hiring 2025", "{company} وظائف 2025", "{company} jobs"],
        "keywords": ["hiring", "join our team", "we're looking", "وظائف", "نوظف", "فرص عمل"],
        "strength": 60,
        "action_ar": "اتصل الآن — الشركة توسّع فريقها وستحتاج منظومة مبيعات",
        "action_en": "Reach out now — they're scaling and will need a sales OS",
    },
    "funding": {
        "label_ar": "تمويل جديد",
        "queries": ["{company} funding 2025", "{company} investment raised", "{company} تمويل"],
        "keywords": ["raised", "funding", "series", "investment", "تمويل", "استثمار", "جولة"],
        "strength": 90,
        "action_ar": "أولوية قصوى — اتصل خلال 48 ساعة من التمويل",
        "action_en": "Top priority — contact within 48 hours of funding",
    },
    "expansion": {
        "label_ar": "توسع جديد",
        "queries": ["{company} expansion 2025", "{company} new office", "{company} توسع"],
        "keywords": ["expansion", "new market", "new office", "opens", "توسع", "افتتاح", "سوق جديد"],
        "strength": 75,
        "action_ar": "تواصل حول كيفية دعم توسعهم بمنظومة إيرادات",
        "action_en": "Reach out about supporting their expansion with a revenue system",
    },
    "partnership": {
        "label_ar": "شراكة جديدة",
        "queries": ["{company} partnership 2025", "{company} شراكة"],
        "keywords": ["partnership", "collaboration", "alliance", "شراكة", "تعاون", "تحالف"],
        "strength": 55,
        "action_ar": "استفسر عن فرص الشراكة الاستراتيجية",
        "action_en": "Inquire about strategic partnership opportunities",
    },
    "ipo": {
        "label_ar": "استعداد للطرح العام",
        "queries": ["{company} IPO 2025 2026", "{company} اكتتاب طرح عام"],
        "keywords": ["ipo", "initial public offering", "طرح عام", "اكتتاب", "تداول"],
        "strength": 95,
        "action_ar": "طوارئ — الطرح العام يستلزم منظومة إيرادات موثوقة وقابلة للتدقيق",
        "action_en": "Emergency priority — IPO demands auditable, reliable revenue infrastructure",
    },
    "digital_transformation": {
        "label_ar": "تحول رقمي",
        "queries": ["{company} digital transformation", "{company} تحول رقمي", "{company} digitization"],
        "keywords": ["digital transformation", "digitization", "modernization", "تحول رقمي", "رقمنة"],
        "strength": 65,
        "action_ar": "اعرض كيف Dealix يُكمّل مبادرة التحول الرقمي لديهم",
        "action_en": "Show how Dealix completes their digital transformation initiative",
    },
    "regulation": {
        "label_ar": "تغيير تنظيمي",
        "queries": ["{company} PDPL ZATCA compliance 2025", "{company} حوكمة ضريبة"],
        "keywords": ["pdpl", "zatca", "compliance", "regulation", "حوكمة", "امتثال", "ضريبة"],
        "strength": 50,
        "action_ar": "ناقش كيف Dealix يُساعد على الامتثال التنظيمي",
        "action_en": "Discuss how Dealix supports regulatory compliance",
    },
}


def search_triggers_for_company(company_name: str, trigger_type: str) -> List[Dict]:
    """Search for trigger signals for a specific company"""
    definition = TRIGGER_DEFINITIONS.get(trigger_type, {})
    queries = definition.get("queries", [])
    keywords = definition.get("keywords", [])
    results = []

    for query_template in queries[:2]:  # Limit queries per trigger
        query = query_template.replace("{company}", company_name)
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; DealixBot/1.0)"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html)
            urls = re.findall(r'<a class="result__a" href="([^"]+)"', html)

            for i, snippet in enumerate(snippets[:3]):
                clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip().lower()
                if any(kw in clean_snippet for kw in keywords):
                    results.append({
                        "snippet": re.sub(r'<[^>]+>', '', snippet).strip(),
                        "url": urls[i] if i < len(urls) else "",
                        "query": query,
                    })
        except Exception:
            pass
        time.sleep(0.3)

    return results


def scan_company_for_triggers(company_name: str) -> List[TriggerEvent]:
    """Scan all trigger types for a given company"""
    events = []
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for trigger_type, definition in TRIGGER_DEFINITIONS.items():
        results = search_triggers_for_company(company_name, trigger_type)
        if results:
            best = results[0]
            event = TriggerEvent(
                company_name=company_name,
                trigger_type=trigger_type,
                trigger_label_ar=definition["label_ar"],
                signal_strength=definition["strength"],
                evidence=best["snippet"][:500],
                source_url=best["url"][:300],
                detected_at=now,
                recommended_action_ar=definition["action_ar"],
                recommended_action_en=definition["action_en"],
            )
            events.append(event)

    return events


def scan_watchlist(company_names: List[str], delay: float = 1.0) -> Dict[str, List[Dict]]:
    """
    Scan a watchlist of companies for all trigger types.
    Returns dict: {company_name: [trigger_event_dicts]}
    """
    all_triggers = {}

    for company in company_names:
        events = scan_company_for_triggers(company)
        if events:
            all_triggers[company] = [
                {
                    "type": e.trigger_type,
                    "label_ar": e.trigger_label_ar,
                    "strength": e.signal_strength,
                    "evidence": e.evidence,
                    "url": e.source_url,
                    "detected_at": e.detected_at,
                    "action_ar": e.recommended_action_ar,
                    "action_en": e.recommended_action_en,
                }
                for e in events
            ]
        time.sleep(delay)

    return all_triggers


def get_strongest_trigger(events: List[Dict]) -> Optional[Dict]:
    """Return the highest-priority trigger from a list"""
    if not events:
        return None
    return max(events, key=lambda e: e.get("strength", 0))

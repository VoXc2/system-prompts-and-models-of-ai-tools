"""
Signal detectors — pure functions over raw observations.

Production: each detector has a real source adapter (LinkedIn jobs API,
Wayback Machine for diffs, Google Ads transparency, Saudi tender feed,
funding announcement RSS, etc.). The detector itself just sees normalized
input + emits a typed SignalDetection.

This module exposes 5 core detectors. More can be added as the catalog
of adapters grows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

# ── Signal taxonomy — 16 signal types Dealix tracks ──────────────
SIGNAL_TYPES: tuple[str, ...] = (
    "hiring_sales_rep",
    "hiring_marketing",
    "hiring_engineering",
    "new_branch_opened",
    "new_service_launched",
    "booking_page_added",
    "whatsapp_business_added",
    "ads_volume_increased",
    "website_redesigned",
    "exhibition_participation",
    "negative_review_spike",
    "sector_pulse_rising",
    "tender_published",
    "leadership_change",
    "funding_round",
    "vision2030_alignment",
)


@dataclass
class SignalDetection:
    """A detected signal — feeds Why-Now? engine + Daily Growth Run."""

    company_id: str
    signal_type: str
    detected_at: datetime
    source: str
    confidence: float          # 0..1
    evidence_url: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


# ── Hiring Signal Detector ───────────────────────────────────────
def detect_hiring_signal(
    *,
    company_id: str,
    job_postings: list[dict[str, Any]],
    now: datetime | None = None,
) -> list[SignalDetection]:
    """
    Detect sales / marketing / engineering hiring signals.

    Each posting is dict with: title, posted_at (datetime), url.
    """
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    out: list[SignalDetection] = []
    for jp in job_postings:
        title = (jp.get("title") or "").lower()
        posted = jp.get("posted_at")
        if not posted:
            continue
        if posted.tzinfo:
            posted = posted.replace(tzinfo=None)
        if (n - posted) > timedelta(days=45):
            continue  # too old to act on

        if any(k in title for k in ("sdr", "sales", "account executive", "ae", "مبيعات")):
            out.append(SignalDetection(
                company_id=company_id,
                signal_type="hiring_sales_rep",
                detected_at=posted,
                source="linkedin_jobs",
                confidence=0.9,
                evidence_url=jp.get("url"),
                payload={"title": jp.get("title")},
            ))
        elif any(k in title for k in ("marketing", "growth", "تسويق")):
            out.append(SignalDetection(
                company_id=company_id,
                signal_type="hiring_marketing",
                detected_at=posted,
                source="linkedin_jobs",
                confidence=0.8,
                evidence_url=jp.get("url"),
                payload={"title": jp.get("title")},
            ))
        elif any(k in title for k in ("engineer", "developer", "backend", "frontend", "مبرمج")):
            out.append(SignalDetection(
                company_id=company_id,
                signal_type="hiring_engineering",
                detected_at=posted,
                source="linkedin_jobs",
                confidence=0.7,
                evidence_url=jp.get("url"),
                payload={"title": jp.get("title")},
            ))
    return out


# ── Website Change Detector ──────────────────────────────────────
def detect_website_change(
    *,
    company_id: str,
    diff: dict[str, Any],
    now: datetime | None = None,
) -> list[SignalDetection]:
    """
    Detect signals from a website diff:
      - new booking page added
      - new pricing page
      - WhatsApp Business widget added
      - new service / product launched
    """
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    out: list[SignalDetection] = []
    added_paths = set(diff.get("added_paths", []))
    added_widgets = set(diff.get("added_widgets", []))

    booking_keywords = ("/booking", "/book", "/calendly", "/appointment", "/حجز")
    if any(any(k in p for k in booking_keywords) for p in added_paths):
        out.append(SignalDetection(
            company_id=company_id,
            signal_type="booking_page_added",
            detected_at=n,
            source="website_diff",
            confidence=0.85,
            evidence_url=diff.get("homepage_url"),
            payload={"new_paths": list(added_paths)},
        ))

    if "whatsapp_business" in added_widgets or "whatsapp_chat" in added_widgets:
        out.append(SignalDetection(
            company_id=company_id,
            signal_type="whatsapp_business_added",
            detected_at=n,
            source="website_diff",
            confidence=0.95,
            evidence_url=diff.get("homepage_url"),
            payload={"widgets": list(added_widgets)},
        ))

    service_paths = ("/services/", "/products/", "/خدماتنا/", "/منتجاتنا/")
    new_services = [p for p in added_paths if any(s in p for s in service_paths)]
    if new_services:
        out.append(SignalDetection(
            company_id=company_id,
            signal_type="new_service_launched",
            detected_at=n,
            source="website_diff",
            confidence=0.7,
            evidence_url=diff.get("homepage_url"),
            payload={"new_pages": new_services},
        ))

    if diff.get("major_redesign"):
        out.append(SignalDetection(
            company_id=company_id,
            signal_type="website_redesigned",
            detected_at=n,
            source="website_diff",
            confidence=0.8,
            evidence_url=diff.get("homepage_url"),
        ))

    return out


# ── Ads Volume Detector ──────────────────────────────────────────
def detect_ads_signal(
    *,
    company_id: str,
    weekly_ad_spend_history: list[float],
    now: datetime | None = None,
) -> list[SignalDetection]:
    """
    Detect a meaningful jump in advertising spend.

    weekly_ad_spend_history: most recent week LAST. Need >= 4 weeks of history.
    """
    if len(weekly_ad_spend_history) < 4:
        return []
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    recent = weekly_ad_spend_history[-2:]
    baseline = weekly_ad_spend_history[:-2]
    if not baseline or sum(baseline) == 0:
        return []
    baseline_avg = sum(baseline) / len(baseline)
    recent_avg = sum(recent) / len(recent)
    if recent_avg < baseline_avg * 1.4:  # need 40%+ jump
        return []
    pct = round((recent_avg / baseline_avg - 1) * 100, 1)
    return [SignalDetection(
        company_id=company_id,
        signal_type="ads_volume_increased",
        detected_at=n,
        source="ads_transparency_feed",
        confidence=min(0.95, 0.5 + (pct / 200)),
        payload={"increase_pct": pct, "baseline_avg": baseline_avg, "recent_avg": recent_avg},
    )]


# ── Funding Signal Detector ──────────────────────────────────────
def detect_funding_signal(
    *,
    company_id: str,
    announcements: list[dict[str, Any]],
    now: datetime | None = None,
) -> list[SignalDetection]:
    """
    Detect a recent funding announcement.

    announcements: list of {round_type, amount_sar, announced_at, url}
    """
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    out: list[SignalDetection] = []
    for a in announcements:
        announced = a.get("announced_at")
        if not announced:
            continue
        if announced.tzinfo:
            announced = announced.replace(tzinfo=None)
        if (n - announced) > timedelta(days=90):
            continue
        out.append(SignalDetection(
            company_id=company_id,
            signal_type="funding_round",
            detected_at=announced,
            source="funding_announcement",
            confidence=0.95,
            evidence_url=a.get("url"),
            payload={
                "round_type": a.get("round_type"),
                "amount_sar": a.get("amount_sar"),
            },
        ))
    return out


# ── Tender Signal Detector ───────────────────────────────────────
def detect_tender_signal(
    *,
    company_id: str,
    tenders: list[dict[str, Any]],
    icp_keywords: tuple[str, ...] = (),
    now: datetime | None = None,
) -> list[SignalDetection]:
    """
    Detect a published government / large-corp tender that matches the ICP.

    tenders: list of {title, body, published_at, deadline, url, value_sar}
    """
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    out: list[SignalDetection] = []
    for t in tenders:
        published = t.get("published_at")
        deadline = t.get("deadline")
        if not published:
            continue
        if published.tzinfo:
            published = published.replace(tzinfo=None)
        if deadline and deadline.tzinfo:
            deadline = deadline.replace(tzinfo=None)
        if deadline and deadline < n:
            continue  # already closed
        text = (t.get("title", "") + " " + t.get("body", "")).lower()
        if icp_keywords and not any(kw.lower() in text for kw in icp_keywords):
            continue
        out.append(SignalDetection(
            company_id=company_id,
            signal_type="tender_published",
            detected_at=published,
            source="tender_feed",
            confidence=0.9,
            evidence_url=t.get("url"),
            payload={
                "title": t.get("title"),
                "deadline": deadline.isoformat() if deadline else None,
                "value_sar": t.get("value_sar"),
            },
        ))
    return out

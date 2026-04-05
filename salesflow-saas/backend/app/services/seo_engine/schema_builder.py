"""JSON-LD helpers — no fabricated Review/Rating; LocalBusiness/Organization/WebSite only when data exists."""

from __future__ import annotations

from typing import Any, Dict, Optional


def build_organization_jsonld(
    *,
    name: str,
    url: str,
    logo_url: Optional[str] = None,
    same_as: Optional[list[str]] = None,
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": name,
        "url": url,
    }
    if logo_url:
        data["logo"] = logo_url
    if same_as:
        data["sameAs"] = [s for s in same_as if s]
    return data


def build_website_jsonld(
    *,
    url: str,
    name: str,
    search_action_target: Optional[str] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": name,
        "url": url,
    }
    if search_action_target:
        out["potentialAction"] = {
            "@type": "SearchAction",
            "target": search_action_target,
            "query-input": "required name=search_term_string",
        }
    return out


def build_local_business_jsonld(
    *,
    name: str,
    url: str,
    telephone: Optional[str] = None,
    address_locality: Optional[str] = None,
    address_country: str = "SA",
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": name,
        "url": url,
        "address": {"@type": "PostalAddress", "addressCountry": address_country},
    }
    if telephone:
        data["telephone"] = telephone
    if address_locality:
        data["address"]["addressLocality"] = address_locality
    return data


def build_article_jsonld(
    *,
    headline: str,
    url: str,
    date_published: str,
    author_name: str,
    language: str = "ar",
) -> Dict[str, Any]:
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "url": url,
        "datePublished": date_published,
        "author": {"@type": "Person", "name": author_name},
        "inLanguage": language,
    }


def build_faq_page_jsonld(questions: list[tuple[str, str]]) -> Dict[str, Any]:
    """questions: list of (question, answer) — factual only."""
    items = []
    for q, a in questions:
        items.append(
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
        )
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items}


def build_breadcrumb_jsonld(items: list[tuple[str, str]]) -> Dict[str, Any]:
    """items: (name, url) in order."""
    el = []
    for i, (name, url) in enumerate(items, start=1):
        el.append({"@type": "ListItem", "position": i, "name": name, "item": url})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": el}

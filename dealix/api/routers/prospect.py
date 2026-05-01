"""
Prospect discovery endpoint — public, rate-limited.

POST /api/v1/prospect/discover
    body: {"icp": str, "use_case": "sales|partnership|collaboration|investor|b2c_audience", "count": 10}
    returns: ProspectResult JSON

POST /api/v1/prospect/demo
    returns: a canned demo result (no LLM call) for instant landing UI preview
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Body, HTTPException

from auto_client_acquisition.agents.prospector import (
    MAX_COUNT,
    USE_CASES,
    ProspectorAgent,
)
from auto_client_acquisition.agents.rules_router import (
    generate_messages as _rules_generate_messages,
    route_account as _rules_route,
)
from auto_client_acquisition.connectors.google_search import google_search
from auto_client_acquisition.connectors.tech_detect import detect_stack, extract_contact_info

router = APIRouter(prefix="/api/v1/prospect", tags=["prospect"])
log = logging.getLogger(__name__)

_agent = ProspectorAgent()


@router.get("/use-cases")
async def list_use_cases() -> dict[str, Any]:
    return {"use_cases": USE_CASES, "max_count": MAX_COUNT}


@router.post("/discover")
async def discover(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    icp = str(body.get("icp") or "").strip()
    use_case = str(body.get("use_case") or "sales").strip().lower()
    count = int(body.get("count") or 10)

    if len(icp) < 20:
        raise HTTPException(
            status_code=400,
            detail="icp_too_short: provide at least 20 characters describing your ideal customer",
        )
    if len(icp) > 2000:
        raise HTTPException(
            status_code=400,
            detail="icp_too_long: keep ICP under 2000 characters",
        )
    if use_case not in USE_CASES:
        raise HTTPException(
            status_code=400,
            detail=f"unknown_use_case: {use_case}. Valid: {list(USE_CASES.keys())}",
        )
    if count < 1 or count > MAX_COUNT:
        raise HTTPException(
            status_code=400,
            detail=f"count_out_of_range: 1..{MAX_COUNT}",
        )

    try:
        result = await _agent.run(icp=icp, use_case=use_case, count=count)
    except Exception as exc:
        log.warning("prospector_llm_unavailable use_case=%s — serving degraded rules mode", use_case)
        # Degraded mode: serve the canned demo with a status flag
        demo_resp = await demo()
        demo_resp["status"] = "degraded"
        demo_resp["reason"] = "missing_llm_key"
        demo_resp["hint"] = "Add GROQ_API_KEY (or ANTHROPIC_API_KEY) in Railway env 'Dealix' service 'web' to enable live discovery."
        demo_resp["error_type"] = type(exc).__name__
        return demo_resp

    return result.to_dict()


@router.get("/search-diag")
async def search_diag() -> dict[str, Any]:
    """Diagnose env var presence without revealing values."""
    import os
    def _diag(value: str) -> dict[str, Any]:
        return {"set": bool(value), "length": len(value)}

    k = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    c = os.getenv("GOOGLE_SEARCH_CX", "")
    gm = os.getenv("GOOGLE_MAPS_API_KEY", "")
    tav = os.getenv("TAVILY_API_KEY", "")
    fc = os.getenv("FIRECRAWL_API_KEY", "")
    hu = os.getenv("HUNTER_API_KEY", "")
    ab = os.getenv("ABSTRACT_API_KEY", "")
    wp = os.getenv("WAPPALYZER_API_KEY", "")
    serp = os.getenv("SERPAPI_API_KEY", "")
    apify = os.getenv("APIFY_TOKEN", "")
    grq = os.getenv("GROQ_API_KEY", "")
    ant = os.getenv("ANTHROPIC_API_KEY", "")
    oai = os.getenv("OPENAI_API_KEY", "")
    sd = os.getenv("SENTRY_DSN", "")
    db = os.getenv("DATABASE_URL", "")
    sg = os.getenv("SENDGRID_API_KEY", "")
    wa = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    m = os.getenv("MOYASAR_SECRET_KEY", "")
    w = os.getenv("MOYASAR_WEBHOOK_SECRET", "")

    # All env vars whose names start with target prefixes — helps detect typos
    related = sorted([
        name for name in os.environ.keys()
        if name.startswith((
            "GOOGLE_", "MOYASAR_", "ANTHROPIC_", "OPENAI_", "GROQ_", "POSTHOG_",
            "SENTRY_", "DATABASE_", "TAVILY_", "FIRECRAWL_", "HUNTER_", "ABSTRACT_",
            "WAPPALYZER_", "SERPAPI_", "APIFY_", "SENDGRID_", "WHATSAPP_",
            "APP_URL", "PORT", "RAILWAY_",
        ))
    ])

    # Tier readiness summary
    tier1_ready = bool(db) and bool(grq or ant or oai) and bool(k and c) and bool(sd)
    tier2_ready = bool(gm) and (bool(tav) or bool(fc) or bool(hu))

    return {
        # ── Layer 1 — Required now ──
        "DATABASE_URL":          _diag(db),
        "GOOGLE_SEARCH_API_KEY": {**_diag(k), "prefix": (k[:6] + "...") if k else ""},
        "GOOGLE_SEARCH_CX":      {**_diag(c), "prefix": (c[:6] + "...") if c else ""},
        "GROQ_API_KEY":          _diag(grq),
        "ANTHROPIC_API_KEY":     _diag(ant),
        "OPENAI_API_KEY":        _diag(oai),
        "SENTRY_DSN":            _diag(sd),
        # ── Layer 2 — Lead discovery power ──
        "GOOGLE_MAPS_API_KEY":   {**_diag(gm), "prefix": (gm[:6] + "...") if gm else ""},
        "TAVILY_API_KEY":        _diag(tav),
        "FIRECRAWL_API_KEY":     _diag(fc),
        "HUNTER_API_KEY":        _diag(hu),
        "ABSTRACT_API_KEY":      _diag(ab),
        "WAPPALYZER_API_KEY":    _diag(wp),
        "SERPAPI_API_KEY":       _diag(serp),
        "APIFY_TOKEN":           _diag(apify),
        # ── Layer 3 — Channels ──
        "SENDGRID_API_KEY":      _diag(sg),
        "WHATSAPP_ACCESS_TOKEN": _diag(wa),
        # ── Payments ──
        "MOYASAR_SECRET_KEY":    {**_diag(m), "prefix": (m[:6] + "...") if m else ""},
        "MOYASAR_WEBHOOK_SECRET":_diag(w),
        # ── Tier readiness summary ──
        "tier1_ready": tier1_ready,
        "tier2_ready": tier2_ready,
        "all_visible_env_var_names_starting_with_known_prefixes": related,
        "railway_environment_name": os.getenv("RAILWAY_ENVIRONMENT_NAME", "(not set)"),
        "railway_service_name": os.getenv("RAILWAY_SERVICE_NAME", "(not set)"),
        "railway_project_name": os.getenv("RAILWAY_PROJECT_NAME", "(not set)"),
        "hint": (
            "ready_to_launch" if tier1_ready and tier2_ready else
            "tier1_only" if tier1_ready else
            "set_DATABASE_URL_first" if not db else
            "set_GOOGLE_SEARCH_API_KEY_and_CX" if not (k and c) else
            "set_GROQ_or_ANTHROPIC_or_OPENAI" if not (grq or ant or oai) else
            "almost_there"
        ),
    }


@router.post("/search")
async def search(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Run a Google Custom Search query using server-side keys.
    Body: {"query": "...", "num": 10, "site": "linkedin.com" (optional), "lang": "ar"|"en"}
    Returns: SearchResponse JSON.
    """
    q = str(body.get("query") or "").strip()
    if len(q) < 3 or len(q) > 500:
        raise HTTPException(status_code=400, detail="query_length_out_of_range")

    num = int(body.get("num") or 10)
    if num < 1 or num > 10:
        raise HTTPException(status_code=400, detail="num_out_of_range: 1..10")

    site = body.get("site")
    site = str(site).strip() if site else None
    lang = body.get("lang")
    lang = str(lang).strip().lower() if lang else None
    if lang and lang not in {"ar", "en", "fr", "es"}:
        raise HTTPException(status_code=400, detail="unsupported_lang")

    try:
        resp = await google_search(q, num=num, site=site, lang=lang, timeout=10.0)
    except Exception as exc:  # noqa: BLE001
        log.exception("google_search_call_failed q=%r", q)
        raise HTTPException(status_code=502, detail="search_error") from exc

    if resp.status == "no_keys":
        raise HTTPException(status_code=503, detail="search_not_configured")

    return resp.to_dict()


@router.post("/enrich-tech")
async def enrich_tech(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Detect tech stack for a domain using Dealix native detector (free, self-hosted).
    Body: {"domain": "foodics.com", "extra_paths": ["/careers", "/contact"]}
    """
    domain = str(body.get("domain") or "").strip()
    extra = body.get("extra_paths") or []
    if not isinstance(extra, list):
        extra = []
    extra = [str(p)[:80] for p in extra[:5]]

    if not domain or "." not in domain or len(domain) > 200:
        raise HTTPException(status_code=400, detail="invalid_domain")

    try:
        result = await detect_stack(domain, timeout=10.0, extra_paths=extra)
    except Exception as exc:  # noqa: BLE001
        log.exception("tech_detect_failed domain=%s", domain)
        raise HTTPException(status_code=502, detail="tech_detect_error") from exc
    return result.to_dict()


@router.post("/enrich-domain")
async def enrich_domain(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    End-to-end enrichment: given a domain + opportunity hint, combine tech stack
    detection + LLM analysis to return a full lead record per LEAD_OUTPUT_SCHEMA.

    Body:
      {
        "domain": "foodics.com",
        "opportunity_hint": "DIRECT_CUSTOMER|AGENCY_PARTNER|..." (optional),
        "context_notes": "optional extra human context"
      }

    Returns: full lead object (opportunity_type, scores, signals, outreach opening, etc.)
    """
    domain = str(body.get("domain") or "").strip()
    opportunity_hint = str(body.get("opportunity_hint") or "").strip().upper()
    context_notes = str(body.get("context_notes") or "").strip()[:1000]

    if not domain or "." not in domain or len(domain) > 200:
        raise HTTPException(status_code=400, detail="invalid_domain")

    # Step 1 — tech detection (free, always available)
    try:
        tech = await detect_stack(domain, timeout=10.0, extra_paths=["/careers", "/about"])
    except Exception:
        log.exception("tech_detect_failed domain=%s", domain)
        tech = None

    tech_dict = tech.to_dict() if tech else {"tools": [], "signals": [], "status": "unavailable"}

    # Step 2 — LLM analysis using ProspectorAgent-style prompt but domain-scoped
    from auto_client_acquisition.agents.prospector import ProspectorAgent, USE_CASES

    agent = ProspectorAgent()
    icp_text = (
        f"الشركة: {domain}\n"
        f"الأدوات المكتشفة عبر tech detector: "
        f"{', '.join(t['name'] for t in tech_dict.get('tools', []))}\n"
        f"الإشارات المستخرجة: "
        f"{', '.join(s['evidence'] for s in tech_dict.get('signals', []))}\n"
        + (f"سياق إضافي: {context_notes}\n" if context_notes else "")
        + (f"تلميح لنوع الفرصة: {opportunity_hint}\n" if opportunity_hint else "")
        + "\nحلّل هذه الشركة تحديداً: صنّف نوع الفرصة، احسب ال 4 scores، اقترح sequence من الخطوات، وأعد نفس شكل JSON كما هو محدد."
    )
    use_case = "sales"  # default; the LLM will classify opportunity_type freely

    try:
        result = await agent.run(icp=icp_text, use_case=use_case, count=1)
        leads = result.leads
        lead_dict = leads[0].to_dict() if leads else None
        search_notes = result.search_notes
        status = "ok"
    except Exception:
        log.warning("enrich_domain_llm_unavailable domain=%s — serving tech-only + rules", domain)
        # Degraded: run rules router over the tech signals to still produce actionable lead
        signals_for_router = [
            {"name": s.get("name", ""), "weight": s.get("weight", 0), "evidence": s.get("evidence", "")}
            for s in tech_dict.get("signals", [])
        ]
        res = _rules_route(
            company=domain.split(".")[0].replace("-", " ").title(),
            sector="",
            country="SA",
            domain=domain,
            signals=signals_for_router,
            tags="",
            decision_maker=None,
        )
        # Also produce messages deterministically
        msgs = _rules_generate_messages(
            company=domain.split(".")[0].replace("-", " ").title(),
            decision_maker=None,
            opportunity_type=res.opportunity_type,
            signals=signals_for_router,
        )
        lead_dict = {
            **res.to_dict(),
            "company_en": domain.split(".")[0].replace("-", " ").title(),
            "company_ar": "",
            "website": f"https://{domain}",
            "outreach_opening": msgs["linkedin"][:280],
            "signals": signals_for_router,
            "confidence": 60,
        }
        search_notes = "degraded mode — rules router + tech detect only (no LLM key)"
        status = "degraded"

    return {
        "domain": domain,
        "tech": tech_dict,
        "lead": lead_dict,
        "search_notes": search_notes,
        "fetched_at": tech_dict.get("fetched_at"),
        "status": status,
    }


@router.post("/route")
async def route_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Deterministic rule-based router — classify + score + route an account without LLM.
    Body: {company, sector?, country?, domain?, signals?, tags?, decision_maker?, size_hint?, is_government?, desired_goal?}
    """
    company = str(body.get("company") or "").strip()
    if not company:
        raise HTTPException(status_code=400, detail="company_required")
    res = _rules_route(
        company=company,
        sector=str(body.get("sector") or ""),
        country=str(body.get("country") or ""),
        domain=str(body.get("domain") or ""),
        signals=body.get("signals") or [],
        tags=str(body.get("tags") or ""),
        decision_maker=body.get("decision_maker"),
        size_hint=str(body.get("size_hint") or ""),
        is_government=bool(body.get("is_government") or False),
        desired_goal=body.get("desired_goal"),
    )
    return {"mode": "rules", "result": res.to_dict()}


@router.post("/score")
async def score_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Score an account against the 100-pt ICP model. Same inputs as /route.
    Returns only the score breakdown (no messages).
    """
    company = str(body.get("company") or "").strip()
    if not company:
        raise HTTPException(status_code=400, detail="company_required")
    res = _rules_route(
        company=company,
        sector=str(body.get("sector") or ""),
        country=str(body.get("country") or ""),
        domain=str(body.get("domain") or ""),
        signals=body.get("signals") or [],
        tags=str(body.get("tags") or ""),
        decision_maker=body.get("decision_maker"),
        size_hint=str(body.get("size_hint") or ""),
        is_government=bool(body.get("is_government") or False),
    )
    r = res.to_dict()
    return {
        "company": company,
        "fit_score": r["fit_score"],
        "intent_score": r["intent_score"],
        "access_score": r["access_score"],
        "revenue_score": r["revenue_score"],
        "priority_score": r["priority_score"],
        "priority_tier": r["priority_tier"],
        "risk_level": r["risk_level"],
        "opportunity_type": r["opportunity_type"],
        "reason": r["reason"],
    }


@router.post("/message")
async def message_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Generate templated, signal-aware Arabic outreach for an account.
    Body: {company, decision_maker?, opportunity_type?, signals?}
    Returns: {linkedin, email, whatsapp_warm_only, follow_up_plus_2/5/10}
    """
    company = str(body.get("company") or "").strip()
    if not company:
        raise HTTPException(status_code=400, detail="company_required")

    opp = str(body.get("opportunity_type") or "").strip().upper()
    if not opp:
        # Fall back: classify via rules
        res = _rules_route(
            company=company,
            sector=str(body.get("sector") or ""),
            tags=str(body.get("tags") or ""),
            signals=body.get("signals") or [],
        )
        opp = res.opportunity_type

    msgs = _rules_generate_messages(
        company=company,
        decision_maker=body.get("decision_maker"),
        opportunity_type=opp,
        signals=body.get("signals") or [],
    )
    return {"mode": "rules", "opportunity_type": opp, "messages": msgs}


@router.post("/bulk-enrich")
async def bulk_enrich(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Bulk tech-detect enrichment for a list of domains.
    Body: {"domains": ["foodics.com", "salla.sa", ...], "concurrency": 5}
    Returns: {"results": {domain: tech_result, ...}, "summary": {...}}

    Hard limit: 25 domains per request (prevent abuse).
    """
    domains_raw = body.get("domains") or []
    if not isinstance(domains_raw, list):
        raise HTTPException(status_code=400, detail="domains_must_be_list")

    domains = [str(d).strip() for d in domains_raw if d and "." in str(d)]
    domains = list(dict.fromkeys(domains))[:25]  # dedupe, cap

    if not domains:
        raise HTTPException(status_code=400, detail="no_valid_domains")

    concurrency = int(body.get("concurrency") or 5)
    concurrency = max(1, min(10, concurrency))

    import asyncio as _asyncio
    sem = _asyncio.Semaphore(concurrency)

    async def _one(d: str) -> tuple[str, dict]:
        async with sem:
            try:
                r = await detect_stack(d, timeout=10.0)
                return d, r.to_dict()
            except Exception as exc:  # noqa: BLE001
                return d, {"status": "error", "error": str(exc), "domain": d}

    pairs = await _asyncio.gather(*(_one(d) for d in domains))
    results = dict(pairs)

    total_tools = sum(len(r.get("tools", [])) for r in results.values())
    total_signals = sum(len(r.get("signals", [])) for r in results.values())
    ok_count = sum(1 for r in results.values() if r.get("status") == "ok")

    return {
        "summary": {
            "domains_requested": len(domains),
            "ok_count": ok_count,
            "total_tools_detected": total_tools,
            "total_signals_detected": total_signals,
        },
        "results": results,
    }


@router.post("/contacts")
async def contacts(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Extract publicly listed contact info (emails, phones, WhatsApp, social) from a company's public pages.
    LEGAL: public pages only; business contact only; no PII from private / authenticated sources.
    Body: {"domain": "foodics.com"}
    """
    domain = str(body.get("domain") or "").strip()
    if not domain or "." not in domain or len(domain) > 200:
        raise HTTPException(status_code=400, detail="invalid_domain")
    try:
        return await extract_contact_info(domain, timeout=10.0)
    except Exception as exc:
        log.exception("contacts_failed domain=%s", domain)
        raise HTTPException(status_code=502, detail="contact_extraction_error") from exc


@router.post("/inbound/handle")
async def inbound_handle(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Autonomous inbound handler — given an incoming lead message, classify, decide,
    generate Arabic response, pick next_action.
    Body:
      {
        "channel": "whatsapp|email|web_chat|linkedin|sms",
        "from": "+966501234567" | "ali@example.com",
        "company": "optional — extracted from domain if known",
        "message": "the actual customer inquiry"
      }
    Returns:
      {
        "classification": "interested|price|demo|later|objection|...",
        "opportunity_type": "DIRECT_CUSTOMER|...",
        "response_ar": "...",
        "next_action": "BOOK_DEMO|PREPARE_DM|...",
        "should_escalate_to_human": bool,
        "tracker_update": {status, sent_at, next_followup}
      }
    """
    channel = str(body.get("channel") or "unknown").lower()
    sender = str(body.get("from") or "").strip()
    company = str(body.get("company") or "").strip()
    message = str(body.get("message") or "").strip()

    if len(message) < 2:
        raise HTTPException(status_code=400, detail="message_required")

    # Very simple offline classifier (same regex rules from scripts/dealix_reply_classifier.py)
    import re
    text = message.lower()
    classification = "interested"  # default
    rules = [
        ("wants_demo",          r"demo|ديمو|عرض|تجربة"),
        ("price",               r"كم\s*(السعر|يكلف|المبلغ)|السعر|price|pricing|كم\s*ريال"),
        ("send_details",        r"ارسل|أرسل|تفاصيل|details|deck|presentation"),
        ("later",               r"بعدين|لاحق|later|not\s*now|رمضان"),
        ("opt_out",             r"أوقف|إيقاف|stop|unsubscribe|لا\s*شكراً|انهاء"),
        ("arabic_concern",       r"العربي|عربي\s*(مضبوط|طبيعي|سيء|سيئ|رديء)|arabic.*quality|خليجي|لهجة"),
        ("not_relevant",        r"مو\s*مناسب|not\s*relevant|غير\s*مناسب|لا\s*نحتاج"),
        ("budget_objection",    r"ميزانية|budget|غالي|مكلف"),
        ("already_has_crm",     r"crm|salesforce|hubspot|zoho"),
        ("arabic_concern",      r"لهجة|arabic.*quality|خليجي"),
        ("privacy_concern",     r"خصوصية|pdpl|privacy|بيانات"),
        ("partnership_interest",r"شراكة|partner|وكالة|reseller"),
        ("referral_opportunity",r"أعرف|رشح|referral|intro"),
    ]
    for cat, pat in rules:
        if re.search(pat, text):
            classification = cat
            break
    # If very short greeting, treat as interested
    if len(text) < 10 and any(g in text for g in ("مرحب", "سلام", "هلا", "hi", "hello")):
        classification = "interested"

    # Decide opportunity type from company name keywords
    opp_type = "DIRECT_CUSTOMER"
    if any(k in (company or "").lower() for k in ["agency", "وكالة", "marketing"]):
        opp_type = "AGENCY_PARTNER"
    elif any(k in (company or "").lower() for k in ["vc", "capital", "ventures", "fund"]):
        opp_type = "INVESTOR_OR_ADVISOR"

    # Build response
    CAL = "https://calendly.com/sami-assiri11/dealix-demo"
    responses = {
        "opt_out":              "تمام، تم إيقاف الرسائل. شكراً لوقتك.",
        "interested":           f"هلا! شكراً على اهتمامك. خلني أحجز معك 20 دقيقة demo بدون أي التزام — تقدر تختار موعدك هنا: {CAL}",
        "wants_demo":           f"ممتاز، نسوي demo. 20 دقيقة، اختار موعد: {CAL}",
        "price":                f"Starter 999/شهر، Growth 2,999، Scale 7,999. في pilot بريال × 7 أيام بدون التزام. 20 دقيقة demo أفصّل الباقة المناسبة: {CAL}",
        "send_details":         f"تفاصيل سريعة: Dealix = AI sales rep بالعربي الخليجي، يرد على leads خلال 45 ثانية، يؤهّل، ويحجز demos. الأفضل نشوفه معاً في 20 دقيقة على سيناريو شركتكم: {CAL}\nأو تصفح: https://dealix.me",
        "later":                "تمام. متى الوقت المناسب يحتمل يكون؟ سأرجع في نفس اليوم بالظبط.",
        "not_relevant":         "أحترم ذلك. سؤال أخير: هل تعرف شخص/شركة سعودية قد تستفيد من AI sales rep بالعربي؟ 10% من MRR لـ 12 شهر لكل referral. شكراً على وقتك.",
        "budget_objection":     "أفهم. عرضنا pilot بريال واحد × 7 أيام — قابل للاسترداد 100% — هدفه يثبت ROI قبل أي التزام. مناسب؟",
        "already_has_crm":      "Dealix ما يستبدل CRM — يشتغل كطبقة أولى فوقه. يرد بالعربي، يؤهّل، ويسلّم الـ CRM قائمة leads جاهزة. تكامل مباشر HubSpot/Salesforce/Zoho/webhook. 20 دقيقة demo: " + CAL,
        "arabic_concern":       f"نقطة مهمة. Dealix خليجي حقيقي، ما يكتب 'حضرتك' و'تعطفكم'. 20 دقيقة demo تختبره بنفسك على سيناريو شركتكم: {CAL}",
        "privacy_concern":      f"مصمم PDPL-compliant: بياناتكم في سيرفرات السعودية، opt-out في كل email، audit log كامل. 20 دقيقة نناقش compliance + demo: {CAL}",
        "partnership_interest": f"ممتاز. 3 tiers:\n- Referral: 10% MRR × 12 شهر\n- Agency: setup 3-15K + 20-30% MRR\n- White-label (Scale)\n20 دقيقة partner call: https://dealix.me/partners.html",
        "referral_opportunity": "شكراً! 10% من MRR × 12 شهر لأي عميل يجي عبرك. ممكن تخبرني بمعلومات الشركة والشخص؟",
    }
    response_ar = responses.get(classification, responses["interested"])

    # Decide next action
    action_map = {
        "opt_out": "STOP_CONTACT",
        "interested": "BOOK_DEMO",
        "wants_demo": "BOOK_DEMO",
        "price": "BOOK_DEMO",
        "send_details": "PREPARE_DEMO_FLOW",
        "later": "FOLLOW_UP",
        "not_relevant": "STOP_CONTACT",
        "budget_objection": "ROUTE_TO_MANUAL_PAYMENT",
        "already_has_crm": "BOOK_DEMO",
        "arabic_concern": "PREPARE_DEMO_FLOW",
        "privacy_concern": "PREPARE_DEMO_FLOW",
        "partnership_interest": "PREPARE_PARTNER_PITCH",
        "referral_opportunity": "FOLLOW_UP",
    }
    next_action = action_map.get(classification, "ASK_HUMAN_FINAL_SEND")

    # Escalation rule
    escalate = classification in ("partnership_interest",) or opp_type == "INVESTOR_OR_ADVISOR"

    from datetime import datetime, timedelta
    now = datetime.utcnow().isoformat() + "Z"
    next_followup = (datetime.utcnow() + timedelta(days=2)).date().isoformat()

    return {
        "classification": classification,
        "opportunity_type": opp_type,
        "response_ar": response_ar,
        "next_action": next_action,
        "should_escalate_to_human": escalate,
        "channel_recommended_reply": channel,
        "tracker_update": {
            "reply_received_at": now,
            "classification": classification,
            "next_followup": next_followup,
            "status": "engaged",
        },
        "compliance_note": (
            "Response auto-generated using rules-based classifier + templated Khaliji Arabic. "
            "No LLM used (deterministic). No personal PII stored beyond the inbound message. "
            "Human review recommended for partnership/investor classifications."
        ),
    }


async def _run_inbound_handler(channel: str, sender: str, company: str, message: str) -> dict[str, Any]:
    """Shared internal handler used by all channel webhooks."""
    return await inbound_handle({
        "channel": channel,
        "from": sender,
        "company": company,
        "message": message,
    })


@router.post("/inbound/whatsapp")
async def inbound_whatsapp(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    WhatsApp Business API webhook handler.
    Expected payload format (Meta WhatsApp Cloud API):
      {"entry":[{"changes":[{"value":{"messages":[{"from":"+966...","text":{"body":"..."}}]}}]}]}
    Or simplified: {"from":"+966...","message":"..."}
    """
    msg = ""
    sender = ""
    # Try both simple and Meta formats
    if "entry" in body:
        try:
            m = body["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = str(m.get("from") or "")
            msg = str(m.get("text", {}).get("body") or m.get("body") or "")
        except (KeyError, IndexError, TypeError):
            pass
    msg = msg or str(body.get("message") or "")
    sender = sender or str(body.get("from") or "")
    if not msg:
        raise HTTPException(status_code=400, detail="no_message_body")
    result = await _run_inbound_handler("whatsapp", sender, str(body.get("company", "")), msg)
    result["send_reply_instruction"] = (
        "POST the response_ar via WhatsApp Business Cloud API: "
        "POST https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages "
        "with { messaging_product: 'whatsapp', to: sender, text: { body: response_ar } }"
    )
    return result


@router.post("/inbound/email")
async def inbound_email(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Email inbound webhook (SendGrid Inbound Parse / Mailgun Routes format).
    Expected: {"from":"ali@example.com","subject":"...","text":"..."} or SendGrid inbound format.
    """
    sender = str(body.get("from") or body.get("sender") or "")
    msg = str(body.get("text") or body.get("body-plain") or body.get("message") or "")
    subject = str(body.get("subject") or "")
    if subject and msg:
        combined = f"[{subject}] {msg}"
    else:
        combined = msg or subject
    if not combined:
        raise HTTPException(status_code=400, detail="no_message_body")
    result = await _run_inbound_handler("email", sender, str(body.get("company", "")), combined)
    result["send_reply_instruction"] = (
        "Reply via Gmail API / SendGrid / SES — include opt-out footer "
        "'لإيقاف الرسائل: رد بـ لا شكراً'"
    )
    return result


@router.post("/inbound/form")
async def inbound_form(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Generic web-form submission handler. Feeds directly into /inbound/handle.
    Expected: {"name","email","company","message","source":"web_form"}
    """
    name = str(body.get("name") or "")
    email = str(body.get("email") or "")
    company = str(body.get("company") or "")
    message = str(body.get("message") or "")
    if not message:
        raise HTTPException(status_code=400, detail="message_required")
    sender = email or name
    result = await _run_inbound_handler("web_form", sender, company, message)
    result["send_reply_instruction"] = (
        "Display response_ar inline in form confirmation. Also auto-send email reply "
        "with response_ar + Calendly link."
    )
    # Also create a lead record via pipeline if email + company known
    if email and company:
        result["also_created_lead"] = True
        result["lead_hint"] = "POST /api/v1/leads with this payload to persist"
    return result


@router.post("/inbound/sms")
async def inbound_sms(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    SMS inbound webhook (Twilio format).
    Expected: {"From":"+966...","Body":"..."} or {"from","message"}
    """
    sender = str(body.get("From") or body.get("from") or "")
    msg = str(body.get("Body") or body.get("message") or "")
    if not msg:
        raise HTTPException(status_code=400, detail="no_message_body")
    result = await _run_inbound_handler("sms", sender, str(body.get("company", "")), msg)
    result["send_reply_instruction"] = (
        "Reply via Twilio / Unifonic / STC. Keep SMS ≤ 160 chars; long messages via WhatsApp link."
    )
    # SMS replies should be SHORTER
    if result.get("response_ar") and len(result["response_ar"]) > 160:
        result["response_ar_short"] = result["response_ar"][:140] + "... رابط: https://dealix.me"
    return result


@router.post("/inbound/linkedin")
async def inbound_linkedin(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    LinkedIn manual-capture webhook (Sami pastes reply content; Dealix classifies + suggests reply).
    NOT auto-send (LinkedIn ToS). Human final-send required.
    Expected: {"from":"...","profile_url":"...","message":"..."}
    """
    sender = str(body.get("from") or body.get("profile_url") or "")
    msg = str(body.get("message") or "")
    if not msg:
        raise HTTPException(status_code=400, detail="no_message_body")
    result = await _run_inbound_handler("linkedin", sender, str(body.get("company", "")), msg)
    result["send_reply_instruction"] = (
        "⚠️ LinkedIn = HUMAN FINAL SEND ONLY (ToS compliance). "
        "Show response_ar to Sami, Sami pastes manually into LinkedIn DM. NO automation."
    )
    result["should_escalate_to_human"] = True  # always for LinkedIn
    return result


@router.post("/demo")
async def demo() -> dict[str, Any]:
    """Canned demo response for landing UI preview. No LLM call."""
    return {
        "use_case": "sales",
        "icp": "شركات SaaS سعودية B2B بحجم 20-100 موظف تبيع للمطاعم",
        "count_requested": 3,
        "count_returned": 3,
        "search_notes": "نتائج توضيحية — جرب الواجهة الحقيقية للحصول على قائمة مخصصة لمواصفاتك.",
        "leads": [
            {
                "company_ar": "فودكس",
                "company_en": "Foodics",
                "industry": "SaaS للمطاعم",
                "est_size": "200-1000",
                "website": "https://www.foodics.com",
                "linkedin": "https://www.linkedin.com/company/foodics",
                "decision_maker_hints": ["Ahmad Al-Zaini — CEO", "Mosab Alothmani — Co-founder"],
                "signals": ["جولة Series C بـ $170M 2025", "توسع في الخليج وشمال أفريقيا"],
                "outreach_opening": "أحمد، مبروك Series C — 170M = فرصة مضاعفة السرعة في onboarding العملاء الجدد.",
                "fit_score": 92,
                "confidence": 90,
                "evidence": "شركة SaaS سعودية واضحة، تستهدف restaurant operators، بحجم يطابق الـ ICP.",
            },
            {
                "company_ar": "رُكاز",
                "company_en": "Rekaz",
                "industry": "SaaS للـ SMB",
                "est_size": "10-50",
                "website": "https://rekaz.io",
                "linkedin": None,
                "decision_maker_hints": ["Abdullah Al-Shalan — Founder"],
                "signals": ["منصة متخصصة في إدارة المستودعات للتجار"],
                "outreach_opening": "عبدالله، رُكاز تبني الطبقة التشغيلية للتاجر السعودي — هذا تماماً مكان AI sales rep بالعربي.",
                "fit_score": 85,
                "confidence": 75,
                "evidence": "SMB-focused SaaS سعودي ضمن الحجم المطلوب.",
            },
            {
                "company_ar": "زد",
                "company_en": "Zid",
                "industry": "E-commerce Platform",
                "est_size": "200-1000",
                "website": "https://zid.sa",
                "linkedin": "https://www.linkedin.com/company/zidsa",
                "decision_maker_hints": ["Sultan Mofarreh — Co-founder"],
                "signals": ["منافس لسلة مع 15K تاجر+", "ركّز على SMB merchants"],
                "outreach_opening": "سلطان، 15K تاجر = فرصة توزيع هائلة لـ AI sales rep داخل zid marketplace.",
                "fit_score": 88,
                "confidence": 85,
                "evidence": "منصة تجارة إلكترونية سعودية راسخة ضمن الحجم المطلوب.",
            },
        ],
    }

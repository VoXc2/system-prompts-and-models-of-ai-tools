"""
Lead Intelligence Pipeline — End-to-end orchestrator
ICP → Discovery → Enrichment → Entity Resolution → Scoring → Outreach Brief
One call drives the full flow.
"""
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from app.intelligence.icp import ICPConfig, DEALIX_DEFAULT_ICP
from app.intelligence.discovery import LeadDiscoveryEngine
from app.intelligence.enrichment import enrich_batch
from app.intelligence.scoring import score_batch
from app.intelligence.entity_resolution import EntityRegistry
from app.intelligence.outreach import generate_batch_briefs


def run_pipeline(
    icp: Optional[ICPConfig] = None,
    custom_queries: Optional[List[str]] = None,
    motion: str = "sales",
    max_leads: int = 30,
    enrich: bool = True,
    generate_outreach: bool = True,
    score_weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Full lead intelligence pipeline.

    Returns:
        {
            "run_id": str,
            "icp_used": dict,
            "total_discovered": int,
            "total_after_dedup": int,
            "total_enriched": int,
            "scored_leads": [...],    # all leads sorted by score
            "p1_leads": [...],        # outreach now
            "p2_leads": [...],        # enrich more
            "p3_leads": [...],        # nurture
            "outreach_briefs": [...], # generated briefs for P1+P2
            "tier_summary": {...},
            "pipeline_duration_sec": float,
            "errors": [...],
        }
    """
    start_time = time.time()
    run_id = f"pipeline_{int(start_time)}"
    errors = []

    # 1. Resolve ICP
    icp = icp or DEALIX_DEFAULT_ICP

    # 2. Discovery
    engine = LeadDiscoveryEngine(icp=icp)
    if custom_queries:
        candidates = engine.discover(custom_queries, max_per_query=6)
    else:
        candidates = engine.discover_from_icp(icp=icp, max_per_query=5)

    total_discovered = len(candidates)

    # 3. Entity Resolution + Dedup
    registry = EntityRegistry()
    raw_lead_dicts = [
        {
            "id": c.id,
            "company_name": c.company_name,
            "domain": c.domain,
            "source": c.source,
            "source_url": c.source_url,
            "raw_snippet": c.raw_snippet,
            "signals": c.signals,
            "trigger": c.trigger,
            "contact_email": c.contact_email,
            "contact_phone": c.phone,
            "contact_linkedin": c.contact_linkedin,
            "confidence": c.confidence,
            "_candidate": c,
        }
        for c in candidates
    ]
    deduped_dicts = registry.deduplicate_lead_list(raw_lead_dicts)
    deduped_candidates = [d["_candidate"] for d in deduped_dicts[:max_leads]]

    total_after_dedup = len(deduped_candidates)

    # 4. Enrichment
    enriched_leads = []
    if enrich:
        enriched_leads = enrich_batch(deduped_candidates, delay=0.2)
    else:
        # Skip enrichment — use candidates as-is
        from app.intelligence.enrichment import EnrichedLead
        for c in deduped_candidates:
            e = EnrichedLead(
                id=c.id,
                company_name=c.company_name,
                domain=c.domain,
                industry=c.industry,
                region=c.region,
                website=f"https://{c.domain}" if c.domain else "",
                signals=c.signals,
                source=c.source,
                source_url=c.source_url,
                raw_snippet=c.raw_snippet,
                trigger=c.trigger,
                contact_email=c.contact_email,
                contact_phone=c.phone,
                enrichment_confidence=c.confidence,
            )
            enriched_leads.append(e)

    total_enriched = len(enriched_leads)

    # 5. Scoring
    scored = score_batch(enriched_leads, weights=score_weights)

    # 6. Tier breakdown
    tier_counts = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    p1, p2, p3, p4 = [], [], [], []
    for item in scored:
        tier = item["score"]["tier"]
        tier_counts[tier] += 1
        if tier == "P1": p1.append(item)
        elif tier == "P2": p2.append(item)
        elif tier == "P3": p3.append(item)
        else: p4.append(item)

    # 7. Outreach briefs
    outreach_briefs = []
    if generate_outreach:
        outreach_briefs = generate_batch_briefs(scored, motion=motion)

    duration = round(time.time() - start_time, 2)

    return {
        "run_id": run_id,
        "icp_used": icp.to_dict() if hasattr(icp, 'to_dict') else {},
        "total_discovered": total_discovered,
        "total_after_dedup": total_after_dedup,
        "total_enriched": total_enriched,
        "scored_leads": scored,
        "p1_leads": p1,
        "p2_leads": p2,
        "p3_leads": p3,
        "p4_leads": p4,
        "outreach_briefs": outreach_briefs,
        "tier_summary": {
            "P1_outreach_now": tier_counts["P1"],
            "P2_enrich_more": tier_counts["P2"],
            "P3_nurture": tier_counts["P3"],
            "P4_archive": tier_counts["P4"],
        },
        "pipeline_duration_sec": duration,
        "errors": errors,
    }

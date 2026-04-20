"""
Revenue Intelligence OS — Lead Machine API
Endpoints for ICP, Discovery, Enrichment, Scoring, Outreach, Triggers
"""
import uuid
import json
import time
from flask import Blueprint, request, jsonify

from app.core.database import db
from app.api.routes.auth import require_auth
from app.core.audit import log as audit_log
from app.intelligence.icp import ICPConfig, DEALIX_DEFAULT_ICP
from app.intelligence.pipeline import run_pipeline
from app.intelligence.triggers import scan_watchlist, scan_company_for_triggers
from app.intelligence.outreach import generate_outreach_brief
from app.intelligence.scoring import score_lead
from app.intelligence.enrichment import enrich_candidate, EnrichedLead

intelligence_bp = Blueprint("intelligence", __name__, url_prefix="/api/intelligence")


def _json(data, status=200):
    return jsonify(data), status


# ─── ICP MANAGEMENT ─────────────────────────────────────────────────────────

@intelligence_bp.get("/icp")
@require_auth
def get_icp(user):
    """Get active ICP config for org"""
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM icp_configs WHERE org_id=? AND is_active=1 ORDER BY created_at DESC LIMIT 1",
            (user["org_id"],)
        ).fetchone()
    if row:
        config = json.loads(row["config"])
        return _json({"icp": config, "id": row["id"], "name": row["name"]})
    # Return default ICP
    return _json({"icp": DEALIX_DEFAULT_ICP.to_dict(), "id": "default", "name": "Dealix Default ICP"})


@intelligence_bp.post("/icp")
@require_auth
def create_icp(user):
    if user["role"] not in ("manager", "admin"):
        return _json({"error": "Forbidden"}, 403)
    """Create or update ICP config"""
    data = request.get_json() or {}
    icp_id = str(uuid.uuid4())

    # Deactivate existing
    with db() as conn:
        conn.execute("UPDATE icp_configs SET is_active=0 WHERE org_id=?", (user["org_id"],))
        conn.execute("""
            INSERT INTO icp_configs (id, org_id, name, config, is_active, created_by)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (icp_id, user["org_id"], data.get("name", "Custom ICP"), json.dumps(data), user["id"]))

    audit_log(user["org_id"], "intelligence", "icp_created", user["id"], icp_id, data)
    return _json({"id": icp_id, "message": "ICP saved"}, 201)


# ─── PIPELINE ────────────────────────────────────────────────────────────────

@intelligence_bp.post("/pipeline/run")
@require_auth
def run_lead_pipeline(user):
    if user["role"] not in ("manager", "admin"):
        return _json({"error": "Forbidden"}, 403)
    """
    Trigger full lead intelligence pipeline.
    Body (all optional):
      custom_queries: list[str]
      motion: sales | partnership | channel | tender
      max_leads: int (default 30)
      enrich: bool (default true)
      generate_outreach: bool (default true)
    """
    data = request.get_json() or {}
    motion = data.get("motion", "sales")
    max_leads = min(int(data.get("max_leads", 30)), 100)
    enrich = data.get("enrich", True)
    gen_outreach = data.get("generate_outreach", True)
    custom_queries = data.get("custom_queries", None)

    run_id = f"run-{uuid.uuid4().hex[:12]}"

    # Load ICP from DB if available
    with db() as conn:
        icp_row = conn.execute(
            "SELECT config FROM icp_configs WHERE org_id=? AND is_active=1 LIMIT 1",
            (user["org_id"],)
        ).fetchone()

    icp = None
    if icp_row:
        try:
            cfg = json.loads(icp_row["config"])
            icp = ICPConfig(**{k: v for k, v in cfg.items() if k in ICPConfig.__dataclass_fields__})
        except Exception:
            icp = DEALIX_DEFAULT_ICP
    else:
        icp = DEALIX_DEFAULT_ICP

    # Record run start
    with db() as conn:
        conn.execute("""
            INSERT INTO intelligence_runs (id, org_id, run_mode, motion, status, created_by)
            VALUES (?, ?, 'manual', ?, 'running', ?)
        """, (run_id, user["org_id"], motion, user["id"]))

    try:
        result = run_pipeline(
            icp=icp,
            custom_queries=custom_queries,
            motion=motion,
            max_leads=max_leads,
            enrich=enrich,
            generate_outreach=gen_outreach,
        )
        result["run_id"] = run_id

        # Persist scored leads to DB
        with db() as conn:
            for item in result.get("scored_leads", []):
                lead = item["lead"]
                score = item["score"]
                lid = lead.get("id", str(uuid.uuid4()))
                conn.execute("""
                    INSERT OR REPLACE INTO intelligence_leads (
                        id, org_id, company_name, domain, industry, region, company_size,
                        description, website, tech_stack, signals, recent_news,
                        contact_name, contact_title, contact_email, contact_phone, contact_linkedin,
                        decision_maker_score, enrichment_source, enrichment_confidence,
                        source, source_url, raw_snippet, trigger,
                        score_fit, score_intent, score_access, score_value, score_urgency,
                        score_master, priority_tier, score_reasons, next_action, next_action_ar,
                        pipeline_run_id, enriched_at
                    ) VALUES (
                        ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
                    )
                """, (
                    lid, user["org_id"],
                    lead.get("company_name", ""), lead.get("domain", ""),
                    lead.get("industry", ""), lead.get("region", ""),
                    lead.get("company_size", "unknown"),
                    lead.get("description", ""), lead.get("website", ""),
                    json.dumps(lead.get("tech_stack", [])),
                    json.dumps(lead.get("signals", [])),
                    json.dumps(lead.get("recent_news", [])),
                    lead.get("contact_name", ""), lead.get("contact_title", ""),
                    lead.get("contact_email", ""), lead.get("contact_phone", ""),
                    lead.get("contact_linkedin", ""),
                    lead.get("decision_maker_score", 0),
                    lead.get("enrichment_source", "web"),
                    lead.get("enrichment_confidence", 0.5),
                    lead.get("source", ""), lead.get("source_url", ""),
                    lead.get("raw_snippet", ""), lead.get("trigger", ""),
                    score.get("fit", 0), score.get("intent", 0),
                    score.get("access", 0), score.get("value", 0),
                    score.get("urgency", 0), score.get("master", 0),
                    score.get("tier", "P4"),
                    json.dumps(score.get("reasons", [])),
                    score.get("next_action", ""), score.get("next_action_ar", ""),
                    run_id, lead.get("enriched_at", ""),
                ))

            # Update run record
            ts = result.get("tier_summary", {})
            conn.execute("""
                UPDATE intelligence_runs SET
                    total_discovered=?, total_deduped=?, total_enriched=?,
                    tier_p1=?, tier_p2=?, tier_p3=?, tier_p4=?,
                    duration_sec=?, status='complete'
                WHERE id=?
            """, (
                result.get("total_discovered", 0),
                result.get("total_after_dedup", 0),
                result.get("total_enriched", 0),
                ts.get("P1_outreach_now", 0), ts.get("P2_enrich_more", 0),
                ts.get("P3_nurture", 0), ts.get("P4_archive", 0),
                result.get("pipeline_duration_sec", 0),
                run_id,
            ))

        audit_log(user["org_id"], "intelligence", "pipeline_run", user["id"], run_id,
                  {"motion": motion, "total": result.get("total_enriched", 0)})

        # Return summary (not full scored list — too large)
        return _json({
            "run_id": run_id,
            "total_discovered": result["total_discovered"],
            "total_after_dedup": result["total_after_dedup"],
            "total_enriched": result["total_enriched"],
            "tier_summary": result["tier_summary"],
            "pipeline_duration_sec": result["pipeline_duration_sec"],
            "p1_leads": result["p1_leads"][:10],
            "outreach_briefs": result["outreach_briefs"][:5],
        })

    except Exception as e:
        with db() as conn:
            conn.execute(
                "UPDATE intelligence_runs SET status='error', error_message=? WHERE id=?",
                (str(e)[:500], run_id)
            )
        return _json({"error": str(e), "run_id": run_id}, 500)


# ─── LEAD MANAGEMENT ─────────────────────────────────────────────────────────

@intelligence_bp.get("/leads")
@require_auth
def list_intelligence_leads(user):
    """List discovered leads with filters"""
    tier = request.args.get("tier")          # P1|P2|P3|P4
    status = request.args.get("status")      # discovered|contacted|qualified|archived
    sort = request.args.get("sort", "score") # score|date
    limit = min(int(request.args.get("limit", 50)), 200)
    offset = int(request.args.get("offset", 0))

    conditions = ["org_id=?"]
    params = [user["org_id"]]
    if tier:
        conditions.append("priority_tier=?")
        params.append(tier)
    if status:
        conditions.append("status=?")
        params.append(status)

    order = "score_master DESC" if sort == "score" else "created_at DESC"
    where = " AND ".join(conditions)

    with db() as conn:
        rows = conn.execute(
            f"SELECT * FROM intelligence_leads WHERE {where} ORDER BY {order} LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) FROM intelligence_leads WHERE {where}", params
        ).fetchone()[0]

    leads = []
    for row in rows:
        lead = dict(row)
        for field in ["tech_stack", "signals", "recent_news", "score_reasons"]:
            try:
                lead[field] = json.loads(lead[field] or "[]")
            except Exception:
                lead[field] = []
        leads.append(lead)

    return _json({"leads": leads, "total": total, "limit": limit, "offset": offset})


@intelligence_bp.get("/leads/<lead_id>")
@require_auth
def get_intelligence_lead(user, lead_id):
    """Get a single intelligence lead"""
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM intelligence_leads WHERE id=? AND org_id=?",
            (lead_id, user["org_id"])
        ).fetchone()
    if not row:
        return _json({"error": "Lead not found"}, 404)
    lead = dict(row)
    for field in ["tech_stack", "signals", "recent_news", "score_reasons"]:
        try:
            lead[field] = json.loads(lead[field] or "[]")
        except Exception:
            lead[field] = []
    return _json(lead)


@intelligence_bp.patch("/leads/<lead_id>/status")
@require_auth
def update_lead_status(user, lead_id):
    """Update lead status — contacted | qualified | archived"""
    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in ("discovered", "contacted", "qualified", "archived"):
        return _json({"error": "Invalid status"}, 400)

    with db() as conn:
        conn.execute("""
            UPDATE intelligence_leads SET status=?, reviewed_by=?, reviewed_at=datetime('now')
            WHERE id=? AND org_id=?
        """, (new_status, user["id"], lead_id, user["org_id"]))

    audit_log(user["org_id"], "intelligence", f"lead_status_{new_status}", user["id"], lead_id)
    return _json({"id": lead_id, "status": new_status})


@intelligence_bp.post("/leads/<lead_id>/push-to-crm")
@require_auth
def push_lead_to_crm(user, lead_id):
    """Push an intelligence lead to the CRM leads table"""
    with db() as conn:
        il = conn.execute(
            "SELECT * FROM intelligence_leads WHERE id=? AND org_id=?",
            (lead_id, user["org_id"])
        ).fetchone()
        if not il:
            return _json({"error": "Lead not found"}, 404)

        crm_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO leads (id, org_id, company_name, contact_name, contact_email,
                contact_phone, source, industry, company_size, region, status, score,
                stage, enriched_data)
            VALUES (?, ?, ?, ?, ?, ?, 'intelligence', ?, ?, ?, 'new', ?, 'intake', ?)
        """, (
            crm_id, user["org_id"],
            il["company_name"], il["contact_name"] or "",
            il["contact_email"] or "", il["contact_phone"] or "",
            il["industry"] or "", il["company_size"] or "",
            il["region"] or "", il["score_master"],
            json.dumps({
                "signals": json.loads(il["signals"] or "[]"),
                "domain": il["domain"],
                "description": il["description"],
                "score_breakdown": {
                    "fit": il["score_fit"], "intent": il["score_intent"],
                    "access": il["score_access"], "value": il["score_value"],
                    "urgency": il["score_urgency"],
                }
            })
        ))
        conn.execute(
            "UPDATE intelligence_leads SET crm_lead_id=?, status='qualified' WHERE id=?",
            (crm_id, lead_id)
        )

    audit_log(user["org_id"], "intelligence", "lead_pushed_to_crm", user["id"], lead_id,
              {"crm_lead_id": crm_id})
    return _json({"lead_id": lead_id, "crm_lead_id": crm_id, "message": "Pushed to CRM"}, 201)


# ─── OUTREACH ────────────────────────────────────────────────────────────────

@intelligence_bp.post("/outreach/generate")
@require_auth
def generate_outreach(user):
    """
    Generate outreach brief for a single lead.
    Body: { lead_id, motion? }
    """
    data = request.get_json() or {}
    lead_id = data.get("lead_id")
    motion = data.get("motion", "sales")

    with db() as conn:
        row = conn.execute(
            "SELECT * FROM intelligence_leads WHERE id=? AND org_id=?",
            (lead_id, user["org_id"])
        ).fetchone()
    if not row:
        return _json({"error": "Lead not found"}, 404)

    lead = dict(row)
    for field in ["tech_stack", "signals", "recent_news"]:
        try:
            lead[field] = json.loads(lead[field] or "[]")
        except Exception:
            lead[field] = []

    score_dict = {
        "fit": lead.get("score_fit", 0), "intent": lead.get("score_intent", 0),
        "access": lead.get("score_access", 0), "value": lead.get("score_value", 0),
        "urgency": lead.get("score_urgency", 0), "master": lead.get("score_master", 0),
        "tier": lead.get("priority_tier", "P3"),
    }

    brief = generate_outreach_brief(lead, score_dict, motion)

    # Save outreach back to lead
    with db() as conn:
        conn.execute("""
            UPDATE intelligence_leads SET
                outreach_whatsapp_ar=?, outreach_email_subject_ar=?,
                outreach_email_body_ar=?, outreach_linkedin_ar=?, outreach_angle=?
            WHERE id=?
        """, (
            brief.whatsapp_ar, brief.email_subject_ar, brief.email_body_ar,
            brief.linkedin_ar, brief.angle, lead_id
        ))

    audit_log(user["org_id"], "intelligence", "outreach_generated", user["id"], lead_id)
    return _json({
        "lead_id": lead_id,
        "company": brief.company_name,
        "angle": brief.angle,
        "whatsapp_ar": brief.whatsapp_ar,
        "email_subject_ar": brief.email_subject_ar,
        "email_body_ar": brief.email_body_ar,
        "email_subject_en": brief.email_subject_en,
        "email_body_en": brief.email_body_en,
        "linkedin_ar": brief.linkedin_ar,
        "personalization_score": brief.personalization_score,
    })


# ─── WATCHLIST & TRIGGERS ────────────────────────────────────────────────────

@intelligence_bp.get("/watchlist")
@require_auth
def get_watchlist(user):
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM intelligence_watchlist WHERE org_id=? AND active=1 ORDER BY priority DESC",
            (user["org_id"],)
        ).fetchall()
    return _json({"watchlist": [dict(r) for r in rows]})


@intelligence_bp.post("/watchlist")
@require_auth
def add_to_watchlist(user):
    data = request.get_json() or {}
    wid = str(uuid.uuid4())
    with db() as conn:
        conn.execute("""
            INSERT INTO intelligence_watchlist (id, org_id, company_name, domain, priority, added_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (wid, user["org_id"], data.get("company_name", ""),
              data.get("domain", ""), data.get("priority", 0), user["id"]))
    return _json({"id": wid, "message": "Added to watchlist"}, 201)


@intelligence_bp.delete("/watchlist/<wid>")
@require_auth
def remove_from_watchlist(user, wid):
    with db() as conn:
        conn.execute(
            "UPDATE intelligence_watchlist SET active=0 WHERE id=? AND org_id=?",
            (wid, user["org_id"])
        )
    return _json({"id": wid, "message": "Removed from watchlist"})


@intelligence_bp.post("/triggers/scan")
@require_auth
def scan_triggers(user):
    if user["role"] not in ("manager", "admin"):
        return _json({"error": "Forbidden"}, 403)
    """
    Scan watchlist companies for trigger events.
    Body: { company_names?: list[str] }
    """
    data = request.get_json() or {}
    company_names = data.get("company_names")

    if not company_names:
        with db() as conn:
            rows = conn.execute(
                "SELECT company_name FROM intelligence_watchlist WHERE org_id=? AND active=1",
                (user["org_id"],)
            ).fetchall()
        company_names = [r["company_name"] for r in rows]

    if not company_names:
        return _json({"message": "No companies to scan", "triggers": {}})

    # Limit to 5 companies per manual scan
    company_names = company_names[:5]
    trigger_results = scan_watchlist(company_names)

    # Persist triggers
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with db() as conn:
        for company, events in trigger_results.items():
            for event in events:
                tid = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO intelligence_triggers (
                        id, org_id, company_name, trigger_type, trigger_label_ar,
                        signal_strength, evidence, source_url,
                        recommended_action_ar, recommended_action_en
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tid, user["org_id"], company,
                    event["type"], event["label_ar"],
                    event["strength"], event["evidence"][:500],
                    event["url"][:300],
                    event["action_ar"], event["action_en"],
                ))

    audit_log(user["org_id"], "intelligence", "triggers_scanned", user["id"],
              f"watchlist-{len(company_names)}", {"companies": company_names})
    return _json({
        "companies_scanned": len(company_names),
        "triggers_found": sum(len(v) for v in trigger_results.values()),
        "results": trigger_results,
    })


@intelligence_bp.get("/triggers")
@require_auth
def list_triggers(user):
    with db() as conn:
        rows = conn.execute(
            """SELECT * FROM intelligence_triggers WHERE org_id=?
               ORDER BY signal_strength DESC, detected_at DESC LIMIT 50""",
            (user["org_id"],)
        ).fetchall()
    return _json({"triggers": [dict(r) for r in rows]})


# ─── RUNS HISTORY ────────────────────────────────────────────────────────────

@intelligence_bp.get("/runs")
@require_auth
def list_runs(user):
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM intelligence_runs WHERE org_id=? ORDER BY created_at DESC LIMIT 20",
            (user["org_id"],)
        ).fetchall()
    return _json({"runs": [dict(r) for r in rows]})


# ─── DASHBOARD SUMMARY ───────────────────────────────────────────────────────

@intelligence_bp.get("/dashboard")
@require_auth
def intelligence_dashboard(user):
    """Intelligence OS overview — stats for the frontend dashboard"""
    with db() as conn:
        total = conn.execute(
            "SELECT COUNT(*) FROM intelligence_leads WHERE org_id=?", (user["org_id"],)
        ).fetchone()[0]
        tiers = conn.execute(
            """SELECT priority_tier, COUNT(*) as cnt FROM intelligence_leads
               WHERE org_id=? GROUP BY priority_tier""",
            (user["org_id"],)
        ).fetchall()
        top_leads = conn.execute(
            """SELECT company_name, score_master, priority_tier, signals,
                      contact_email, next_action_ar, outreach_angle, status
               FROM intelligence_leads WHERE org_id=?
               ORDER BY score_master DESC LIMIT 10""",
            (user["org_id"],)
        ).fetchall()
        trigger_count = conn.execute(
            "SELECT COUNT(*) FROM intelligence_triggers WHERE org_id=? AND is_actioned=0",
            (user["org_id"],)
        ).fetchone()[0]
        runs = conn.execute(
            """SELECT COUNT(*) as total, MAX(created_at) as last_run
               FROM intelligence_runs WHERE org_id=?""",
            (user["org_id"],)
        ).fetchone()

    tier_breakdown = {r["priority_tier"]: r["cnt"] for r in tiers}

    top = []
    for row in top_leads:
        lead = dict(row)
        try:
            lead["signals"] = json.loads(lead["signals"] or "[]")
        except Exception:
            lead["signals"] = []
        top.append(lead)

    return _json({
        "total_leads": total,
        "tier_breakdown": {
            "P1_outreach_now": tier_breakdown.get("P1", 0),
            "P2_enrich_more": tier_breakdown.get("P2", 0),
            "P3_nurture": tier_breakdown.get("P3", 0),
            "P4_archive": tier_breakdown.get("P4", 0),
        },
        "unactioned_triggers": trigger_count,
        "pipeline_runs": runs["total"] if runs else 0,
        "last_run": runs["last_run"] if runs else None,
        "top_leads": top,
    })

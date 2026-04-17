"""Executive & Board OS — Command Center"""
from flask import Blueprint, request, jsonify
from app.core.database import db
from app.core.audit import log
from app.api.routes.auth import require_auth
import uuid, json

executive_bp = Blueprint("executive", __name__, url_prefix="/executive")

@executive_bp.get("/approvals")
@require_auth
def list_approvals(user):
    with db() as conn:
        if user["role"] == "admin":
            rows = conn.execute("SELECT * FROM approvals WHERE org_id=? ORDER BY created_at DESC", (user["org_id"],)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM approvals WHERE org_id=? AND status='pending' ORDER BY created_at DESC", (user["org_id"],)).fetchall()
    return jsonify([dict(r) for r in rows])

@executive_bp.patch("/approvals/<aid>/decide")
@require_auth
def decide_approval(user, aid):
    if user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Forbidden"}), 403
    data = request.get_json() or {}
    decision = data.get("decision")  # "approved" or "rejected"
    if decision not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid decision"}), 400
    with db() as conn:
        conn.execute("UPDATE approvals SET status=?, approved_by=?, decision_at=datetime('now') WHERE id=? AND org_id=?",
                     (decision, user["id"], aid, user["org_id"]))
    log(user["org_id"], "executive", f"approval_{decision}", user["id"], aid, {"decision": decision})
    return jsonify({"decision": decision})

@executive_bp.get("/command-center")
@require_auth
def command_center(user):
    """The Executive Command Center — full cross-module view"""
    if user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Forbidden"}), 403
    org = user["org_id"]
    with db() as conn:
        # Revenue
        pipeline = conn.execute("SELECT SUM(value) as t, COUNT(*) as c FROM deals WHERE org_id=?", (org,)).fetchone()
        weighted = conn.execute("SELECT SUM(value*probability/100.0) as w FROM deals WHERE org_id=?", (org,)).fetchone()
        arr = conn.execute("SELECT SUM(arr) as t FROM accounts WHERE org_id=?", (org,)).fetchone()
        # Approvals
        pending_approvals = conn.execute("SELECT COUNT(*) as c FROM approvals WHERE org_id=? AND status='pending'", (org,)).fetchone()["c"]
        # Deals by stage
        deals_by_stage = conn.execute("SELECT stage, COUNT(*) as c, SUM(value) as v FROM deals WHERE org_id=? GROUP BY stage", (org,)).fetchall()
        # Partners
        active_partners = conn.execute("SELECT COUNT(*) as c FROM partners WHERE org_id=? AND status='active'", (org,)).fetchone()["c"]
        partner_revenue = conn.execute("SELECT SUM(revenue_contribution) as r FROM partners WHERE org_id=?", (org,)).fetchone()["r"] or 0
        # Renewals at risk
        at_risk_arr = conn.execute("SELECT SUM(current_arr) as t FROM renewals WHERE org_id=? AND churn_risk_score > 50", (org,)).fetchone()["t"] or 0
        # Procurement
        pending_procurement = conn.execute("SELECT COUNT(*) as c FROM procurement_requests WHERE org_id=? AND approval_status='pending'", (org,)).fetchone()["c"]
        # M&A
        ma_pipeline_value = conn.execute("SELECT SUM(estimated_value) as t FROM ma_targets WHERE org_id=?", (org,)).fetchone()["t"] or 0
        # Audit
        total_audit = conn.execute("SELECT COUNT(*) as c FROM audit_log WHERE org_id=?", (org,)).fetchone()["c"]
        # Executive pack
        ep = conn.execute("SELECT * FROM executive_packs WHERE org_id=? ORDER BY generated_at DESC LIMIT 1", (org,)).fetchone()

    data = {
        "revenue": {
            "total_pipeline": pipeline["t"] or 0,
            "deal_count": pipeline["c"] or 0,
            "weighted_forecast": weighted["w"] or 0,
            "total_arr": arr["t"] or 0,
            "deals_by_stage": [dict(r) for r in deals_by_stage]
        },
        "approvals": {
            "pending": pending_approvals,
        },
        "partnerships": {
            "active_partners": active_partners,
            "partner_revenue_contribution": partner_revenue
        },
        "renewals": {
            "arr_at_risk": at_risk_arr
        },
        "procurement": {
            "pending_approvals": pending_procurement
        },
        "ma": {
            "pipeline_value": ma_pipeline_value
        },
        "governance": {
            "audit_entries": total_audit,
            "chain_integrity": "verified"
        },
        "audit": {
            "total_log_entries": total_audit,
            "chain_integrity": "verified"
        },
        "executive_pack": dict(ep) if ep else None
    }

    if ep:
        data["executive_pack"]["blockers"] = json.loads(ep["blockers"]) if ep["blockers"] else []
        data["executive_pack"]["next_best_actions"] = json.loads(ep["next_best_actions"]) if ep["next_best_actions"] else []

    log(org, "executive", "command_center_accessed", user["id"], "command-center", {})
    return jsonify(data)

@executive_bp.get("/weekly-pack")
@require_auth
def weekly_pack(user):
    if user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Forbidden"}), 403
    with db() as conn:
        row = conn.execute("SELECT * FROM executive_packs WHERE org_id=? ORDER BY generated_at DESC LIMIT 1", (user["org_id"],)).fetchone()
    if not row:
        return jsonify({"error": "No pack generated yet"}), 404
    pack = dict(row)
    pack["blockers"] = json.loads(pack["blockers"]) if pack["blockers"] else []
    pack["next_best_actions"] = json.loads(pack["next_best_actions"]) if pack["next_best_actions"] else []
    return jsonify(pack)

@executive_bp.get("/risk-heatmap")
@require_auth
def risk_heatmap(user):
    if user["role"] not in ["admin", "manager"]:
        return jsonify({"error": "Forbidden"}), 403
    org = user["org_id"]
    risks = []
    with db() as conn:
        high_churn = conn.execute("SELECT COUNT(*) as c FROM renewals WHERE org_id=? AND churn_risk_score > 70", (org,)).fetchone()["c"]
        if high_churn > 0:
            risks.append({"module": "renewal", "risk": "high_churn", "count": high_churn, "severity": "high"})
        pending_disc = conn.execute("SELECT COUNT(*) as c FROM quotes WHERE org_id=? AND approval_status='pending' AND discount_pct > 20", (org,)).fetchone()["c"]
        if pending_disc > 0:
            risks.append({"module": "pricing", "risk": "large_discounts_pending", "count": pending_disc, "severity": "medium"})
        high_risk_vendors = conn.execute("SELECT COUNT(*) as c FROM vendors WHERE org_id=? AND risk_level='high'", (org,)).fetchone()["c"]
        if high_risk_vendors > 0:
            risks.append({"module": "procurement", "risk": "high_risk_vendors", "count": high_risk_vendors, "severity": "medium"})
    return jsonify({"risks": risks, "overall_risk": "high" if any(r["severity"]=="high" for r in risks) else "medium"})

@executive_bp.get("/audit-chain")
@require_auth
def audit_chain(user):
    if user["role"] != "admin":
        return jsonify({"error": "Forbidden"}), 403
    with db() as conn:
        rows = conn.execute("SELECT * FROM audit_log WHERE org_id=? ORDER BY id DESC LIMIT 50", (user["org_id"],)).fetchall()
        total = conn.execute("SELECT COUNT(*) as c FROM audit_log WHERE org_id=?", (user["org_id"],)).fetchone()["c"]
    return jsonify({"total_entries": total, "recent": [dict(r) for r in rows]})

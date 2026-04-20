"""Dealix Sovereign Revenue, Deal, Growth & Commitment OS — Backend"""
from flask import Flask, jsonify
from flask_cors import CORS

from app.core.database import init_db
from app.api.routes.auth import auth_bp
from app.api.routes.revenue import revenue_bp
from app.api.routes.pricing import pricing_bp
from app.api.routes.partnership import partnership_bp
from app.api.routes.procurement import procurement_bp
from app.api.routes.renewal import renewal_bp
from app.api.routes.expansion import expansion_bp
from app.api.routes.ma import ma_bp
from app.api.routes.pmo import pmo_bp
from app.api.routes.executive import executive_bp
from app.api.routes.intelligence import intelligence_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Register all 9 OS blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(revenue_bp)
app.register_blueprint(pricing_bp)
app.register_blueprint(partnership_bp)
app.register_blueprint(procurement_bp)
app.register_blueprint(renewal_bp)
app.register_blueprint(expansion_bp)
app.register_blueprint(ma_bp)
app.register_blueprint(pmo_bp)
app.register_blueprint(executive_bp)
app.register_blueprint(intelligence_bp)  # Revenue Intelligence OS — Lead Machine

@app.get("/api/health")
def health():
    from app.core.database import db
    with db() as conn:
        count = conn.execute("SELECT COUNT(*) as c FROM audit_log").fetchone()["c"]
        modules = conn.execute("SELECT COUNT(DISTINCT module) as m FROM audit_log").fetchone()["m"]
    return jsonify({
        "status": "healthy",
        "database": "connected",
        "audit_entries": count,
        "active_modules": modules,
        "modules": [
            "Revenue OS", "Pricing & Margin Control OS", "Partnership & Alliance OS",
            "Procurement & Vendor OS", "Renewal & Expansion OS", "Market Entry OS",
            "M&A Corporate Development OS", "PMI Strategic PMO OS", "Executive Board OS"
        ]
    })

@app.get("/")
def root():
    return jsonify({
        "product": "Dealix",
        "tagline": "Sovereign Revenue, Deal, Growth & Commitment OS",
        "version": "2.0.0",
        "modules": 9,
        "docs": "/api/health"
    })

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000, debug=False)

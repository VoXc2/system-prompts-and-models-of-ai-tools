"""Dealix Database Core — SQLite with full schema for 9 OS modules"""
import sqlite3
import hashlib
import json
import time
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "dealix.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

@contextmanager
def db():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    with db() as conn:
        conn.executescript("""
        -- Users & Auth
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'sales',
            org_id TEXT NOT NULL DEFAULT 'dealix',
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- 1. REVENUE OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS leads (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            source TEXT DEFAULT 'website',
            industry TEXT,
            company_size TEXT,
            annual_revenue TEXT,
            region TEXT,
            status TEXT DEFAULT 'new',
            score INTEGER DEFAULT 0,
            stage TEXT DEFAULT 'intake',
            assigned_to TEXT,
            notes TEXT,
            enriched_data TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS deals (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            lead_id TEXT,
            title TEXT NOT NULL,
            value REAL DEFAULT 0,
            currency TEXT DEFAULT 'SAR',
            stage TEXT DEFAULT 'discovery',
            probability INTEGER DEFAULT 0,
            close_date TEXT,
            owner_id TEXT,
            account_id TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            industry TEXT,
            tier TEXT DEFAULT 'standard',
            arr REAL DEFAULT 0,
            health_score INTEGER DEFAULT 75,
            csm_id TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- 2. PRICING & MARGIN CONTROL OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS quotes (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            deal_id TEXT,
            account_id TEXT,
            line_items TEXT,
            subtotal REAL DEFAULT 0,
            discount_pct REAL DEFAULT 0,
            discount_reason TEXT,
            final_price REAL DEFAULT 0,
            margin_pct REAL DEFAULT 0,
            approval_status TEXT DEFAULT 'pending',
            approved_by TEXT,
            approved_at TEXT,
            valid_until TEXT,
            created_by TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS discount_policies (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            max_discount_pct REAL NOT NULL,
            approver_role TEXT NOT NULL,
            deal_value_min REAL DEFAULT 0,
            deal_value_max REAL,
            active INTEGER DEFAULT 1
        );

        -- ============================================================
        -- 3. PARTNERSHIP & ALLIANCE OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS partners (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            partner_type TEXT DEFAULT 'reseller',
            status TEXT DEFAULT 'prospect',
            fit_score INTEGER DEFAULT 0,
            revenue_contribution REAL DEFAULT 0,
            health_score INTEGER DEFAULT 75,
            contact_name TEXT,
            contact_email TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS alliance_workflows (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            partner_id TEXT NOT NULL,
            stage TEXT DEFAULT 'scouting',
            economics_model TEXT,
            term_sheet TEXT,
            approval_status TEXT DEFAULT 'pending',
            approved_by TEXT,
            activation_date TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- 4. PROCUREMENT / VENDOR OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS vendors (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            vendor_name TEXT NOT NULL,
            category TEXT,
            risk_level TEXT DEFAULT 'medium',
            spend REAL DEFAULT 0,
            health_score INTEGER DEFAULT 75,
            contract_expiry TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS procurement_requests (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            vendor_id TEXT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            justification TEXT,
            status TEXT DEFAULT 'draft',
            approval_status TEXT DEFAULT 'pending',
            approved_by TEXT,
            approved_at TEXT,
            created_by TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- 5. RENEWAL & EXPANSION OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS renewals (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            account_id TEXT NOT NULL,
            current_arr REAL DEFAULT 0,
            renewal_date TEXT,
            churn_risk_score INTEGER DEFAULT 0,
            expansion_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'upcoming',
            rescue_play_active INTEGER DEFAULT 0,
            assigned_to TEXT,
            notes TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- 6. EXPANSION / MARKET ENTRY OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS market_entries (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            market_name TEXT NOT NULL,
            segment TEXT,
            readiness_score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'scanning',
            gtm_plan TEXT,
            launch_date TEXT,
            stop_loss_triggered INTEGER DEFAULT 0,
            actual_vs_forecast TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- 7. M&A / CORPORATE DEVELOPMENT OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS ma_targets (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            target_name TEXT NOT NULL,
            industry TEXT,
            estimated_value REAL,
            fit_score INTEGER DEFAULT 0,
            stage TEXT DEFAULT 'screening',
            dd_findings TEXT,
            valuation_memo TEXT,
            synergy_model TEXT,
            ic_pack_status TEXT DEFAULT 'pending',
            board_pack_ready INTEGER DEFAULT 0,
            close_date TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- 8. PMI / STRATEGIC PMO OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS pmo_projects (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            title TEXT NOT NULL,
            type TEXT DEFAULT 'pmi',
            status TEXT DEFAULT 'active',
            day1_readiness INTEGER DEFAULT 0,
            plan_30_60_90 TEXT,
            synergy_target REAL DEFAULT 0,
            synergy_realized REAL DEFAULT 0,
            blockers TEXT,
            health TEXT DEFAULT 'green',
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- 9. EXECUTIVE / BOARD OS
        -- ============================================================
        CREATE TABLE IF NOT EXISTS approvals (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            module TEXT NOT NULL,
            reference_id TEXT NOT NULL,
            title TEXT NOT NULL,
            amount REAL,
            risk_level TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'pending',
            requested_by TEXT,
            approved_by TEXT,
            decision_at TEXT,
            evidence_pack TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS executive_packs (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            week_label TEXT,
            actual_revenue REAL DEFAULT 0,
            forecast_revenue REAL DEFAULT 0,
            open_approvals INTEGER DEFAULT 0,
            blockers TEXT,
            next_best_actions TEXT,
            risk_heatmap TEXT,
            generated_at TEXT DEFAULT (datetime('now'))
        );

        -- ============================================================
        -- AUDIT CHAIN (cross-module)
        -- ============================================================
        -- =============================================
        -- Revenue Intelligence OS — Lead Machine Tables
        -- =============================================

        -- ICP configs per org
        CREATE TABLE IF NOT EXISTS icp_configs (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            name TEXT NOT NULL,
            config TEXT NOT NULL,         -- JSON ICPConfig
            is_active INTEGER DEFAULT 1,
            created_by TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Discovered leads (raw, before enrichment)
        CREATE TABLE IF NOT EXISTS intelligence_leads (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            domain TEXT,
            industry TEXT,
            region TEXT,
            company_size TEXT,
            description TEXT,
            website TEXT,
            tech_stack TEXT,              -- JSON list
            signals TEXT,                 -- JSON list
            recent_news TEXT,             -- JSON list
            contact_name TEXT,
            contact_title TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            contact_linkedin TEXT,
            decision_maker_score INTEGER DEFAULT 0,
            enrichment_source TEXT DEFAULT 'web',
            enrichment_confidence REAL DEFAULT 0.5,
            source TEXT,
            source_url TEXT,
            raw_snippet TEXT,
            trigger TEXT,
            -- Scores
            score_fit INTEGER DEFAULT 0,
            score_intent INTEGER DEFAULT 0,
            score_access INTEGER DEFAULT 0,
            score_value INTEGER DEFAULT 0,
            score_urgency INTEGER DEFAULT 0,
            score_master INTEGER DEFAULT 0,
            priority_tier TEXT DEFAULT 'P4',
            score_reasons TEXT,           -- JSON list
            next_action TEXT,
            next_action_ar TEXT,
            -- Outreach
            outreach_whatsapp_ar TEXT,
            outreach_email_subject_ar TEXT,
            outreach_email_body_ar TEXT,
            outreach_linkedin_ar TEXT,
            outreach_angle TEXT,
            -- Pipeline tracking
            pipeline_run_id TEXT,
            crm_lead_id TEXT,             -- linked to leads table
            status TEXT DEFAULT 'discovered',  -- discovered | contacted | qualified | archived
            reviewed_by TEXT,
            reviewed_at TEXT,
            enriched_at TEXT,
            discovered_at TEXT DEFAULT (datetime('now')),
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Pipeline run history
        CREATE TABLE IF NOT EXISTS intelligence_runs (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            icp_id TEXT,
            run_mode TEXT DEFAULT 'auto',  -- auto | manual | triggered
            motion TEXT DEFAULT 'sales',
            total_discovered INTEGER DEFAULT 0,
            total_deduped INTEGER DEFAULT 0,
            total_enriched INTEGER DEFAULT 0,
            tier_p1 INTEGER DEFAULT 0,
            tier_p2 INTEGER DEFAULT 0,
            tier_p3 INTEGER DEFAULT 0,
            tier_p4 INTEGER DEFAULT 0,
            duration_sec REAL DEFAULT 0,
            status TEXT DEFAULT 'running', -- running | complete | error
            error_message TEXT,
            created_by TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Watchlist for trigger alerts
        CREATE TABLE IF NOT EXISTS intelligence_watchlist (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            domain TEXT,
            priority INTEGER DEFAULT 0,
            last_scanned TEXT,
            active INTEGER DEFAULT 1,
            added_by TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        -- Trigger events detected
        CREATE TABLE IF NOT EXISTS intelligence_triggers (
            id TEXT PRIMARY KEY,
            org_id TEXT NOT NULL,
            company_name TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            trigger_label_ar TEXT,
            signal_strength INTEGER DEFAULT 0,
            evidence TEXT,
            source_url TEXT,
            recommended_action_ar TEXT,
            recommended_action_en TEXT,
            is_actioned INTEGER DEFAULT 0,
            actioned_by TEXT,
            detected_at TEXT DEFAULT (datetime('now'))
        );

        -- Entity registry (deduplication)
        CREATE TABLE IF NOT EXISTS intelligence_entities (
            id TEXT PRIMARY KEY,
            canonical_name TEXT NOT NULL,
            normalized_name TEXT,
            domain TEXT,
            aliases TEXT,   -- JSON list
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_id TEXT NOT NULL,
            module TEXT NOT NULL,
            action TEXT NOT NULL,
            actor_id TEXT,
            resource_id TEXT,
            payload TEXT,
            prev_hash TEXT,
            entry_hash TEXT,
            ts TEXT DEFAULT (datetime('now'))
        );
        """)

        # Seed admin users
        import hashlib, uuid
        users = [
            ("admin-001", "admin@dealix.io", "Admin", "admin"),
            ("mgr-001", "manager@dealix.io", "Manager", "manager"),
            ("sales-001", "sales@dealix.io", "Sales Rep", "sales"),
        ]
        passwords = {"admin": "Admin1234!", "manager": "Manager1234!", "sales": "Sales1234!"}
        for uid, email, name, role in users:
            pw = hashlib.sha256(passwords[role].encode()).hexdigest()
            conn.execute("""
                INSERT OR IGNORE INTO users (id, email, name, role, password_hash)
                VALUES (?, ?, ?, ?, ?)
            """, (uid, email, name, role, pw))

        # Seed discount policies
        conn.execute("""
            INSERT OR IGNORE INTO discount_policies (id, org_id, max_discount_pct, approver_role, deal_value_min, deal_value_max)
            VALUES ('dp-1','dealix',10,'sales',0,50000),
                   ('dp-2','dealix',20,'manager',50000,200000),
                   ('dp-3','dealix',35,'admin',200000,NULL)
        """)

        # Seed sample data for dashboard
        _seed_sample_data(conn)

def _seed_sample_data(conn):
    import uuid
    # Sample leads
    leads = [
        ("lead-001","dealix","البنك الأهلي","محمد الغامدي","m@anb.com","0500000001","referral","banking","enterprise","500M+","Riyadh","qualified",88,"proposal","sales-001"),
        ("lead-002","dealix","stc","فيصل الحربي","f@stc.com","0500000002","website","telecom","enterprise","1B+","Riyadh","qualified",91,"negotiation","sales-001"),
        ("lead-003","dealix","أرامكو","خالد المالكي","k@aramco.com","0500000003","partner","energy","enterprise","10B+","Dhahran","new",72,"intake","sales-001"),
        ("lead-004","dealix","مجموعة العثيم","سارة القحطاني","s@othaim.com","0500000004","website","retail","large","100M+","Riyadh","contacted",65,"discovery","sales-001"),
        ("lead-005","dealix","مستشفى الملك فيصل","أحمد الزهراني","a@kfsh.com","0500000005","referral","healthcare","enterprise","200M+","Riyadh","qualified",79,"proposal","sales-001"),
    ]
    for l in leads:
        conn.execute("""INSERT OR IGNORE INTO leads 
            (id,org_id,company_name,contact_name,contact_email,contact_phone,source,industry,company_size,annual_revenue,region,status,score,stage,assigned_to)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", l)

    # Sample deals
    deals = [
        ("deal-001","dealix","lead-001","صفقة البنك الأهلي — Revenue OS",850000,"SAR","proposal",75,"2026-06-30","sales-001","acc-001"),
        ("deal-002","dealix","lead-002","stc — Enterprise Suite",1200000,"SAR","negotiation",85,"2026-05-31","sales-001","acc-002"),
        ("deal-003","dealix","lead-003","أرامكو — Executive OS",2500000,"SAR","discovery",40,"2026-09-30","sales-001","acc-003"),
        ("deal-004","dealix","lead-005","KFSH — Procurement OS",420000,"SAR","proposal",65,"2026-07-15","sales-001","acc-004"),
    ]
    for d in deals:
        conn.execute("""INSERT OR IGNORE INTO deals
            (id,org_id,lead_id,title,value,currency,stage,probability,close_date,owner_id,account_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""", d)

    # Sample accounts
    accounts = [
        ("acc-001","dealix","البنك الأهلي","banking","enterprise",850000,82,"sales-001"),
        ("acc-002","dealix","stc","telecom","strategic",1200000,91,"sales-001"),
        ("acc-003","dealix","أرامكو","energy","strategic",0,88,"sales-001"),
        ("acc-004","dealix","KFSH","healthcare","enterprise",420000,74,"sales-001"),
    ]
    for a in accounts:
        conn.execute("""INSERT OR IGNORE INTO accounts
            (id,org_id,company_name,industry,tier,arr,health_score,csm_id)
            VALUES (?,?,?,?,?,?,?,?)""", a)

    # Sample partners
    partners = [
        ("part-001","dealix","Oracle Arabia","technology","active",87,320000,82,"علي الدوسري","a@oracle.com"),
        ("part-002","dealix","SAP KSA","technology","active",91,580000,88,"نورة العتيبي","n@sap.com"),
        ("part-003","dealix","Deloitte KSA","consulting","prospect",73,0,0,"طارق المحمد","t@deloitte.com"),
    ]
    for p in partners:
        conn.execute("""INSERT OR IGNORE INTO partners
            (id,org_id,company_name,partner_type,status,fit_score,revenue_contribution,health_score,contact_name,contact_email)
            VALUES (?,?,?,?,?,?,?,?,?,?)""", p)

    # Sample M&A targets
    conn.execute("""INSERT OR IGNORE INTO ma_targets
        (id,org_id,target_name,industry,estimated_value,fit_score,stage)
        VALUES ('ma-001','dealix','Salesbook KSA','SaaS',8500000,84,'due_diligence')""")

    # Sample renewals
    conn.execute("""INSERT OR IGNORE INTO renewals
        (id,org_id,account_id,current_arr,renewal_date,churn_risk_score,expansion_score,status)
        VALUES ('ren-001','dealix','acc-001',850000,'2026-12-31',22,67,'upcoming'),
               ('ren-002','dealix','acc-002',1200000,'2026-10-31',8,88,'upcoming')""")

    # Sample approvals
    conn.execute("""INSERT OR IGNORE INTO approvals
        (id,org_id,module,reference_id,title,amount,risk_level,status,requested_by)
        VALUES 
        ('appr-001','dealix','pricing','deal-001','خصم 25% — البنك الأهلي',212500,'high','pending','sales-001'),
        ('appr-002','dealix','procurement','pr-001','تجديد عقد Oracle',145000,'medium','pending','mgr-001'),
        ('appr-003','dealix','partnership','part-003','تفعيل شراكة Deloitte',0,'low','pending','mgr-001')""")

    # Executive pack
    conn.execute("""INSERT OR IGNORE INTO executive_packs
        (id,org_id,week_label,actual_revenue,forecast_revenue,open_approvals,blockers,next_best_actions)
        VALUES ('ep-001','dealix','الأسبوع 16 — 2026',3850000,4200000,3,
        '["صفقة أرامكو: تأخر RFP","تجديد Oracle: انتهاء العقد في 30 يوم"]',
        '["أغلق خصم البنك الأهلي — 25%","ادفع تجديد Oracle قبل الانتهاء","جدول kickoff مع Deloitte"]')""")

    # Audit chain seed — only insert if no entries exist yet
    existing = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
    if existing > 0:
        return
    prev = "GENESIS"
    entries = [
        ("dealix","revenue","lead_created","admin-001","lead-001","{}"),
        ("dealix","pricing","quote_created","sales-001","deal-001","{}"),
        ("dealix","partnership","partner_added","mgr-001","part-001","{}"),
        ("dealix","executive","pack_generated","admin-001","ep-001","{}"),
    ]
    for org, module, action, actor, resource, payload in entries:
        import hashlib, time
        content = f"{org}:{module}:{action}:{actor}:{resource}:{time.time()}"
        entry_hash = hashlib.sha256(f"{prev}:{content}".encode()).hexdigest()
        conn.execute("""INSERT INTO audit_log (org_id,module,action,actor_id,resource_id,payload,prev_hash,entry_hash)
            VALUES (?,?,?,?,?,?,?,?)""", (org, module, action, actor, resource, payload, prev, entry_hash))
        prev = entry_hash

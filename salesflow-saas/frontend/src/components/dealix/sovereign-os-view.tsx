"use client";

import { useState, useEffect, useCallback } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TENANT = "demo_tenant";

// ─── Types ────────────────────────────────────────────────────────
interface KPI {
  label_ar: string;
  label_en?: string;
  value: number | string;
  unit?: string;
  trend?: "up" | "down" | "neutral";
  severity?: "ok" | "warning" | "critical";
}

interface BoardPack {
  id: string;
  title_ar: string;
  pack_type: string;
  period_label?: string;
  status: string;
  policy_violations_count: number;
  created_at: string;
}

interface Partner {
  id: string;
  name_ar: string;
  partner_type: string;
  status: string;
  strategic_fit_score?: number;
  quarterly_revenue_sar?: number;
  active_deals_count: number;
}

interface MATarget {
  id: string;
  company_name_ar: string;
  sector?: string;
  status: string;
  valuation_low_sar?: number;
  valuation_high_sar?: number;
}

interface ExpansionMarket {
  id: string;
  market_name_ar: string;
  country_code: string;
  status: string;
  priority_score?: number;
  tam_sar?: number;
}

interface PolicyViolation {
  id: string;
  violation_type: string;
  severity: string;
  description_ar: string;
  policy_ref?: string;
  resolved: boolean;
  created_at: string;
}

interface Connector {
  id: string;
  connector_key: string;
  display_name_ar: string;
  vendor?: string;
  api_version: string;
  health_status: string;
  last_success_at?: string;
  last_error?: string;
}

interface ComplianceControl {
  id: string;
  framework: string;
  control_ref: string;
  title_ar: string;
  implementation_status: string;
  risk_level: string;
}

interface ModelRoute {
  lane: string;
  primary_model: string;
  provider: string;
  is_active: boolean;
  avg_latency_ms?: number;
  contradiction_rate_pct?: number;
}

interface Contradiction {
  id: string;
  agent_role: string;
  contradiction_type: string;
  severity: string;
  status: string;
  created_at: string;
}

interface PendingDecision {
  decision_id: string;
  decision_type: string;
  recommendation_ar: string;
  lane: string;
  created_at: string;
}

// ─── Helper Components ────────────────────────────────────────────

function Badge({ children, variant = "neutral" }: { children: React.ReactNode; variant?: string }) {
  const colors: Record<string, string> = {
    ok: "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30",
    warning: "bg-amber-500/20 text-amber-300 border border-amber-500/30",
    critical: "bg-red-500/20 text-red-300 border border-red-500/30",
    neutral: "bg-slate-700/50 text-slate-300 border border-slate-600",
    active: "bg-blue-500/20 text-blue-300 border border-blue-500/30",
    pending: "bg-purple-500/20 text-purple-300 border border-purple-500/30",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colors[variant] || colors.neutral}`}>
      {children}
    </span>
  );
}

function KPICard({ kpi }: { kpi: KPI }) {
  const severityColors = {
    ok: "from-emerald-900/30 to-emerald-800/10 border-emerald-700/30",
    warning: "from-amber-900/30 to-amber-800/10 border-amber-700/30",
    critical: "from-red-900/30 to-red-800/10 border-red-700/30",
  };
  const colorClass = severityColors[kpi.severity || "ok"];
  return (
    <div className={`bg-gradient-to-br ${colorClass} border rounded-xl p-4`}>
      <p className="text-xs text-slate-400 mb-1">{kpi.label_ar}</p>
      <p className="text-2xl font-bold text-white">
        {typeof kpi.value === "number" ? kpi.value.toLocaleString("ar-SA") : kpi.value}
        {kpi.unit && <span className="text-sm text-slate-400 mr-1">{kpi.unit}</span>}
      </p>
      {kpi.label_en && <p className="text-xs text-slate-500 mt-1">{kpi.label_en}</p>}
    </div>
  );
}

function SectionHeader({ ar, en, icon }: { ar: string; en: string; icon: string }) {
  return (
    <div className="flex items-center gap-3 mb-6">
      <span className="text-2xl">{icon}</span>
      <div>
        <h2 className="text-lg font-bold text-white">{ar}</h2>
        <p className="text-xs text-slate-400">{en}</p>
      </div>
    </div>
  );
}

// ─── Surface 1: Executive Room ────────────────────────────────────
function ExecutiveRoom() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [packs, setPacks] = useState<BoardPack[]>([]);
  const [pending, setPending] = useState<PendingDecision[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/v1/executive-room/dashboard?tenant_id=${TENANT}`).then(r => r.ok ? r.json() : null),
      fetch(`${API}/api/v1/executive-room/board-packs?tenant_id=${TENANT}`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/api/v1/decision-plane/pending-hitl?tenant_id=${TENANT}`).then(r => r.ok ? r.json() : { decisions: [] }),
    ]).then(([dash, p, hitl]) => {
      setDashboard(dash);
      setPacks(p || []);
      setPending(hitl?.decisions || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-slate-400 text-sm">جار التحميل...</div>;

  const kpis: KPI[] = [
    { label_ar: "انتهاكات السياسة المفتوحة", label_en: "Open Policy Violations", value: dashboard?.kpis?.open_policy_violations ?? 0, severity: dashboard?.kpis?.open_policy_violations > 0 ? "critical" : "ok" },
    { label_ar: "اعتمادات معلقة", label_en: "Pending Approvals", value: dashboard?.kpis?.pending_approvals ?? 0, severity: dashboard?.kpis?.pending_approvals > 0 ? "warning" : "ok" },
    { label_ar: "حزم المجلس", label_en: "Board Packs", value: dashboard?.kpis?.board_packs_total ?? 0, severity: "ok" },
    { label_ar: "انتهاكات حرجة", label_en: "Critical Violations", value: dashboard?.kpis?.critical_violations ?? 0, severity: dashboard?.kpis?.critical_violations > 0 ? "critical" : "ok" },
  ];

  return (
    <div dir="rtl">
      <SectionHeader ar="الغرفة التنفيذية" en="Executive Room" icon="👑" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {kpis.map((k, i) => <KPICard key={i} kpi={k} />)}
      </div>

      {pending.length > 0 && (
        <div className="mb-8">
          <h3 className="text-sm font-semibold text-purple-300 mb-3">⏳ اعتمادات تنتظر المراجعة</h3>
          <div className="space-y-2">
            {pending.map(d => (
              <div key={d.decision_id} className="bg-purple-900/20 border border-purple-700/30 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <span className="text-sm text-white">{d.decision_type}</span>
                  <p className="text-xs text-slate-400 mt-0.5">{d.recommendation_ar || "لا توجد توصية"}</p>
                </div>
                <Badge variant="pending">معلق</Badge>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <h3 className="text-sm font-semibold text-slate-300 mb-3">📋 حزم المجلس الأخيرة</h3>
        {packs.length === 0 ? (
          <div className="text-slate-500 text-sm bg-slate-800/40 rounded-lg p-4 text-center">لا توجد حزم مجلس حتى الآن</div>
        ) : (
          <div className="space-y-2">
            {packs.slice(0, 5).map(p => (
              <div key={p.id} className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <span className="text-sm text-white">{p.title_ar}</span>
                  <p className="text-xs text-slate-500 mt-0.5">{p.pack_type} · {p.period_label}</p>
                </div>
                <div className="flex items-center gap-2">
                  {p.policy_violations_count > 0 && <Badge variant="critical">{p.policy_violations_count} انتهاك</Badge>}
                  <Badge variant={p.status === "published" ? "ok" : "warning"}>{p.status}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Surface 2: Partnership OS ────────────────────────────────────
function PartnershipOS() {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/partnership-os/partners?tenant_id=${TENANT}`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setPartners(data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const statusColor = (s: string) => {
    if (s === "active") return "ok";
    if (s === "negotiation") return "warning";
    if (s === "terminated") return "critical";
    return "neutral";
  };

  return (
    <div dir="rtl">
      <SectionHeader ar="نظام الشراكات" en="Partnership OS" icon="🤝" />
      {loading ? <div className="text-slate-400 text-sm">جار التحميل...</div> : partners.length === 0 ? (
        <div className="text-slate-500 text-sm bg-slate-800/40 rounded-lg p-6 text-center">
          <p className="text-2xl mb-2">🤝</p>
          <p>لا يوجد شركاء حتى الآن — ابدأ باستكشاف الشركاء المحتملين</p>
        </div>
      ) : (
        <div className="space-y-3">
          {partners.map(p => (
            <div key={p.id} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-white">{p.name_ar}</p>
                  <p className="text-xs text-slate-400 mt-1">{p.partner_type} · {p.active_deals_count} صفقة نشطة</p>
                </div>
                <Badge variant={statusColor(p.status)}>{p.status}</Badge>
              </div>
              <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
                {p.strategic_fit_score && <span>ملاءمة استراتيجية: <span className="text-blue-300">{p.strategic_fit_score}%</span></span>}
                {p.quarterly_revenue_sar && <span>إيرادات ربع سنوية: <span className="text-emerald-300">{p.quarterly_revenue_sar.toLocaleString("ar-SA")} ر.س</span></span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Surface 3: M&A Pipeline Board ───────────────────────────────
function CorporateDevOS() {
  const [targets, setTargets] = useState<MATarget[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/corporate-dev/targets?tenant_id=${TENANT}`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setTargets(data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const statusStages = ["sourced", "screening", "dd_active", "ic_memo", "offer", "signed", "closed", "passed"];
  const stageColor = (s: string) => {
    if (["signed", "closed"].includes(s)) return "ok";
    if (["offer", "ic_memo"].includes(s)) return "warning";
    if (s === "passed") return "neutral";
    return "active";
  };

  return (
    <div dir="rtl">
      <SectionHeader ar="التطوير المؤسسي — M&A" en="Corporate Development / M&A OS" icon="🏢" />

      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {statusStages.map(stage => {
          const count = targets.filter(t => t.status === stage).length;
          return (
            <div key={stage} className="flex-shrink-0 bg-slate-800/40 border border-slate-700/50 rounded-lg px-3 py-2 min-w-[100px]">
              <p className="text-xs text-slate-400">{stage}</p>
              <p className="text-xl font-bold text-white">{count}</p>
            </div>
          );
        })}
      </div>

      {loading ? <div className="text-slate-400 text-sm">جار التحميل...</div> : targets.length === 0 ? (
        <div className="text-slate-500 text-sm bg-slate-800/40 rounded-lg p-6 text-center">
          <p className="text-2xl mb-2">🏢</p>
          <p>لا توجد أهداف استحواذ — ابدأ بإضافة شركات للاستكشاف</p>
        </div>
      ) : (
        <div className="space-y-3">
          {targets.map(t => (
            <div key={t.id} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-white">{t.company_name_ar}</p>
                  <p className="text-xs text-slate-400 mt-1">{t.sector} · السعودية</p>
                </div>
                <Badge variant={stageColor(t.status)}>{t.status}</Badge>
              </div>
              {(t.valuation_low_sar || t.valuation_high_sar) && (
                <div className="flex items-center gap-2 mt-3 text-xs text-slate-400">
                  <span>التقييم:</span>
                  <span className="text-blue-300">
                    {t.valuation_low_sar?.toLocaleString("ar-SA")} - {t.valuation_high_sar?.toLocaleString("ar-SA")} ر.س
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Surface 4: Expansion OS ──────────────────────────────────────
function ExpansionOS() {
  const [markets, setMarkets] = useState<ExpansionMarket[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/expansion-os/markets?tenant_id=${TENANT}`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setMarkets(data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const statusColor = (s: string) => {
    if (s === "live") return "ok";
    if (s === "launching") return "warning";
    if (s === "stopped") return "critical";
    return "active";
  };

  return (
    <div dir="rtl">
      <SectionHeader ar="نظام التوسع الجغرافي" en="Expansion OS" icon="🌍" />
      {loading ? <div className="text-slate-400 text-sm">جار التحميل...</div> : markets.length === 0 ? (
        <div className="text-slate-500 text-sm bg-slate-800/40 rounded-lg p-6 text-center">
          <p className="text-2xl mb-2">🌍</p>
          <p>لا توجد أسواق حالية — ابدأ بمسح السوق وتحديد الأولويات</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {markets.map(m => (
            <div key={m.id} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-semibold text-white">{m.market_name_ar}</p>
                  <p className="text-xs text-slate-400">{m.country_code}</p>
                </div>
                <Badge variant={statusColor(m.status)}>{m.status}</Badge>
              </div>
              <div className="flex gap-3 text-xs text-slate-400">
                {m.priority_score && <span>الأولوية: <span className="text-blue-300">{m.priority_score}</span></span>}
                {m.tam_sar && <span>TAM: <span className="text-emerald-300">{m.tam_sar.toLocaleString("ar-SA")} ر.س</span></span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Surface 5: Trust Plane — Policy Violations Board ────────────
function TrustPlane() {
  const [violations, setViolations] = useState<PolicyViolation[]>([]);
  const [contradictions, setContradictions] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/v1/trust-plane/violations?tenant_id=${TENANT}&resolved=false`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/api/v1/trust-plane/contradictions?tenant_id=${TENANT}`).then(r => r.ok ? r.json() : null),
    ]).then(([v, c]) => {
      setViolations(v || []);
      setContradictions(c);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const severityVariant = (s: string) => {
    if (s === "critical") return "critical";
    if (s === "high") return "critical";
    if (s === "medium") return "warning";
    return "neutral";
  };

  const contradictionKPIs: KPI[] = contradictions ? [
    { label_ar: "إجمالي التناقضات", label_en: "Total Contradictions", value: contradictions.total_contradictions, severity: "ok" },
    { label_ar: "مفتوحة", label_en: "Open", value: contradictions.open_contradictions, severity: contradictions.open_contradictions > 0 ? "warning" : "ok" },
    { label_ar: "حرجة مفتوحة", label_en: "Critical Open", value: contradictions.critical_open, severity: contradictions.critical_open > 0 ? "critical" : "ok" },
  ] : [];

  return (
    <div dir="rtl">
      <SectionHeader ar="طبقة الثقة — انتهاكات السياسة" en="Trust Plane — Policy Violations Board" icon="🔐" />

      {contradictions && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          {contradictionKPIs.map((k, i) => <KPICard key={i} kpi={k} />)}
        </div>
      )}

      {loading ? <div className="text-slate-400 text-sm">جار التحميل...</div> : violations.length === 0 ? (
        <div className="text-emerald-500 text-sm bg-emerald-900/10 border border-emerald-700/30 rounded-lg p-4 text-center">
          ✅ لا توجد انتهاكات مفتوحة — النظام آمن
        </div>
      ) : (
        <div className="space-y-3">
          {violations.map(v => (
            <div key={v.id} className={`border rounded-xl p-4 ${v.severity === "critical" || v.severity === "high" ? "bg-red-900/20 border-red-700/30" : "bg-amber-900/20 border-amber-700/30"}`}>
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-semibold text-white">{v.description_ar}</p>
                  <p className="text-xs text-slate-400 mt-1">{v.violation_type} · {v.policy_ref}</p>
                </div>
                <Badge variant={severityVariant(v.severity)}>{v.severity}</Badge>
              </div>
            </div>
          ))}
        </div>
      )}

      {contradictions?.recent && contradictions.recent.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-semibold text-slate-300 mb-3">🔍 تناقضات الوكلاء الأخيرة</h3>
          <div className="space-y-2">
            {contradictions.recent.map((c: Contradiction) => (
              <div key={c.id} className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3 flex items-center justify-between">
                <div>
                  <span className="text-xs text-white">{c.agent_role} · {c.contradiction_type}</span>
                </div>
                <div className="flex gap-2">
                  <Badge variant={severityVariant(c.severity)}>{c.severity}</Badge>
                  <Badge variant={c.status === "open" ? "warning" : "ok"}>{c.status}</Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Surface 6: Connector Health Board ───────────────────────────
function ConnectorHealthBoard() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/connector-health/connectors?tenant_id=${TENANT}`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setConnectors(data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const healthVariant = (s: string) => {
    if (s === "ok") return "ok";
    if (s === "degraded") return "warning";
    if (s === "error") return "critical";
    return "neutral";
  };

  return (
    <div dir="rtl">
      <SectionHeader ar="لوحة صحة الموصلات" en="Connector Health Board" icon="🔌" />
      {loading ? <div className="text-slate-400 text-sm">جار التحميل...</div> : connectors.length === 0 ? (
        <div className="text-slate-500 text-sm bg-slate-800/40 rounded-lg p-6 text-center">
          <p className="text-2xl mb-2">🔌</p>
          <p>لا توجد موصلات مسجلة — سجّل موصلاتك الخارجية أولاً</p>
        </div>
      ) : (
        <div className="space-y-3">
          {connectors.map(c => (
            <div key={c.id || c.connector_key} className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-semibold text-white">{c.display_name_ar}</p>
                  <p className="text-xs text-slate-400 mt-1">{c.vendor} · v{c.api_version}</p>
                </div>
                <Badge variant={healthVariant(c.health_status)}>{c.health_status}</Badge>
              </div>
              {c.last_error && (
                <p className="text-xs text-red-300 mt-2 bg-red-900/20 rounded p-2">{c.last_error}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Surface 7: Saudi Compliance Matrix ──────────────────────────
function SaudiComplianceMatrix() {
  const [controls, setControls] = useState<ComplianceControl[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [framework, setFramework] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    setLoading(true);
    const [ctrls, sum] = await Promise.all([
      fetch(`${API}/api/v1/saudi-compliance/controls?tenant_id=${TENANT}${framework ? `&framework=${framework}` : ""}`).then(r => r.ok ? r.json() : []),
      fetch(`${API}/api/v1/saudi-compliance/summary?tenant_id=${TENANT}`).then(r => r.ok ? r.json() : null),
    ]);
    setControls(ctrls || []);
    setSummary(sum);
    setLoading(false);
  }, [framework]);

  useEffect(() => { loadData(); }, [loadData]);

  const statusVariant = (s: string) => {
    if (s === "implemented" || s === "verified") return "ok";
    if (s === "in_progress") return "warning";
    if (s === "planned") return "active";
    return "neutral";
  };

  const riskVariant = (r: string) => {
    if (r === "critical") return "critical";
    if (r === "high") return "warning";
    return "neutral";
  };

  const frameworks = ["PDPL", "NCA_ECC_2024", "NIST_AI_RMF", "OWASP_LLM_TOP10"];

  return (
    <div dir="rtl">
      <SectionHeader ar="مصفوفة الامتثال السعودي" en="Saudi Compliance Matrix" icon="🇸🇦" />

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <KPICard kpi={{ label_ar: "الضوابط الكلية", value: summary.total_controls, severity: "ok" }} />
          <KPICard kpi={{ label_ar: "مُنفَّذة", value: summary.implemented, severity: "ok" }} />
          <KPICard kpi={{ label_ar: "نسبة الامتثال", value: `${summary.compliance_pct}%`, severity: summary.compliance_pct < 50 ? "critical" : summary.compliance_pct < 80 ? "warning" : "ok" }} />
          <KPICard kpi={{ label_ar: "ثغرات حرجة", value: summary.critical_gaps, severity: summary.critical_gaps > 0 ? "critical" : "ok" }} />
        </div>
      )}

      <div className="flex gap-2 mb-4 overflow-x-auto">
        <button onClick={() => setFramework("")} className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${!framework ? "bg-blue-600 text-white" : "bg-slate-700 text-slate-300 hover:bg-slate-600"}`}>الكل</button>
        {frameworks.map(f => (
          <button key={f} onClick={() => setFramework(f)} className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors whitespace-nowrap ${framework === f ? "bg-blue-600 text-white" : "bg-slate-700 text-slate-300 hover:bg-slate-600"}`}>{f}</button>
        ))}
      </div>

      {loading ? <div className="text-slate-400 text-sm">جار التحميل...</div> : controls.length === 0 ? (
        <div className="text-slate-500 text-sm bg-slate-800/40 rounded-lg p-4 text-center">
          لا توجد ضوابط — قم بتشغيل seed لتحميل الضوابط الكاملة
        </div>
      ) : (
        <div className="space-y-2">
          {controls.map(c => (
            <div key={c.id} className="bg-slate-800/40 border border-slate-700/50 rounded-lg p-3">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-blue-400">{c.control_ref}</span>
                    <Badge variant={riskVariant(c.risk_level)}>{c.risk_level}</Badge>
                  </div>
                  <p className="text-sm text-white">{c.title_ar}</p>
                </div>
                <Badge variant={statusVariant(c.implementation_status)}>{c.implementation_status}</Badge>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Surface 8: Model Routing Dashboard ──────────────────────────
function ModelRoutingDashboard() {
  const [configs, setConfigs] = useState<ModelRoute[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/api/v1/model-routing/configs?tenant_id=${TENANT}`)
      .then(r => r.ok ? r.json() : [])
      .then(data => { setConfigs(data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const laneIcons: Record<string, string> = {
    coding: "💻",
    executive_reasoning: "🧠",
    throughput_drafting: "⚡",
    arabic_nlp: "🇸🇦",
    fallback: "🔄",
  };

  return (
    <div dir="rtl">
      <SectionHeader ar="لوحة توجيه النماذج" en="Model Routing Dashboard" icon="🗺️" />
      {loading ? <div className="text-slate-400 text-sm">جار التحميل...</div> : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {configs.map((c, i) => (
            <div key={i} className={`bg-slate-800/40 border rounded-xl p-4 ${c.is_active ? "border-blue-700/30" : "border-slate-700/50 opacity-60"}`}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span>{laneIcons[c.lane] || "🔀"}</span>
                  <span className="font-semibold text-white text-sm">{c.lane}</span>
                </div>
                <Badge variant={c.is_active ? "ok" : "neutral"}>{c.is_active ? "نشط" : "معطل"}</Badge>
              </div>
              <p className="text-sm text-blue-300 mb-1">{c.primary_model}</p>
              <p className="text-xs text-slate-400 mb-3">{c.provider}</p>
              <div className="flex gap-3 text-xs text-slate-400">
                {c.avg_latency_ms && <span>تأخر: <span className="text-white">{c.avg_latency_ms}ms</span></span>}
                {c.contradiction_rate_pct !== null && c.contradiction_rate_pct !== undefined && (
                  <span>تناقض: <span className={c.contradiction_rate_pct > 5 ? "text-red-300" : "text-emerald-300"}>{c.contradiction_rate_pct}%</span></span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Main Sovereign OS View ───────────────────────────────────────
const SURFACES = [
  { id: "executive", label: "👑 الغرفة التنفيذية", en: "Executive Room", component: ExecutiveRoom },
  { id: "partnership", label: "🤝 الشراكات", en: "Partnership OS", component: PartnershipOS },
  { id: "corpdev", label: "🏢 الاستحواذات", en: "M&A / Corp Dev", component: CorporateDevOS },
  { id: "expansion", label: "🌍 التوسع", en: "Expansion OS", component: ExpansionOS },
  { id: "trust", label: "🔐 طبقة الثقة", en: "Trust Plane", component: TrustPlane },
  { id: "connectors", label: "🔌 الموصلات", en: "Connector Health", component: ConnectorHealthBoard },
  { id: "compliance", label: "🇸🇦 الامتثال", en: "Saudi Compliance", component: SaudiComplianceMatrix },
  { id: "routing", label: "🗺️ توجيه النماذج", en: "Model Routing", component: ModelRoutingDashboard },
];

export function SovereignOSView() {
  const [activeId, setActiveId] = useState("executive");
  const active = SURFACES.find(s => s.id === activeId);
  const ActiveComponent = active?.component;

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900 text-white" dir="rtl">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-950/80 to-purple-950/80 border-b border-slate-800 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-bold">D</div>
          <div>
            <h1 className="text-base font-bold text-white">Dealix Sovereign Enterprise OS</h1>
            <p className="text-xs text-slate-400">نظام تشغيل سيادي مؤسسي · 5 طبقات · Arabic-first · Saudi-ready</p>
          </div>
        </div>
      </div>

      {/* Surface Navigation */}
      <div className="flex gap-2 overflow-x-auto px-6 py-4 border-b border-slate-800 bg-slate-900/50">
        {SURFACES.map(s => (
          <button
            key={s.id}
            onClick={() => setActiveId(s.id)}
            className={`flex-shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              activeId === s.id
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                : "bg-slate-800/60 text-slate-400 hover:text-white hover:bg-slate-700/60"
            }`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Active Surface Content */}
      <div className="px-6 py-8 max-w-6xl mx-auto">
        {ActiveComponent && <ActiveComponent />}
      </div>

      {/* Footer */}
      <div className="text-center py-4 text-xs text-slate-600 border-t border-slate-800">
        Dealix Sovereign Enterprise OS · Decision-native · Execution-durable · Trust-enforced · Arabic-first
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import {
  BarChart3,
  Users,
  Handshake,
  Building,
  Globe2,
  Layers,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Activity,
  Shield,
  FileCheck,
  Loader2,
} from "lucide-react";

interface DashboardData {
  total_recommendations: number;
  pending_approvals: number;
  active_workflows: number;
  active_partners: number;
  ma_pipeline_count: number;
  expansion_markets: number;
  pmi_programs: number;
  policy_violations: number;
  contradiction_alerts: number;
  connector_health: { ok: number; degraded: number; error: number };
  compliance_summary: { total_controls: number; compliant: number; non_compliant: number; in_progress: number };
}

const EMPTY: DashboardData = {
  total_recommendations: 0,
  pending_approvals: 0,
  active_workflows: 0,
  active_partners: 0,
  ma_pipeline_count: 0,
  expansion_markets: 0,
  pmi_programs: 0,
  policy_violations: 0,
  contradiction_alerts: 0,
  connector_health: { ok: 0, degraded: 0, error: 0 },
  compliance_summary: { total_controls: 0, compliant: 0, non_compliant: 0, in_progress: 0 },
};

const summaryCards = (d: DashboardData) => [
  { label: "التوصيات", labelEn: "Recommendations", value: d.total_recommendations, icon: BarChart3, color: "text-blue-500 bg-blue-500/10" },
  { label: "الموافقات المعلقة", labelEn: "Pending Approvals", value: d.pending_approvals, icon: FileCheck, color: "text-amber-500 bg-amber-500/10" },
  { label: "سير العمل النشط", labelEn: "Active Workflows", value: d.active_workflows, icon: Activity, color: "text-emerald-500 bg-emerald-500/10" },
  { label: "الشركاء النشطون", labelEn: "Active Partners", value: d.active_partners, icon: Handshake, color: "text-purple-500 bg-purple-500/10" },
  { label: "خط أنابيب الاستحواذ", labelEn: "M&A Pipeline", value: d.ma_pipeline_count, icon: Building, color: "text-indigo-500 bg-indigo-500/10" },
  { label: "أسواق التوسع", labelEn: "Expansion Markets", value: d.expansion_markets, icon: Globe2, color: "text-cyan-500 bg-cyan-500/10" },
  { label: "برامج التكامل", labelEn: "PMI Programs", value: d.pmi_programs, icon: Layers, color: "text-teal-500 bg-teal-500/10" },
  { label: "انتهاكات السياسات", labelEn: "Policy Violations", value: d.policy_violations, icon: AlertTriangle, color: "text-red-500 bg-red-500/10" },
  { label: "تنبيهات التعارض", labelEn: "Contradiction Alerts", value: d.contradiction_alerts, icon: XCircle, color: "text-orange-500 bg-orange-500/10" },
];

export default function ExecutiveRoomPage() {
  const [data, setData] = useState<DashboardData>(EMPTY);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/executive/dashboard")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => { if (d) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const cards = summaryCards(data);
  const ch = data.connector_health;
  const cs = data.compliance_summary;

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">غرفة القيادة</h1>
        <p className="text-sm text-muted-foreground">Executive Room — لمحة شاملة عن النمو السيادي</p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map((c) => {
          const Icon = c.icon;
          return (
            <div key={c.labelEn} className="bg-card border border-border rounded-2xl p-5 flex items-start gap-4 transition-shadow hover:shadow-lg">
              <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${c.color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{c.value}</p>
                <p className="text-sm font-medium">{c.label}</p>
                <p className="text-[10px] text-muted-foreground">{c.labelEn}</p>
              </div>
            </div>
          );
        })}
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-2xl p-6">
          <h2 className="text-lg font-bold mb-1">صحة الموصلات</h2>
          <p className="text-xs text-muted-foreground mb-4">Connector Health</p>
          <div className="flex gap-4">
            <div className="flex-1 rounded-xl bg-emerald-500/10 border border-emerald-500/20 p-4 text-center">
              <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto mb-1" />
              <p className="text-2xl font-bold text-emerald-500">{ch.ok}</p>
              <p className="text-xs text-muted-foreground">سليم</p>
            </div>
            <div className="flex-1 rounded-xl bg-amber-500/10 border border-amber-500/20 p-4 text-center">
              <AlertTriangle className="w-6 h-6 text-amber-500 mx-auto mb-1" />
              <p className="text-2xl font-bold text-amber-500">{ch.degraded}</p>
              <p className="text-xs text-muted-foreground">متدهور</p>
            </div>
            <div className="flex-1 rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-center">
              <XCircle className="w-6 h-6 text-red-500 mx-auto mb-1" />
              <p className="text-2xl font-bold text-red-500">{ch.error}</p>
              <p className="text-xs text-muted-foreground">خطأ</p>
            </div>
          </div>
        </div>

        <div className="bg-card border border-border rounded-2xl p-6">
          <h2 className="text-lg font-bold mb-1">ملخص الامتثال</h2>
          <p className="text-xs text-muted-foreground mb-4">Compliance Summary</p>
          <div className="space-y-3">
            {[
              { label: "إجمالي الضوابط", value: cs.total_controls, color: "bg-blue-500" },
              { label: "ممتثل", value: cs.compliant, color: "bg-emerald-500" },
              { label: "غير ممتثل", value: cs.non_compliant, color: "bg-red-500" },
              { label: "قيد التنفيذ", value: cs.in_progress, color: "bg-amber-500" },
            ].map((row) => (
              <div key={row.label} className="flex items-center gap-3">
                <div className={`w-2.5 h-2.5 rounded-full ${row.color}`} />
                <span className="text-sm flex-1">{row.label}</span>
                <span className="text-sm font-bold">{row.value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {data.total_recommendations === 0 && data.pending_approvals === 0 && (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Shield className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد بيانات بعد</p>
          <p className="text-sm text-muted-foreground/70">No data yet — the system will populate as modules are activated</p>
        </div>
      )}
    </div>
  );
}

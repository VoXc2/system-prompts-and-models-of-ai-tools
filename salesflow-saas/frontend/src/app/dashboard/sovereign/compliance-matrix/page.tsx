"use client";

import { useEffect, useState } from "react";
import { Shield, Loader2, CheckCircle2, XCircle, Clock, AlertTriangle } from "lucide-react";

interface ComplianceControl {
  id: string;
  framework: string;
  control_id: string;
  control_name: string;
  status: string;
  evidence_status: string;
  last_assessed: string;
  owner: string;
  notes: string;
}

interface ComplianceData {
  frameworks: FrameworkSummary[];
  controls: ComplianceControl[];
}

interface FrameworkSummary {
  name: string;
  total: number;
  compliant: number;
  non_compliant: number;
  in_progress: number;
}

const FRAMEWORKS = [
  { key: "PDPL", label: "نظام حماية البيانات الشخصية", labelEn: "PDPL" },
  { key: "ECC-2024", label: "ضوابط الأمن السيبراني الأساسية", labelEn: "ECC-2024" },
  { key: "NIST-AI-RMF", label: "إطار إدارة مخاطر الذكاء الاصطناعي", labelEn: "NIST AI RMF" },
  { key: "OWASP-LLM", label: "أمان نماذج اللغة الكبيرة", labelEn: "OWASP LLM Top 10" },
];

const STATUS_CFG: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  compliant: { icon: CheckCircle2, color: "text-emerald-500", label: "ممتثل" },
  non_compliant: { icon: XCircle, color: "text-red-500", label: "غير ممتثل" },
  in_progress: { icon: Clock, color: "text-amber-500", label: "قيد التنفيذ" },
  not_assessed: { icon: AlertTriangle, color: "text-gray-400", label: "لم يُقيَّم" },
};

export default function ComplianceMatrixPage() {
  const [data, setData] = useState<ComplianceData>({ frameworks: [], controls: [] });
  const [loading, setLoading] = useState(true);
  const [activeFramework, setActiveFramework] = useState("all");

  useEffect(() => {
    fetch("/api/v1/sovereign/trust/compliance-matrix")
      .then((r) => (r.ok ? r.json() : { frameworks: [], controls: [] }))
      .then((d) => {
        if (d && d.frameworks) setData(d);
        else if (Array.isArray(d)) setData({ frameworks: [], controls: d });
      })
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

  const controls =
    activeFramework === "all"
      ? data.controls
      : data.controls.filter((c) => c.framework === activeFramework);

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">مصفوفة الامتثال السعودي</h1>
        <p className="text-sm text-muted-foreground">Saudi Compliance Matrix — متابعة الأطر التنظيمية</p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {FRAMEWORKS.map((fw) => {
          const summary = data.frameworks.find((f) => f.name === fw.key);
          const compliantPct = summary && summary.total > 0 ? Math.round((summary.compliant / summary.total) * 100) : 0;
          return (
            <button
              key={fw.key}
              type="button"
              onClick={() => setActiveFramework(activeFramework === fw.key ? "all" : fw.key)}
              className={`bg-card border rounded-2xl p-5 text-right transition-all hover:shadow-lg ${
                activeFramework === fw.key ? "border-primary/50 ring-1 ring-primary/20" : "border-border"
              }`}
            >
              <h3 className="text-sm font-bold mb-1">{fw.label}</h3>
              <p className="text-[10px] text-muted-foreground mb-3">{fw.labelEn}</p>
              {summary ? (
                <>
                  <div className="flex items-center gap-2 mb-2">
                    <div className="flex-1 bg-muted rounded-full h-2">
                      <div
                        className="bg-emerald-500 rounded-full h-2 transition-all"
                        style={{ width: `${compliantPct}%` }}
                      />
                    </div>
                    <span className="text-xs font-bold">{compliantPct}%</span>
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                    <span className="text-emerald-500">{summary.compliant} ممتثل</span>
                    <span className="text-red-500">{summary.non_compliant} غير ممتثل</span>
                    <span className="text-amber-500">{summary.in_progress} جارٍ</span>
                  </div>
                </>
              ) : (
                <p className="text-xs text-muted-foreground">لا توجد بيانات</p>
              )}
            </button>
          );
        })}
      </section>

      {controls.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Shield className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد ضوابط امتثال بعد</p>
          <p className="text-sm text-muted-foreground/70">No compliance controls yet</p>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الإطار</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">رمز الضابط</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الضابط</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الحالة</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المسؤول</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">آخر تقييم</th>
              </tr>
            </thead>
            <tbody>
              {controls.map((ctrl) => {
                const cfg = STATUS_CFG[ctrl.status] || STATUS_CFG.not_assessed;
                const Icon = cfg.icon;
                return (
                  <tr key={ctrl.id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                    <td className="px-5 py-4 text-xs font-medium">{ctrl.framework}</td>
                    <td className="px-5 py-4 text-xs font-mono text-muted-foreground">{ctrl.control_id}</td>
                    <td className="px-5 py-4 text-xs">{ctrl.control_name}</td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-1.5">
                        <Icon className={`w-4 h-4 ${cfg.color}`} />
                        <span className={`text-[10px] font-bold ${cfg.color}`}>{cfg.label}</span>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">{ctrl.owner}</td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">
                      {new Date(ctrl.last_assessed).toLocaleDateString("ar-SA")}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

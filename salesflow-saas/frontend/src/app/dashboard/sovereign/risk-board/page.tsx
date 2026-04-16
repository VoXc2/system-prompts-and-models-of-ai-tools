"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Loader2, ShieldAlert } from "lucide-react";

interface RiskItem {
  id: string;
  title: string;
  source: string;
  severity: "low" | "medium" | "high" | "critical";
  category: string;
  description: string;
  owner: string;
  created_at: string;
}

const SEVERITY_CONFIG: Record<string, { bg: string; text: string; border: string; label: string }> = {
  low: { bg: "bg-emerald-500/10", text: "text-emerald-500", border: "border-emerald-500/20", label: "منخفض" },
  medium: { bg: "bg-amber-500/10", text: "text-amber-500", border: "border-amber-500/20", label: "متوسط" },
  high: { bg: "bg-orange-500/10", text: "text-orange-500", border: "border-orange-500/20", label: "مرتفع" },
  critical: { bg: "bg-red-500/10", text: "text-red-500", border: "border-red-500/20", label: "حرج" },
};

const SOURCE_LABELS: Record<string, string> = {
  ma: "الاستحواذ",
  expansion: "التوسع",
  pmi: "التكامل",
  compliance: "الامتثال",
  partnership: "الشراكات",
};

export default function RiskBoardPage() {
  const [items, setItems] = useState<RiskItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/executive/risk-board")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setItems(Array.isArray(d) ? d : d.items || []))
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

  const bySeverity = (severity: string) => items.filter((i) => i.severity === severity);

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">لوحة المخاطر</h1>
        <p className="text-sm text-muted-foreground">Risk Board — خريطة المخاطر الحرارية عبر جميع المسارات</p>
      </header>

      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {(["critical", "high", "medium", "low"] as const).map((sev) => {
          const cfg = SEVERITY_CONFIG[sev];
          const count = bySeverity(sev).length;
          return (
            <div key={sev} className={`rounded-2xl border p-5 text-center ${cfg.bg} ${cfg.border}`}>
              <p className={`text-3xl font-bold ${cfg.text}`}>{count}</p>
              <p className={`text-sm font-medium ${cfg.text}`}>{cfg.label}</p>
            </div>
          );
        })}
      </section>

      {items.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <ShieldAlert className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد مخاطر مسجلة</p>
          <p className="text-sm text-muted-foreground/70">No risks recorded yet</p>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المخاطرة</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المصدر</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الخطورة</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المسؤول</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">التاريخ</th>
              </tr>
            </thead>
            <tbody>
              {items.map((risk) => {
                const cfg = SEVERITY_CONFIG[risk.severity] || SEVERITY_CONFIG.medium;
                return (
                  <tr key={risk.id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className={`w-4 h-4 shrink-0 ${cfg.text}`} />
                        <div>
                          <p className="font-medium">{risk.title}</p>
                          <p className="text-xs text-muted-foreground line-clamp-1">{risk.description}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-xs">{SOURCE_LABELS[risk.source] || risk.source}</td>
                    <td className="px-5 py-4">
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold border ${cfg.bg} ${cfg.text} ${cfg.border}`}>
                        {cfg.label}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-xs">{risk.owner}</td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">
                      {new Date(risk.created_at).toLocaleDateString("ar-SA")}
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

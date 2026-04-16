"use client";

import { useEffect, useState } from "react";
import { ShieldX, Loader2, AlertOctagon } from "lucide-react";

interface Violation {
  id: string;
  policy_name: string;
  action: string;
  severity: string;
  denied_at: string;
  reason: string;
  actor: string;
  module: string;
}

const SEVERITY_BADGE: Record<string, { class: string; label: string }> = {
  critical: { class: "bg-red-500/10 text-red-500 border-red-500/20", label: "حرج" },
  high: { class: "bg-orange-500/10 text-orange-500 border-orange-500/20", label: "مرتفع" },
  medium: { class: "bg-amber-500/10 text-amber-500 border-amber-500/20", label: "متوسط" },
  low: { class: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20", label: "منخفض" },
};

export default function PolicyViolationsPage() {
  const [items, setItems] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/trust/violations")
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

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">انتهاكات السياسات</h1>
        <p className="text-sm text-muted-foreground">Policy Violations — تقييمات السياسات المرفوضة</p>
      </header>

      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {(["critical", "high", "medium", "low"] as const).map((sev) => {
          const count = items.filter((i) => i.severity === sev).length;
          const badge = SEVERITY_BADGE[sev];
          return (
            <div key={sev} className={`rounded-2xl border p-4 text-center ${badge.class.replace("text-", "").split(" ")[0]} border-${sev === "critical" ? "red" : sev === "high" ? "orange" : sev === "medium" ? "amber" : "emerald"}-500/20`}>
              <p className={`text-2xl font-bold ${badge.class.split(" ")[1]}`}>{count}</p>
              <p className="text-xs text-muted-foreground">{badge.label}</p>
            </div>
          );
        })}
      </section>

      {items.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <ShieldX className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد انتهاكات مسجلة</p>
          <p className="text-sm text-muted-foreground/70">No policy violations recorded</p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((v) => {
            const badge = SEVERITY_BADGE[v.severity] || SEVERITY_BADGE.medium;
            return (
              <div key={v.id} className="bg-card border border-border rounded-2xl p-5">
                <div className="flex items-start gap-3">
                  <AlertOctagon className={`w-5 h-5 shrink-0 mt-0.5 ${badge.class.split(" ")[1]}`} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="font-bold text-sm">{v.policy_name}</span>
                      <span className={`inline-flex px-2 py-0.5 rounded-full text-[10px] font-bold border ${badge.class}`}>
                        {badge.label}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">{v.reason}</p>
                    <div className="flex items-center gap-3 text-[10px] text-muted-foreground">
                      <span>الإجراء: {v.action}</span>
                      <span>•</span>
                      <span>المنفذ: {v.actor}</span>
                      <span>•</span>
                      <span>الوحدة: {v.module}</span>
                      <span>•</span>
                      <span>{new Date(v.denied_at).toLocaleDateString("ar-SA")}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

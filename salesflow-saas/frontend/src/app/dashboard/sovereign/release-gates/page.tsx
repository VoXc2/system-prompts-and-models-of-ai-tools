"use client";

import { useEffect, useState } from "react";
import { Rocket, Loader2, CheckCircle2, XCircle, Clock, ChevronDown } from "lucide-react";

interface ReleaseGate {
  id: string;
  release_name: string;
  version: string;
  status: string;
  environment: string;
  created_at: string;
  checklist: GateCheck[];
  overall_ready: boolean;
}

interface GateCheck {
  id: string;
  name: string;
  category: string;
  status: string;
  details: string;
}

const GATE_STATUS: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  passed: { icon: CheckCircle2, color: "text-emerald-500", label: "نجح" },
  failed: { icon: XCircle, color: "text-red-500", label: "فشل" },
  pending: { icon: Clock, color: "text-amber-500", label: "قيد الانتظار" },
  skipped: { icon: Clock, color: "text-gray-400", label: "تم التخطي" },
};

const ENV_BADGE: Record<string, string> = {
  staging: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  production: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
  canary: "bg-amber-500/10 text-amber-500 border-amber-500/20",
};

export default function ReleaseGatesPage() {
  const [gates, setGates] = useState<ReleaseGate[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/v1/sovereign/operating/release-gates")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setGates(Array.isArray(d) ? d : d.items || []))
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
        <h1 className="text-2xl font-bold text-foreground">بوابات الإصدار</h1>
        <p className="text-sm text-muted-foreground">Release Gates — قائمة الجاهزية ومؤشرات الإصدار</p>
      </header>

      {gates.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Rocket className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد بوابات إصدار بعد</p>
          <p className="text-sm text-muted-foreground/70">No release gates yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {gates.map((gate) => {
            const isExpanded = expanded === gate.id;
            const passedCount = gate.checklist.filter((c) => c.status === "passed").length;
            const totalChecks = gate.checklist.length;

            return (
              <div key={gate.id} className="bg-card border border-border rounded-2xl overflow-hidden">
                <button
                  type="button"
                  onClick={() => setExpanded(isExpanded ? null : gate.id)}
                  className="w-full p-6 text-right"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                    <div className="flex items-center gap-3">
                      {gate.overall_ready ? (
                        <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                          <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                        </div>
                      ) : (
                        <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
                          <Clock className="w-5 h-5 text-amber-500" />
                        </div>
                      )}
                      <div>
                        <h3 className="font-bold text-sm">{gate.release_name}</h3>
                        <p className="text-[10px] text-muted-foreground">v{gate.version}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 sm:mr-auto">
                      <span className={`inline-flex px-2.5 py-1 rounded-full text-[10px] font-bold border ${ENV_BADGE[gate.environment] || ENV_BADGE.staging}`}>
                        {gate.environment}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {passedCount}/{totalChecks} فحص ناجح
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-muted rounded-full h-2">
                        <div
                          className={`rounded-full h-2 transition-all ${
                            gate.overall_ready ? "bg-emerald-500" : "bg-amber-500"
                          }`}
                          style={{ width: `${totalChecks > 0 ? (passedCount / totalChecks) * 100 : 0}%` }}
                        />
                      </div>
                      <ChevronDown
                        className={`w-4 h-4 text-muted-foreground transition-transform ${
                          isExpanded ? "rotate-180" : ""
                        }`}
                      />
                    </div>
                  </div>
                </button>

                {isExpanded && gate.checklist.length > 0 && (
                  <div className="border-t border-border px-6 py-4 space-y-2">
                    {gate.checklist.map((check) => {
                      const cfg = GATE_STATUS[check.status] || GATE_STATUS.pending;
                      const Icon = cfg.icon;
                      return (
                        <div key={check.id} className="flex items-center gap-3 py-2 border-b border-border/30 last:border-0">
                          <Icon className={`w-4 h-4 shrink-0 ${cfg.color}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-medium">{check.name}</p>
                            <p className="text-[10px] text-muted-foreground">{check.details}</p>
                          </div>
                          <span className="text-[10px] text-muted-foreground">{check.category}</span>
                          <span className={`text-[10px] font-bold ${cfg.color}`}>{cfg.label}</span>
                        </div>
                      );
                    })}
                  </div>
                )}

                <div className="px-6 py-3 bg-muted/20 border-t border-border/50 text-[10px] text-muted-foreground">
                  {new Date(gate.created_at).toLocaleString("ar-SA")}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

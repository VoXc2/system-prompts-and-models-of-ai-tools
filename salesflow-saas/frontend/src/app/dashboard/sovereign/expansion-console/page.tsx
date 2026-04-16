"use client";

import { useEffect, useState } from "react";
import { Globe2, Loader2, MapPin, CheckCircle2, Clock, AlertTriangle } from "lucide-react";

interface Market {
  id: string;
  name: string;
  country: string;
  status: string;
  readiness_score: number;
  launch_date: string | null;
  regulatory_status: string;
  team_assigned: boolean;
  budget_allocated: boolean;
  infrastructure_ready: boolean;
}

const STATUS_BADGE: Record<string, { class: string; label: string }> = {
  planning: { class: "bg-gray-500/10 text-gray-400 border-gray-500/20", label: "تخطيط" },
  preparing: { class: "bg-blue-500/10 text-blue-500 border-blue-500/20", label: "تجهيز" },
  launching: { class: "bg-amber-500/10 text-amber-500 border-amber-500/20", label: "إطلاق" },
  active: { class: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20", label: "نشط" },
  on_hold: { class: "bg-orange-500/10 text-orange-500 border-orange-500/20", label: "متوقف" },
};

export default function ExpansionConsolePage() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/expansion/launch-console")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setMarkets(Array.isArray(d) ? d : d.items || []))
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

  const ReadinessIndicator = ({ ready, label }: { ready: boolean; label: string }) => (
    <div className="flex items-center gap-1.5">
      {ready ? (
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
      ) : (
        <Clock className="w-3.5 h-3.5 text-amber-500" />
      )}
      <span className="text-[10px]">{label}</span>
    </div>
  );

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">وحدة التحكم بالتوسع</h1>
        <p className="text-sm text-muted-foreground">Expansion Console — متابعة الأسواق وجاهزية الإطلاق</p>
      </header>

      {markets.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Globe2 className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد أسواق توسع بعد</p>
          <p className="text-sm text-muted-foreground/70">No expansion markets yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {markets.map((m) => {
            const badge = STATUS_BADGE[m.status] || STATUS_BADGE.planning;
            const readinessColor =
              m.readiness_score >= 80
                ? "text-emerald-500"
                : m.readiness_score >= 50
                  ? "text-amber-500"
                  : "text-red-500";

            return (
              <div key={m.id} className="bg-card border border-border rounded-2xl p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center">
                      <MapPin className="w-5 h-5 text-cyan-500" />
                    </div>
                    <div>
                      <h3 className="font-bold text-sm">{m.name}</h3>
                      <p className="text-[10px] text-muted-foreground">{m.country}</p>
                    </div>
                  </div>
                  <span className={`inline-flex px-2.5 py-1 rounded-full text-[10px] font-bold border ${badge.class}`}>
                    {badge.label}
                  </span>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-xs text-muted-foreground">جاهزية الإطلاق</p>
                    <p className="text-[10px] text-muted-foreground">Launch Readiness</p>
                  </div>
                  <span className={`text-2xl font-bold ${readinessColor}`}>{m.readiness_score}%</span>
                </div>

                <div className="w-full bg-muted rounded-full h-2 mb-4">
                  <div
                    className={`rounded-full h-2 transition-all ${
                      m.readiness_score >= 80
                        ? "bg-emerald-500"
                        : m.readiness_score >= 50
                          ? "bg-amber-500"
                          : "bg-red-500"
                    }`}
                    style={{ width: `${m.readiness_score}%` }}
                  />
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <ReadinessIndicator ready={m.team_assigned} label="الفريق" />
                  <ReadinessIndicator ready={m.budget_allocated} label="الميزانية" />
                  <ReadinessIndicator ready={m.infrastructure_ready} label="البنية التحتية" />
                </div>

                {m.launch_date && (
                  <p className="text-[10px] text-muted-foreground mt-3">
                    تاريخ الإطلاق: {new Date(m.launch_date).toLocaleDateString("ar-SA")}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

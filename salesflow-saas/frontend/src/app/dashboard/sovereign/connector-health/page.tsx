"use client";

import { useEffect, useState } from "react";
import { Plug, Loader2, CheckCircle2, AlertTriangle, XCircle, RefreshCw } from "lucide-react";

interface Connector {
  id: string;
  name: string;
  type: string;
  status: "ok" | "degraded" | "error";
  last_sync: string;
  latency_ms: number;
  uptime_pct: number;
  error_message: string | null;
}

const STATUS_CONFIG: Record<string, { icon: typeof CheckCircle2; color: string; bg: string; border: string; label: string }> = {
  ok: { icon: CheckCircle2, color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/20", label: "سليم" },
  degraded: { icon: AlertTriangle, color: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/20", label: "متدهور" },
  error: { icon: XCircle, color: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/20", label: "خطأ" },
};

export default function ConnectorHealthPage() {
  const [connectors, setConnectors] = useState<Connector[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/connectors/health-board")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setConnectors(Array.isArray(d) ? d : d.items || []))
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

  const okCount = connectors.filter((c) => c.status === "ok").length;
  const degradedCount = connectors.filter((c) => c.status === "degraded").length;
  const errorCount = connectors.filter((c) => c.status === "error").length;

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">صحة الموصلات</h1>
        <p className="text-sm text-muted-foreground">Connector Health — حالة جميع الموصلات والتكاملات</p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-2xl p-5 text-center">
          <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto mb-1" />
          <p className="text-2xl font-bold text-emerald-500">{okCount}</p>
          <p className="text-xs text-muted-foreground">سليم</p>
        </div>
        <div className="bg-amber-500/10 border border-amber-500/20 rounded-2xl p-5 text-center">
          <AlertTriangle className="w-6 h-6 text-amber-500 mx-auto mb-1" />
          <p className="text-2xl font-bold text-amber-500">{degradedCount}</p>
          <p className="text-xs text-muted-foreground">متدهور</p>
        </div>
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-5 text-center">
          <XCircle className="w-6 h-6 text-red-500 mx-auto mb-1" />
          <p className="text-2xl font-bold text-red-500">{errorCount}</p>
          <p className="text-xs text-muted-foreground">خطأ</p>
        </div>
      </section>

      {connectors.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Plug className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد موصلات مسجلة</p>
          <p className="text-sm text-muted-foreground/70">No connectors registered yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {connectors.map((c) => {
            const cfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.error;
            const Icon = cfg.icon;
            return (
              <div key={c.id} className={`bg-card border rounded-2xl p-5 hover:shadow-lg transition-shadow ${cfg.border}`}>
                <div className="flex items-start justify-between mb-3">
                  <div className={`w-10 h-10 rounded-xl ${cfg.bg} flex items-center justify-center`}>
                    <Plug className={`w-5 h-5 ${cfg.color}`} />
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Icon className={`w-4 h-4 ${cfg.color}`} />
                    <span className={`text-[10px] font-bold ${cfg.color}`}>{cfg.label}</span>
                  </div>
                </div>

                <h3 className="font-bold text-sm mb-1">{c.name}</h3>
                <p className="text-[10px] text-muted-foreground mb-3">{c.type}</p>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">زمن الاستجابة</span>
                    <span className="font-mono">{c.latency_ms}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">وقت التشغيل</span>
                    <span className="font-mono">{c.uptime_pct}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">آخر مزامنة</span>
                    <span className="flex items-center gap-1 text-[10px]">
                      <RefreshCw className="w-3 h-3" />
                      {new Date(c.last_sync).toLocaleString("ar-SA")}
                    </span>
                  </div>
                </div>

                {c.error_message && (
                  <div className="mt-3 p-2 bg-red-500/5 border border-red-500/10 rounded-lg">
                    <p className="text-[10px] text-red-500">{c.error_message}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

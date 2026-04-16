"use client";

import { useEffect, useState } from "react";
import { Brain, Loader2, Zap, Clock, CheckCircle2 } from "lucide-react";

interface ModelLane {
  id: string;
  lane_name: string;
  model_provider: string;
  model_name: string;
  task_type: string;
  total_requests: number;
  avg_latency_ms: number;
  success_rate_pct: number;
  avg_tokens_in: number;
  avg_tokens_out: number;
  cost_per_1k_tokens: number;
  status: string;
}

const STATUS_CONFIG: Record<string, { color: string; label: string }> = {
  active: { color: "text-emerald-500", label: "نشط" },
  standby: { color: "text-amber-500", label: "احتياط" },
  disabled: { color: "text-gray-400", label: "معطل" },
  error: { color: "text-red-500", label: "خطأ" },
};

export default function ModelRoutingPage() {
  const [lanes, setLanes] = useState<ModelLane[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/decision/model-routing-dashboard")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setLanes(Array.isArray(d) ? d : d.items || []))
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

  const totalRequests = lanes.reduce((s, l) => s + l.total_requests, 0);
  const avgLatency = lanes.length > 0 ? Math.round(lanes.reduce((s, l) => s + l.avg_latency_ms, 0) / lanes.length) : 0;
  const avgSuccess = lanes.length > 0 ? (lanes.reduce((s, l) => s + l.success_rate_pct, 0) / lanes.length).toFixed(1) : "0";

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">لوحة توجيه النماذج</h1>
        <p className="text-sm text-muted-foreground">Model Routing Dashboard — أداء مسارات توجيه نماذج الذكاء الاصطناعي</p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-2xl p-5 flex items-start gap-4">
          <div className="w-11 h-11 rounded-xl bg-blue-500/10 flex items-center justify-center">
            <Zap className="w-5 h-5 text-blue-500" />
          </div>
          <div>
            <p className="text-2xl font-bold">{totalRequests.toLocaleString("ar-SA")}</p>
            <p className="text-xs text-muted-foreground">إجمالي الطلبات</p>
            <p className="text-[10px] text-muted-foreground">Total Requests</p>
          </div>
        </div>
        <div className="bg-card border border-border rounded-2xl p-5 flex items-start gap-4">
          <div className="w-11 h-11 rounded-xl bg-amber-500/10 flex items-center justify-center">
            <Clock className="w-5 h-5 text-amber-500" />
          </div>
          <div>
            <p className="text-2xl font-bold">{avgLatency}ms</p>
            <p className="text-xs text-muted-foreground">متوسط زمن الاستجابة</p>
            <p className="text-[10px] text-muted-foreground">Avg Latency</p>
          </div>
        </div>
        <div className="bg-card border border-border rounded-2xl p-5 flex items-start gap-4">
          <div className="w-11 h-11 rounded-xl bg-emerald-500/10 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5 text-emerald-500" />
          </div>
          <div>
            <p className="text-2xl font-bold">{avgSuccess}%</p>
            <p className="text-xs text-muted-foreground">معدل النجاح</p>
            <p className="text-[10px] text-muted-foreground">Success Rate</p>
          </div>
        </div>
      </section>

      {lanes.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Brain className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد مسارات توجيه بعد</p>
          <p className="text-sm text-muted-foreground/70">No model routing lanes configured yet</p>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المسار</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المزود</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">النموذج</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المهمة</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الطلبات</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الاستجابة</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">النجاح</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الحالة</th>
              </tr>
            </thead>
            <tbody>
              {lanes.map((lane) => {
                const status = STATUS_CONFIG[lane.status] || STATUS_CONFIG.active;
                const successColor =
                  lane.success_rate_pct >= 95
                    ? "text-emerald-500"
                    : lane.success_rate_pct >= 80
                      ? "text-amber-500"
                      : "text-red-500";
                return (
                  <tr key={lane.id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                    <td className="px-5 py-4 text-xs font-medium">{lane.lane_name}</td>
                    <td className="px-5 py-4 text-xs">{lane.model_provider}</td>
                    <td className="px-5 py-4 text-xs font-mono">{lane.model_name}</td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">{lane.task_type}</td>
                    <td className="px-5 py-4 text-xs font-mono">{lane.total_requests.toLocaleString("ar-SA")}</td>
                    <td className="px-5 py-4 text-xs font-mono">{lane.avg_latency_ms}ms</td>
                    <td className="px-5 py-4">
                      <span className={`text-xs font-bold ${successColor}`}>{lane.success_rate_pct}%</span>
                    </td>
                    <td className="px-5 py-4">
                      <span className={`text-[10px] font-bold ${status.color}`}>{status.label}</span>
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

"use client";

import { useEffect, useState } from "react";
import { Wrench, Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";

interface ToolVerification {
  id: string;
  tool_name: string;
  action: string;
  status: string;
  executed_at: string;
  duration_ms: number;
  input_hash: string;
  output_hash: string;
  verified: boolean;
  error_message: string | null;
}

const STATUS_ICON: Record<string, { icon: typeof CheckCircle2; color: string; label: string }> = {
  success: { icon: CheckCircle2, color: "text-emerald-500", label: "ناجح" },
  failure: { icon: XCircle, color: "text-red-500", label: "فشل" },
  running: { icon: Clock, color: "text-amber-500", label: "جارٍ" },
};

export default function ToolLedgerPage() {
  const [items, setItems] = useState<ToolVerification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/trust/tool-verifications")
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

  const successCount = items.filter((i) => i.status === "success").length;
  const failureCount = items.filter((i) => i.status === "failure").length;

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">سجل التحقق من الأدوات</h1>
        <p className="text-sm text-muted-foreground">Tool Verification Ledger — سجل تنفيذ الأدوات والتحقق</p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-2xl p-5 text-center">
          <p className="text-2xl font-bold">{items.length}</p>
          <p className="text-xs text-muted-foreground">إجمالي التنفيذات</p>
          <p className="text-[10px] text-muted-foreground">Total Executions</p>
        </div>
        <div className="bg-card border border-border rounded-2xl p-5 text-center">
          <p className="text-2xl font-bold text-emerald-500">{successCount}</p>
          <p className="text-xs text-muted-foreground">ناجح</p>
          <p className="text-[10px] text-muted-foreground">Successful</p>
        </div>
        <div className="bg-card border border-border rounded-2xl p-5 text-center">
          <p className="text-2xl font-bold text-red-500">{failureCount}</p>
          <p className="text-xs text-muted-foreground">فشل</p>
          <p className="text-[10px] text-muted-foreground">Failed</p>
        </div>
      </section>

      {items.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Wrench className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد عمليات تحقق بعد</p>
          <p className="text-sm text-muted-foreground/70">No tool verifications yet</p>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الحالة</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الأداة</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الإجراء</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">المدة</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">التحقق</th>
                <th className="text-right px-5 py-3 font-bold text-xs text-muted-foreground">الوقت</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const cfg = STATUS_ICON[item.status] || STATUS_ICON.running;
                const Icon = cfg.icon;
                return (
                  <tr key={item.id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <Icon className={`w-4 h-4 ${cfg.color}`} />
                        <span className="text-xs">{cfg.label}</span>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-xs font-medium">{item.tool_name}</td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">{item.action}</td>
                    <td className="px-5 py-4 text-xs font-mono">{item.duration_ms}ms</td>
                    <td className="px-5 py-4">
                      {item.verified ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-500" />
                      )}
                    </td>
                    <td className="px-5 py-4 text-xs text-muted-foreground">
                      {new Date(item.executed_at).toLocaleString("ar-SA")}
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

"use client";

import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Building2,
  CheckCircle2,
  ClipboardList,
  Cpu,
  GitBranch,
  Handshake,
  Layers,
  LineChart,
  Loader2,
  RefreshCw,
  Scale,
  Shield,
} from "lucide-react";
import { apiFetch } from "@/lib/api-client";

type PlaneHealth = {
  plane: string;
  status: string;
  signals: string[];
};

type SalesOsSignals = {
  total_leads: number;
  new_leads_today: number;
  total_deals: number;
  open_deals_value_sar: string;
  closed_won_value_sar: string;
  closed_won_count: number;
  messages_sent_today: number;
  conversion_rate_pct: number;
  active_workflows: number;
  upcoming_meetings_7d: number;
  proposals_draft: number;
  proposals_pending_send: number;
};

type PipelineBoard = {
  title: string;
  title_ar: string;
  total: number;
  by_stage: Record<string, number>;
  items: Array<Record<string, unknown>>;
};

type RiskHeatmap = {
  score_0_100: number;
  drivers: string[];
};

type ComplianceRow = {
  control_id: string;
  domain: string;
  status: string;
  evidence_hint: string;
  evidence_hint_ar: string;
};

type ModelRouteRow = {
  task_type: string;
  model_slot: string;
};

type ToolLedgerRow = {
  tool_id: string;
  last_verified_at: string | null;
  status: string;
  connector_version: string | null;
};

type SovereignSnapshot = {
  generated_at: string;
  tenant_id: string;
  correlation_id: string | null;
  planes: PlaneHealth[];
  sales_os: SalesOsSignals;
  partnership: PipelineBoard;
  ma_corp_dev: PipelineBoard;
  expansion: PipelineBoard;
  pmi_pmo: PipelineBoard;
  executive: {
    headline?: string;
    headline_ar?: string;
    next_best_actions?: Array<{
      id: string;
      title: string;
      title_ar: string;
      priority: string;
    }>;
    actual_vs_forecast?: {
      currency: string;
      actual_closed_won_sar: number;
      forecast_hint?: string;
    };
    escalations_open_hint?: number;
  };
  approvals_pending: number;
  policy_violations_open: number;
  risk: RiskHeatmap;
  compliance_matrix: ComplianceRow[];
  model_routing_fabric: ModelRouteRow[];
  tool_verification_ledger: ToolLedgerRow[];
  release_gate: {
    environment: string;
    rulesets_required: boolean;
    oidc_preferred: boolean;
    last_gate_check_at: string | null;
  };
};

function formatSar(value: string | number) {
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return "—";
  return new Intl.NumberFormat("ar-SA", { maximumFractionDigits: 0 }).format(n);
}

function planeLabelAr(plane: string) {
  const m: Record<string, string> = {
    decision: "مستوى القرار",
    execution: "مستوى التنفيذ",
    trust: "مستوى الثقة",
    data: "مستوى البيانات",
    operating: "مستوى التشغيل",
  };
  return m[plane] ?? plane;
}

function PipelineMini({ board }: { board: PipelineBoard }) {
  const stages = Object.entries(board.by_stage).slice(0, 6);
  return (
    <div className="rounded-2xl border border-border/60 bg-card/40 p-4 space-y-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs text-muted-foreground">{board.title}</p>
          <p className="text-sm font-semibold">{board.title_ar}</p>
        </div>
        <span className="text-xs font-mono rounded-full bg-secondary px-2 py-0.5">{board.total}</span>
      </div>
      {stages.length === 0 ? (
        <p className="text-xs text-muted-foreground">لا صفقات استراتيجية بعد — اربط الاكتشاف والمطابقة هنا.</p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {stages.map(([k, v]) => (
            <span key={k} className="text-[11px] rounded-lg border border-border/50 px-2 py-0.5 bg-background/50">
              {k}: {v}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export function SovereignOsView() {
  const [data, setData] = useState<SovereignSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setErr(null);
    const cid =
      typeof crypto !== "undefined" && "randomUUID" in crypto
        ? crypto.randomUUID()
        : `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const res = await apiFetch("/api/v1/sovereign-os/snapshot", {
      headers: { "X-Correlation-ID": cid },
    });
    if (!res.ok) {
      setErr(`تعذر تحميل لقطة النظام (${res.status})`);
      setData(null);
      setLoading(false);
      return;
    }
    setData((await res.json()) as SovereignSnapshot);
    setLoading(false);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[320px] gap-3 text-muted-foreground">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="text-sm">جاري تحميل مركز القيادة السيادي…</p>
      </div>
    );
  }

  if (err || !data) {
    return (
      <div className="rounded-2xl border border-destructive/40 bg-destructive/5 p-6 text-center space-y-3">
        <p className="text-sm text-destructive">{err || "خطأ غير متوقع"}</p>
        <button
          type="button"
          onClick={() => void load()}
          className="inline-flex items-center gap-2 rounded-xl border border-border px-4 py-2 text-sm hover:bg-secondary/60"
        >
          <RefreshCw className="w-4 h-4" />
          إعادة المحاولة
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 p-6 lg:p-10" dir="rtl">
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-primary/80 font-semibold">Dealix Sovereign OS</p>
          <h1 className="text-2xl lg:text-3xl font-bold mt-1">{data.executive.headline_ar ?? "مركز القيادة السيادي"}</h1>
          <p className="text-sm text-muted-foreground mt-2 max-w-2xl">
            لقطة JSON مُهيكلة للإيرادات والشراكات والاستحواذ والتوسع وما بعد الإغلاق، مع موافقات ومخاطر وحوكمة
            ومسار النماذج — وليس مجرد محادثة.
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs text-muted-foreground font-mono">
          <span className="rounded-lg border border-border px-2 py-1">trace: {data.correlation_id?.slice(0, 8) ?? "—"}…</span>
          <span className="rounded-lg border border-border px-2 py-1">
            {new Date(data.generated_at).toLocaleString("ar-SA", { timeZone: "Asia/Riyadh" })}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-primary/10 to-transparent p-4">
          <p className="text-xs text-muted-foreground">موافقات معلقة (تقدير)</p>
          <p className="text-2xl font-bold">{data.approvals_pending}</p>
        </div>
        <div className="rounded-2xl border border-border/60 bg-card/50 p-4">
          <p className="text-xs text-muted-foreground">مخالفات / نزاعات مفتوحة</p>
          <p className="text-2xl font-bold">{data.policy_violations_open}</p>
        </div>
        <div className="rounded-2xl border border-border/60 bg-card/50 p-4">
          <p className="text-xs text-muted-foreground">حرارة المخاطر</p>
          <p className="text-2xl font-bold flex items-center gap-2">
            <Activity className="w-5 h-5 text-amber-500" />
            {data.risk.score_0_100}
          </p>
        </div>
        <div className="rounded-2xl border border-border/60 bg-card/50 p-4">
          <p className="text-xs text-muted-foreground">بيئة التشغيل</p>
          <p className="text-lg font-semibold capitalize">{data.release_gate.environment}</p>
        </div>
      </div>

      <section className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <LineChart className="w-5 h-5 text-primary" />
            Sales & Revenue OS
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <div className="rounded-xl border border-border/50 p-3 bg-card/30">
              <p className="text-xs text-muted-foreground">عملاء محتملون</p>
              <p className="text-xl font-bold">{data.sales_os.total_leads}</p>
              <p className="text-[11px] text-muted-foreground">جدد اليوم: {data.sales_os.new_leads_today}</p>
            </div>
            <div className="rounded-xl border border-border/50 p-3 bg-card/30">
              <p className="text-xs text-muted-foreground">قيمة الصفقات المفتوحة (ر.س)</p>
              <p className="text-xl font-bold">{formatSar(data.sales_os.open_deals_value_sar)}</p>
            </div>
            <div className="rounded-xl border border-border/50 p-3 bg-card/30">
              <p className="text-xs text-muted-foreground">مغلقة فوز (ر.س)</p>
              <p className="text-xl font-bold">{formatSar(data.sales_os.closed_won_value_sar)}</p>
              <p className="text-[11px] text-muted-foreground">عدد: {data.sales_os.closed_won_count}</p>
            </div>
            <div className="rounded-xl border border-border/50 p-3 bg-card/30">
              <p className="text-xs text-muted-foreground">اجتماعات ٧ أيام</p>
              <p className="text-xl font-bold">{data.sales_os.upcoming_meetings_7d}</p>
            </div>
            <div className="rounded-xl border border-border/50 p-3 bg-card/30">
              <p className="text-xs text-muted-foreground">عروض / مسودات</p>
              <p className="text-xl font-bold">{data.sales_os.proposals_draft}</p>
              <p className="text-[11px] text-muted-foreground">بانتظار الإرسال: {data.sales_os.proposals_pending_send}</p>
            </div>
            <div className="rounded-xl border border-border/50 p-3 bg-card/30">
              <p className="text-xs text-muted-foreground">رسائل صادرة اليوم</p>
              <p className="text-xl font-bold">{data.sales_os.messages_sent_today}</p>
              <p className="text-[11px] text-muted-foreground">تحويل: {data.sales_os.conversion_rate_pct}%</p>
            </div>
          </div>
        </div>
        <div className="space-y-3">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Shield className="w-5 h-5 text-emerald-500" />
            الخمس طائرات
          </h2>
          <ul className="space-y-2">
            {data.planes.map((p) => (
              <li
                key={p.plane}
                className="flex items-center justify-between rounded-xl border border-border/50 px-3 py-2 text-sm bg-card/40"
              >
                <span>{planeLabelAr(p.plane)}</span>
                <span
                  className={`text-xs font-medium rounded-full px-2 py-0.5 ${
                    p.status === "healthy"
                      ? "bg-emerald-500/15 text-emerald-600"
                      : p.status === "blocked"
                        ? "bg-destructive/15 text-destructive"
                        : "bg-amber-500/15 text-amber-700"
                  }`}
                >
                  {p.status}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
        <div className="flex items-center gap-2 text-sm font-semibold md:col-span-2 xl:col-span-4">
          <Layers className="w-4 h-4" />
          غرف التشغيل الاستراتيجية (DD / شراكة / توسع / PMI)
        </div>
        <PipelineMini board={data.partnership} />
        <PipelineMini board={data.ma_corp_dev} />
        <PipelineMini board={data.expansion} />
        <PipelineMini board={data.pmi_pmo} />
      </section>

      <section className="grid lg:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-border/60 p-5 space-y-4 bg-card/30">
          <h3 className="font-bold flex items-center gap-2">
            <ClipboardList className="w-5 h-5" />
            الإجراء التالي المقترح
          </h3>
          <ul className="space-y-3">
            {(data.executive.next_best_actions ?? []).map((a) => (
              <li key={a.id} className="rounded-xl border border-border/40 p-3 text-sm">
                <p className="font-medium">{a.title_ar}</p>
                <p className="text-xs text-muted-foreground mt-1">{a.title}</p>
                <span className="inline-block mt-2 text-[10px] uppercase tracking-wide text-muted-foreground">
                  {a.priority}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-2xl border border-border/60 p-5 space-y-4 bg-card/30">
          <h3 className="font-bold flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-500" />
            المخاطر والتصعيد
          </h3>
          {data.risk.drivers.length === 0 ? (
            <p className="text-sm text-muted-foreground">لا مؤشرات تصعيد حرجة من البيانات التشغيلية الحالية.</p>
          ) : (
            <ul className="list-disc list-inside text-sm space-y-1">
              {data.risk.drivers.map((d, i) => (
                <li key={i}>{d}</li>
              ))}
            </ul>
          )}
          <p className="text-xs text-muted-foreground">
            التصعيدات المفتوحة (تلميح): {data.executive.escalations_open_hint ?? 0}
          </p>
        </div>
      </section>

      <section className="grid xl:grid-cols-2 gap-6">
        <div className="rounded-2xl border border-border/60 p-5 space-y-3">
          <h3 className="font-bold flex items-center gap-2">
            <Scale className="w-5 h-5" />
            مصفوفة الامتثال (PDPL / NCA ECC / حوكمة AI)
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-right">
              <thead>
                <tr className="text-xs text-muted-foreground border-b border-border/50">
                  <th className="py-2 px-2">المتحكم</th>
                  <th className="py-2 px-2">المجال</th>
                  <th className="py-2 px-2">الحالة</th>
                </tr>
              </thead>
              <tbody>
                {data.compliance_matrix.map((row) => (
                  <tr key={row.control_id} className="border-b border-border/30">
                    <td className="py-2 px-2 font-mono text-xs">{row.control_id}</td>
                    <td className="py-2 px-2">{row.domain}</td>
                    <td className="py-2 px-2">
                      <span
                        className={`text-xs rounded-full px-2 py-0.5 ${
                          row.status === "aligned"
                            ? "bg-emerald-500/15"
                            : row.status === "gap"
                              ? "bg-destructive/15"
                              : "bg-amber-500/15"
                        }`}
                      >
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-muted-foreground">كل صف يجب أن يرتبط لاحقًا بحزمة أدلة قابلة للتدقيق.</p>
        </div>
        <div className="rounded-2xl border border-border/60 p-5 space-y-3">
          <h3 className="font-bold flex items-center gap-2">
            <Cpu className="w-5 h-5" />
            نسيج توجيه النماذج (داخلي)
          </h3>
          <div className="max-h-48 overflow-y-auto rounded-xl border border-border/40 bg-background/40 p-2 font-mono text-[11px] space-y-1">
            {data.model_routing_fabric.map((r) => (
              <div key={r.task_type} className="flex justify-between gap-2 border-b border-border/20 pb-1 last:border-0">
                <span>{r.task_type}</span>
                <span className="text-primary">{r.model_slot}</span>
              </div>
            ))}
          </div>
          <h3 className="font-bold flex items-center gap-2 pt-2">
            <Handshake className="w-5 h-5" />
            سجل التحقق من الأدوات
          </h3>
          <ul className="text-sm space-y-2">
            {data.tool_verification_ledger.map((t) => (
              <li key={t.tool_id} className="flex items-center justify-between rounded-lg border border-border/40 px-3 py-2">
                <span className="font-mono text-xs">{t.tool_id}</span>
                <span className="flex items-center gap-1 text-xs">
                  {t.status === "verified" ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                  ) : (
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                  )}
                  {t.status}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="rounded-2xl border border-border/60 p-5 flex flex-wrap items-center gap-6 bg-secondary/10">
        <div className="flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-muted-foreground" />
          <div>
            <p className="text-xs text-muted-foreground">Release gate</p>
            <p className="text-sm font-medium">
              rulesets: {data.release_gate.rulesets_required ? "مطلوب" : "لا"} · OIDC:{" "}
              {data.release_gate.oidc_preferred ? "مفضل" : "—"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Building2 className="w-5 h-5 text-muted-foreground" />
          <p className="text-xs text-muted-foreground max-w-md">
            هذه اللوحة هي نقطة ربط بين قاعدة البيانات التشغيلية ومسارات HITL — وسيتم تعميقها بـ Temporal وOPA/OpenFGA
            وعقود الأحداث.
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          className="mr-auto inline-flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2 text-sm hover:bg-secondary/60"
        >
          <RefreshCw className="w-4 h-4" />
          تحديث اللقطة
        </button>
      </section>
    </div>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertCircle,
  Bot,
  BrainCircuit,
  Building2,
  CheckCircle2,
  Clock3,
  Database,
  GitBranch,
  Layers,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

import { apiFetch } from "@/lib/api-client";

type Status = "live" | "partial" | "planned";

type SovereignMetric = {
  label_ar: string;
  value: string;
};

type RoomDefinition = {
  id: string;
  plane_id: "decision" | "execution" | "trust" | "data" | "operating";
  name_ar: string;
  name_en: string;
  status: Status;
  outcome_ar: string;
  approval_class: string;
  reversibility_class: string;
  sensitivity_class: string;
  evidence_source: string;
  primary_surface: string;
  metric?: SovereignMetric | null;
};

type PlaneDefinition = {
  id: "decision" | "execution" | "trust" | "data" | "operating";
  name_ar: string;
  name_en: string;
  mission_ar: string;
  operating_model_ar: string;
  status: Status;
  trace_ar: string;
  rooms: RoomDefinition[];
};

type ComplianceControl = {
  framework: string;
  control_ar: string;
  status: Status;
  mapped_surface: string;
};

type ModelRoute = {
  provider: string;
  role_ar: string;
  configured: boolean;
  tasks: string[];
};

type AutomationLane = {
  title_ar: string;
  policy_ar: string;
  examples: string[];
};

type SovereignControlCenter = {
  product_name: string;
  product_tagline_ar: string;
  executive_thesis_ar: string;
  snapshot: {
    demo_mode: boolean;
    pending_approvals: number;
    domain_events_24h: number;
    audit_events_24h: number;
    connectors_total: number;
    connectors_healthy: number;
    company_profiles_total: number;
    strategic_deals_total: number;
    active_matches_total: number;
    dd_rooms_live: number;
    policy_alerts_total: number;
    note_ar: string;
  };
  planes: PlaneDefinition[];
  automation_matrix: AutomationLane[];
  compliance_matrix: ComplianceControl[];
  model_routing: ModelRoute[];
};

function statusLabel(status: Status) {
  if (status === "live") return "نشط";
  if (status === "partial") return "جزئي";
  return "مخطط";
}

function statusClasses(status: Status) {
  if (status === "live") {
    return "border-emerald-500/30 bg-emerald-500/10 text-emerald-200";
  }
  if (status === "partial") {
    return "border-amber-500/30 bg-amber-500/10 text-amber-100";
  }
  return "border-slate-500/30 bg-slate-500/10 text-slate-200";
}

function planeIcon(planeId: PlaneDefinition["id"]) {
  switch (planeId) {
    case "decision":
      return BrainCircuit;
    case "execution":
      return Layers;
    case "trust":
      return ShieldCheck;
    case "data":
      return Database;
    case "operating":
      return GitBranch;
    default:
      return Layers;
  }
}

export function SovereignGrowthOsView() {
  const [data, setData] = useState<SovereignControlCenter | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setErr(null);
    try {
      const response = await apiFetch("/api/v1/sovereign-os/control-center", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      setData((await response.json()) as SovereignControlCenter);
    } catch (error) {
      setErr(error instanceof Error ? error.message : "تعذّر التحميل");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 leading-relaxed text-right rtl">
      <div className="flex flex-col xl:flex-row justify-between items-start xl:items-end gap-6">
        <div className="space-y-3 text-right">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3 py-1.5 text-xs font-bold text-primary">
            <Building2 className="w-4 h-4" />
            <span dir="ltr">Dealix Sovereign Growth, Execution & Governance OS</span>
          </div>
          <div>
            <h1 className="text-2xl md:text-4xl font-black tracking-tight leading-tight" dir="ltr">
              {data?.product_name ?? "Dealix Sovereign OS"}
            </h1>
            <p className="mt-2 text-sm md:text-base text-muted-foreground max-w-4xl">
              {data?.product_tagline_ar ?? "سطح تنفيذي حي يربط القرار بالدليل، والتنفيذ بالموافقة، والحوكمة بالتتبع."}
            </p>
          </div>
          <p className="text-sm text-foreground/85 max-w-4xl">{data?.executive_thesis_ar}</p>
        </div>
        <button
          type="button"
          onClick={() => void load()}
          disabled={loading}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-border bg-card hover:bg-secondary/50 text-sm font-medium"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          تحديث السطح التنفيذي
        </button>
      </div>

      {err && (
        <div className="flex items-start gap-3 rounded-xl border border-destructive/40 bg-destructive/10 p-4 text-sm">
          <AlertCircle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
          <div>
            <p className="font-bold text-destructive">تعذّر الاتصال بـ Sovereign OS API</p>
            <p className="text-muted-foreground mt-1">{err}</p>
          </div>
        </div>
      )}

      {loading && !data && !err && (
        <div className="glass-card p-12 text-center text-muted-foreground">جاري تحميل سطح القرار والتنفيذ والحوكمة…</div>
      )}

      {data && (
        <>
          {data.snapshot.demo_mode && (
            <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 px-4 py-3 text-sm text-amber-200/90">
              وضع توضيحي — اربط حساب المستأجر لرؤية counts الحقيقية للموافقات، الصفقات، والموصلات.
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-6 gap-4">
            {[
              { label: "موافقات معلّقة", value: data.snapshot.pending_approvals, icon: ShieldCheck },
              { label: "أحداث 24 ساعة", value: data.snapshot.domain_events_24h, icon: Layers },
              { label: "تدقيق 24 ساعة", value: data.snapshot.audit_events_24h, icon: CheckCircle2 },
              { label: "صفقات استراتيجية", value: data.snapshot.strategic_deals_total, icon: Building2 },
              { label: "غرف DD", value: data.snapshot.dd_rooms_live, icon: Clock3 },
              { label: "تنبيهات سياسة", value: data.snapshot.policy_alerts_total, icon: AlertCircle },
            ].map((card) => (
              <div key={card.label} className="glass-card p-5 border border-border/50">
                <div className="flex items-center justify-end gap-2 text-xs font-bold text-muted-foreground mb-2">
                  <card.icon className="w-4 h-4" />
                  {card.label}
                </div>
                <p className="text-3xl font-black">{card.value}</p>
              </div>
            ))}
          </div>

          <div className="glass-card p-5 border border-primary/20 bg-primary/5">
            <p className="text-sm text-primary font-bold mb-1">حالة التشغيل المؤسسي</p>
            <p className="text-sm text-foreground/85">{data.snapshot.note_ar}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-5">
            {data.planes.map((plane) => {
              const Icon = planeIcon(plane.id);
              return (
                <div key={plane.id} className="glass-card p-5 border border-border/50 space-y-4 h-full">
                  <div className="flex items-start justify-between gap-3">
                    <span className={`rounded-full border px-2.5 py-1 text-[11px] font-bold ${statusClasses(plane.status)}`}>
                      {statusLabel(plane.status)}
                    </span>
                    <div className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <h2 className="font-black">{plane.name_ar}</h2>
                        <Icon className="w-5 h-5 text-primary" />
                      </div>
                      <p className="text-[11px] text-muted-foreground" dir="ltr">
                        {plane.name_en}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-foreground/85">{plane.mission_ar}</p>
                  <div className="space-y-2 text-xs text-muted-foreground">
                    <p>{plane.operating_model_ar}</p>
                    <p>{plane.trace_ar}</p>
                  </div>
                  <div className="rounded-xl border border-border/40 bg-background/40 px-3 py-2 text-xs text-muted-foreground">
                    {plane.rooms.length} واجهة مرتبطة
                  </div>
                </div>
              );
            })}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {data.planes.map((plane) => (
              <div key={`rooms-${plane.id}`} className="glass-card p-5 border border-border/50 space-y-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-xs text-muted-foreground">{plane.rooms.length} غرفة/سطح</span>
                  <h3 className="font-black">{plane.name_ar}</h3>
                </div>
                <div className="space-y-3">
                  {plane.rooms.map((room) => (
                    <div key={room.id} className="rounded-2xl border border-border/40 bg-background/40 p-4 space-y-3">
                      <div className="flex items-start justify-between gap-3">
                        <span className={`rounded-full border px-2.5 py-1 text-[11px] font-bold ${statusClasses(room.status)}`}>
                          {statusLabel(room.status)}
                        </span>
                        <div className="text-right">
                          <h4 className="font-bold">{room.name_ar}</h4>
                          <p className="text-[11px] text-muted-foreground" dir="ltr">
                            {room.name_en}
                          </p>
                        </div>
                      </div>
                      <p className="text-sm text-foreground/85">{room.outcome_ar}</p>
                      <div className="grid grid-cols-3 gap-2 text-[11px]">
                        <div className="rounded-xl border border-border/40 bg-secondary/20 p-2">
                          <p className="text-muted-foreground mb-1">الاعتماد</p>
                          <p className="font-bold">{room.approval_class}</p>
                        </div>
                        <div className="rounded-xl border border-border/40 bg-secondary/20 p-2">
                          <p className="text-muted-foreground mb-1">الرجوعية</p>
                          <p className="font-bold">{room.reversibility_class}</p>
                        </div>
                        <div className="rounded-xl border border-border/40 bg-secondary/20 p-2">
                          <p className="text-muted-foreground mb-1">الحساسية</p>
                          <p className="font-bold">{room.sensitivity_class}</p>
                        </div>
                      </div>
                      {room.metric && (
                        <div className="rounded-xl border border-primary/20 bg-primary/5 p-3">
                          <p className="text-xs text-muted-foreground">{room.metric.label_ar}</p>
                          <p className="text-lg font-black text-primary">{room.metric.value}</p>
                        </div>
                      )}
                      <div className="text-[11px] text-muted-foreground space-y-2">
                        <div className="rounded-xl border border-border/30 bg-secondary/10 px-3 py-2">
                          <p className="mb-1">مصدر الدليل</p>
                          <p dir="ltr" className="break-all text-foreground/80">
                            {room.evidence_source}
                          </p>
                        </div>
                        <div className="rounded-xl border border-border/30 bg-secondary/10 px-3 py-2">
                          <p className="mb-1">السطح الرئيسي</p>
                          <p dir="ltr" className="break-all text-foreground/80">
                            {room.primary_surface}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="glass-card p-5 border border-border/50 space-y-4">
              <div className="flex items-center justify-end gap-2">
                <Bot className="w-5 h-5 text-primary" />
                <h3 className="font-black">Matrix — ما يُؤتمت بالكامل وما يُراجع</h3>
              </div>
              <div className="space-y-3">
                {data.automation_matrix.map((lane) => (
                  <div key={lane.title_ar} className="rounded-2xl border border-border/40 bg-background/40 p-4">
                    <h4 className="font-bold mb-2">{lane.title_ar}</h4>
                    <p className="text-sm text-muted-foreground mb-3">{lane.policy_ar}</p>
                    <ul className="space-y-2 text-sm text-foreground/85 list-disc list-inside">
                      {lane.examples.map((example) => (
                        <li key={example}>{example}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card p-5 border border-border/50 space-y-4">
              <div className="flex items-center justify-end gap-2">
                <ShieldCheck className="w-5 h-5 text-primary" />
                <h3 className="font-black">Saudi compliance + AI governance</h3>
              </div>
              <div className="space-y-3">
                {data.compliance_matrix.map((control) => (
                  <div key={`${control.framework}-${control.control_ar}`} className="rounded-2xl border border-border/40 bg-background/40 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <span className={`rounded-full border px-2.5 py-1 text-[11px] font-bold ${statusClasses(control.status)}`}>
                        {statusLabel(control.status)}
                      </span>
                      <h4 className="font-bold" dir="ltr">
                        {control.framework}
                      </h4>
                    </div>
                    <p className="text-sm mt-3">{control.control_ar}</p>
                    <div className="mt-2 rounded-xl border border-border/30 bg-secondary/10 px-3 py-2 text-[11px] text-muted-foreground">
                      <p className="mb-1">السطح المرتبط</p>
                      <p dir="ltr" className="break-all text-foreground/80">
                        {control.mapped_surface}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="glass-card p-5 border border-border/50 space-y-4">
            <div className="flex items-center justify-end gap-2">
              <BrainCircuit className="w-5 h-5 text-primary" />
              <h3 className="font-black">لوحة توجيه النماذج</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 2xl:grid-cols-3 gap-4">
              {data.model_routing.map((route) => (
                <div key={route.provider} className="rounded-2xl border border-border/40 bg-background/40 p-4 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <span
                      className={`rounded-full border px-2.5 py-1 text-[11px] font-bold ${
                        route.configured
                          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
                          : "border-amber-500/30 bg-amber-500/10 text-amber-100"
                      }`}
                    >
                      {route.configured ? "مهيأ" : "احتياطي"}
                    </span>
                    <div className="text-right">
                      <h4 className="font-bold uppercase" dir="ltr">
                        {route.provider}
                      </h4>
                      <p className="text-[11px] text-muted-foreground">{route.role_ar}</p>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {route.tasks.length} أنواع مهام
                  </div>
                  <div className="flex flex-wrap gap-2 justify-end">
                    {route.tasks.slice(0, 6).map((task) => (
                      <span
                        key={task}
                        dir="ltr"
                        className="rounded-full border border-border/40 bg-secondary/20 px-2.5 py-1 text-[11px]"
                      >
                        {task}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

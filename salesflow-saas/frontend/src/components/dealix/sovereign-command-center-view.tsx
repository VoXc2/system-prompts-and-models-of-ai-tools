"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  GitBranch,
  LockKeyhole,
  Radar,
  RefreshCw,
  Shield,
  TowerControl,
} from "lucide-react";

import { apiFetch } from "@/lib/api-client";

type Status = "live" | "partial" | "planned" | "success" | "warning" | "info";

type Metric = {
  key: string;
  label_ar: string;
  value: number | string;
  unit?: string | null;
  status: Status;
};

type Plane = {
  key: string;
  title_ar: string;
  status: Status;
  description_ar: string;
  backbone: string[];
  live_signals: string[];
  control_focus: string[];
};

type OperatingSystem = {
  key: string;
  title_ar: string;
  status: Status;
  automation_summary_ar: string;
  auto_scope: string[];
  approval_scope: string[];
  coverage_metrics: Record<string, number>;
};

type GovernanceClass = {
  key: string;
  title_ar: string;
  description_ar: string;
  examples: string[];
};

type CommitmentGate = {
  action: string;
  title_ar: string;
  approval_class: string;
  reversibility_class: string;
  sensitivity_class: string;
  why_ar: string;
};

type Surface = {
  slug: string;
  title_ar: string;
  plane: string;
  status: Status;
  backing_routes: string[];
  status_reason_ar: string;
};

type ModelRouting = {
  providers: {
    provider: string;
    label_ar: string;
    task_count: number;
    task_types: string[];
  }[];
  benchmark_dimensions: string[];
  recommended_fabric_ar: string;
};

type ComplianceControl = {
  framework: string;
  control_id: string;
  title_ar: string;
  status: Status;
  evidence: string[];
};

type Gap = {
  slug: string;
  title_ar: string;
  severity: "high" | "medium" | "low";
  status_needed: string;
  next_step_ar: string;
};

type Payload = {
  demo_mode: boolean;
  headline: {
    system_name_ar: string;
    subtitle_ar: string;
    operating_mode: string;
    status: Status;
    readiness_percent: number;
    traceability_status: string;
    policy_posture: string;
  };
  metrics: Metric[];
  planes: Plane[];
  operating_systems: OperatingSystem[];
  approval_classes: GovernanceClass[];
  reversibility_classes: GovernanceClass[];
  sensitivity_classes: GovernanceClass[];
  commitment_gates: CommitmentGate[];
  surfaces: Surface[];
  model_routing: ModelRouting;
  saudi_compliance: ComplianceControl[];
  gaps: Gap[];
  note_ar: string;
};

function statusClasses(status: Status) {
  switch (status) {
    case "live":
    case "success":
      return "border-emerald-500/30 bg-emerald-500/10 text-emerald-200";
    case "partial":
    case "warning":
      return "border-amber-500/30 bg-amber-500/10 text-amber-100";
    case "planned":
      return "border-slate-500/30 bg-slate-500/10 text-slate-200";
    default:
      return "border-cyan-500/30 bg-cyan-500/10 text-cyan-100";
  }
}

function severityClasses(severity: Gap["severity"]) {
  if (severity === "high") return "border-rose-500/30 bg-rose-500/10 text-rose-100";
  if (severity === "medium") return "border-amber-500/30 bg-amber-500/10 text-amber-100";
  return "border-slate-500/30 bg-slate-500/10 text-slate-100";
}

function formatMetric(metric: Metric) {
  return `${metric.value}${metric.unit ?? ""}`;
}

function CoverageList({ items }: { items: Record<string, number> }) {
  return (
    <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
      {Object.entries(items).map(([key, value]) => (
        <div key={key} className="rounded-lg border border-border/50 bg-background/30 px-3 py-2">
          <p className="font-mono text-[10px] opacity-70">{key}</p>
          <p className="mt-1 text-sm font-black text-foreground">{value}</p>
        </div>
      ))}
    </div>
  );
}

export function SovereignCommandCenterView() {
  const [data, setData] = useState<Payload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiFetch("/api/v1/operations/command-center", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`command-center ${response.status}`);
      }
      setData((await response.json()) as Payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "تعذر تحميل السطح المؤسسي");
      setData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const liveCounts = useMemo(() => {
    const surfaces = data?.surfaces ?? [];
    return {
      live: surfaces.filter((surface) => surface.status === "live").length,
      partial: surfaces.filter((surface) => surface.status === "partial").length,
      planned: surfaces.filter((surface) => surface.status === "planned").length,
    };
  }, [data]);

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-3">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-bold text-primary">
            <TowerControl className="h-4 w-4" />
            Sovereign Growth, Execution & Governance OS
          </div>
          <div>
            <h1 className="text-2xl md:text-3xl font-black tracking-tight">{data?.headline.system_name_ar ?? "السطح المؤسسي"}</h1>
            <p className="mt-2 max-w-4xl text-sm md:text-base text-muted-foreground">
              {data?.headline.subtitle_ar ?? "تحويل الحوكمة والتنفيذ والقرار إلى سطح حي داخل Dealix."}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 justify-end">
          {data && (
            <>
              <span className={`rounded-full border px-3 py-1 text-xs font-bold ${statusClasses(data.headline.status)}`}>
                {data.headline.status === "live" ? "حي" : data.headline.status === "partial" ? "جزئي" : "قيد الإكمال"}
              </span>
              <span className="rounded-full border border-border/60 bg-card px-3 py-1 text-xs font-bold text-muted-foreground">
                Traceability: {data.headline.traceability_status}
              </span>
              <span className="rounded-full border border-border/60 bg-card px-3 py-1 text-xs font-bold text-muted-foreground">
                Policy: {data.headline.policy_posture}
              </span>
            </>
          )}
          <button
            type="button"
            onClick={() => void load()}
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-2 text-sm font-bold hover:bg-secondary/50"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            تحديث
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-2xl border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
          تعذر تحميل السطح المؤسسي: {error}
        </div>
      )}

      {data && (
        <>
          {data.demo_mode && (
            <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-100">
              وضع توضيحي: يتم عرض surface المؤسسي حتى بدون جلسة، بينما تتحول الأرقام إلى بيانات المستأجر بعد تسجيل الدخول.
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-6">
            {data.metrics.map((metric) => (
              <div key={metric.key} className="glass-card rounded-2xl border border-border/50 p-5">
                <div className={`inline-flex rounded-full border px-2 py-1 text-[10px] font-bold ${statusClasses(metric.status)}`}>
                  {metric.label_ar}
                </div>
                <p className="mt-4 text-3xl font-black">{formatMetric(metric)}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.4fr,0.9fr]">
            <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-5">
              <div className="flex items-center gap-2 text-lg font-black">
                <Radar className="h-5 w-5 text-primary" />
                حالة الـ planes
              </div>
              <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
                {data.planes.map((plane) => (
                  <div key={plane.key} className="rounded-2xl border border-border/60 bg-background/25 p-4 space-y-4">
                    <div className="flex items-center justify-between gap-3">
                      <h2 className="font-black">{plane.title_ar}</h2>
                      <span className={`rounded-full border px-2.5 py-1 text-[10px] font-bold ${statusClasses(plane.status)}`}>
                        {plane.status === "live" ? "live" : plane.status === "partial" ? "partial" : "planned"}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{plane.description_ar}</p>
                    <div className="space-y-2">
                      <p className="text-xs font-bold text-primary">Backbone</p>
                      <div className="flex flex-wrap gap-2">
                        {plane.backbone.map((item) => (
                          <span key={item} className="rounded-full border border-border/60 bg-card px-2.5 py-1 text-[11px] text-muted-foreground">
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                      <div>
                        <p className="text-xs font-bold text-primary">Signals</p>
                        <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                          {plane.live_signals.map((item) => (
                            <li key={item} className="flex items-start gap-2">
                              <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 text-emerald-300" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <p className="text-xs font-bold text-primary">Controls</p>
                        <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                          {plane.control_focus.map((item) => (
                            <li key={item} className="flex items-start gap-2">
                              <ChevronLeft className="mt-0.5 h-3.5 w-3.5 text-primary" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-5">
              <div className="flex items-center gap-2 text-lg font-black">
                <Activity className="h-5 w-5 text-primary" />
                حي مقابل الجزئي
              </div>
              <div className="grid grid-cols-3 gap-3">
                {[
                  { label: "Live", value: liveCounts.live, status: "live" as Status },
                  { label: "Partial", value: liveCounts.partial, status: "partial" as Status },
                  { label: "Planned", value: liveCounts.planned, status: "planned" as Status },
                ].map((item) => (
                  <div key={item.label} className={`rounded-2xl border p-4 text-center ${statusClasses(item.status)}`}>
                    <p className="text-xs font-bold">{item.label}</p>
                    <p className="mt-2 text-3xl font-black">{item.value}</p>
                  </div>
                ))}
              </div>
              <div className="rounded-2xl border border-border/60 bg-background/25 p-4 text-sm text-muted-foreground">
                <p className="font-bold text-foreground">ملاحظة تشغيلية</p>
                <p className="mt-2">{data.note_ar}</p>
              </div>
            </div>
          </div>

          <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-5">
            <div className="flex items-center gap-2 text-lg font-black">
              <GitBranch className="h-5 w-5 text-primary" />
              Operating Systems
            </div>
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
              {data.operating_systems.map((system) => (
                <div key={system.key} className="rounded-2xl border border-border/60 bg-background/25 p-5 space-y-4">
                  <div className="flex items-center justify-between gap-3">
                    <h2 className="font-black">{system.title_ar}</h2>
                    <span className={`rounded-full border px-2.5 py-1 text-[10px] font-bold ${statusClasses(system.status)}`}>
                      {system.status}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{system.automation_summary_ar}</p>
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div>
                      <p className="text-xs font-bold text-emerald-300">مؤتمت بالكامل</p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {system.auto_scope.map((item) => (
                          <span key={item} className="rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] text-emerald-100">
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-bold text-amber-200">يتطلب اعتمادًا</p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {system.approval_scope.map((item) => (
                          <span key={item} className="rounded-full border border-amber-500/20 bg-amber-500/10 px-2.5 py-1 text-[11px] text-amber-100">
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <CoverageList items={system.coverage_metrics} />
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.15fr,0.85fr]">
            <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-5">
              <div className="flex items-center gap-2 text-lg font-black">
                <LockKeyhole className="h-5 w-5 text-primary" />
                Governance Fabric
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                {[
                  { title: "Approval", items: data.approval_classes },
                  { title: "Reversibility", items: data.reversibility_classes },
                  { title: "Sensitivity", items: data.sensitivity_classes },
                ].map((group) => (
                  <div key={group.title} className="rounded-2xl border border-border/60 bg-background/25 p-4">
                    <p className="text-sm font-black text-primary">{group.title}</p>
                    <div className="mt-3 space-y-3">
                      {group.items.map((item) => (
                        <div key={item.key} className="rounded-xl border border-border/50 bg-background/40 p-3">
                          <div className="flex items-center justify-between gap-2">
                            <p className="font-bold">{item.title_ar}</p>
                            <span className="font-mono text-[10px] text-muted-foreground">{item.key}</span>
                          </div>
                          <p className="mt-2 text-xs text-muted-foreground">{item.description_ar}</p>
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {item.examples.map((example) => (
                              <span key={example} className="rounded-full border border-border/50 px-2 py-0.5 text-[10px] text-muted-foreground">
                                {example}
                              </span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-4">
              <div className="flex items-center gap-2 text-lg font-black">
                <Shield className="h-5 w-5 text-primary" />
                Commitment Gates
              </div>
              <div className="space-y-3">
                {data.commitment_gates.map((gate) => (
                  <div key={gate.action} className="rounded-2xl border border-border/60 bg-background/25 p-4">
                    <div className="flex flex-wrap items-center gap-2 justify-between">
                      <p className="font-black">{gate.title_ar}</p>
                      <div className="flex flex-wrap gap-1.5">
                        {[gate.approval_class, gate.reversibility_class, gate.sensitivity_class].map((tag) => (
                          <span key={tag} className="rounded-full border border-primary/20 bg-primary/10 px-2 py-0.5 text-[10px] font-bold text-primary">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">{gate.why_ar}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.1fr,0.9fr]">
            <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-5">
              <div className="flex items-center gap-2 text-lg font-black">
                <TowerControl className="h-5 w-5 text-primary" />
                Live Surfaces Matrix
              </div>
              <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
                {data.surfaces.map((surface) => (
                  <div key={surface.slug} className="rounded-2xl border border-border/60 bg-background/25 p-4 space-y-3">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-black">{surface.title_ar}</p>
                        <p className="text-[11px] text-muted-foreground">Plane: {surface.plane}</p>
                      </div>
                      <span className={`rounded-full border px-2.5 py-1 text-[10px] font-bold ${statusClasses(surface.status)}`}>
                        {surface.status}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">{surface.status_reason_ar}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {surface.backing_routes.map((route) => (
                        <span key={route} className="rounded-full border border-border/50 px-2 py-0.5 text-[10px] font-mono text-muted-foreground">
                          {route}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="space-y-4">
              <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-4">
                <div className="flex items-center gap-2 text-lg font-black">
                  <Activity className="h-5 w-5 text-primary" />
                  Model Routing Dashboard
                </div>
                <div className="space-y-3">
                  {data.model_routing.providers.map((provider) => (
                    <div key={provider.provider} className="rounded-2xl border border-border/60 bg-background/25 p-4">
                      <div className="flex items-center justify-between gap-3">
                        <p className="font-black">{provider.label_ar}</p>
                        <span className="rounded-full border border-primary/20 bg-primary/10 px-2 py-0.5 text-[10px] font-bold text-primary">
                          {provider.task_count} tasks
                        </span>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {provider.task_types.map((task) => (
                          <span key={task} className="rounded-full border border-border/50 px-2 py-0.5 text-[10px] font-mono text-muted-foreground">
                            {task}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="rounded-2xl border border-border/60 bg-background/25 p-4">
                  <p className="text-xs font-bold text-primary">Benchmark Harness</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {data.model_routing.benchmark_dimensions.map((dimension) => (
                      <span key={dimension} className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-2.5 py-1 text-[11px] text-cyan-100">
                        {dimension}
                      </span>
                    ))}
                  </div>
                  <p className="mt-3 text-sm text-muted-foreground">{data.model_routing.recommended_fabric_ar}</p>
                </div>
              </div>

              <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-4">
                <div className="flex items-center gap-2 text-lg font-black">
                  <Shield className="h-5 w-5 text-primary" />
                  Saudi Compliance Matrix
                </div>
                {data.saudi_compliance.map((control) => (
                  <div key={control.control_id} className="rounded-2xl border border-border/60 bg-background/25 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="font-black">{control.title_ar}</p>
                        <p className="text-[11px] text-muted-foreground">
                          {control.framework} - {control.control_id}
                        </p>
                      </div>
                      <span className={`rounded-full border px-2.5 py-1 text-[10px] font-bold ${statusClasses(control.status)}`}>
                        {control.status}
                      </span>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {control.evidence.map((evidence) => (
                        <span key={evidence} className="rounded-full border border-border/50 px-2 py-0.5 text-[10px] text-muted-foreground">
                          {evidence}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="glass-card rounded-3xl border border-border/50 p-6 space-y-5">
            <div className="flex items-center gap-2 text-lg font-black">
              <AlertTriangle className="h-5 w-5 text-primary" />
              Gaps to Dominance
            </div>
            <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-3">
              {data.gaps.map((gap) => (
                <div key={gap.slug} className={`rounded-2xl border p-4 ${severityClasses(gap.severity)}`}>
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-black">{gap.title_ar}</p>
                    <span className="rounded-full border border-white/10 bg-black/10 px-2 py-0.5 text-[10px] font-bold">
                      {gap.severity}
                    </span>
                  </div>
                  <p className="mt-3 text-sm">{gap.next_step_ar}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {loading && !data && !error && (
        <div className="glass-card rounded-3xl border border-border/50 p-12 text-center text-muted-foreground">
          جاري بناء السطح التنفيذي...
        </div>
      )}
    </div>
  );
}

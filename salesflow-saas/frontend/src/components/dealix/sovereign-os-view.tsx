"use client";

import { useEffect, useState, type ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  Building2,
  CheckCircle2,
  ClipboardList,
  Crown,
  Database,
  GitBranch,
  Handshake,
  Layers,
  LineChart,
  Lock,
  Network,
  RefreshCw,
  Rocket,
  Scale,
  ShieldCheck,
  Target,
} from "lucide-react";

import { apiFetch } from "@/lib/api-client";

type StatusKind = "live" | "foundation" | "gap";
type ModeKind = "demo" | "tenant";

type StatusCounts = {
  live: number;
  foundation: number;
  gap: number;
};

type PlaneMetric = {
  label_ar: string;
  value: string;
  hint_ar?: string | null;
};

type PlaneCard = {
  id: string;
  title_ar: string;
  status: StatusKind;
  current_state_ar: string;
  target_state_ar: string;
  summary_ar: string;
  evidence_sources: string[];
  metrics: PlaneMetric[];
};

type BusinessSystemCard = {
  id: string;
  title_ar: string;
  status: StatusKind;
  summary_ar: string;
  stages: string[];
  automation_now: string[];
  approval_gates: string[];
};

type LiveSurfaceCard = {
  id: string;
  title_ar: string;
  status: StatusKind;
  plane_owner_ar: string;
  route_hint?: string | null;
  api_hint?: string | null;
  note_ar: string;
};

type MetadataClassCard = {
  family: "approval" | "reversibility" | "sensitivity";
  code: string;
  label_ar: string;
  mode_ar: string;
  examples: string[];
};

type AutomationBucket = {
  id: string;
  label_ar: string;
  mode: "auto" | "approval";
  items: string[];
};

type ComplianceControlCard = {
  id: string;
  title_ar: string;
  status: StatusKind;
  control_ar: string;
  note_ar: string;
};

type BenchmarkHarness = {
  status: StatusKind;
  title_ar: string;
  note_ar: string;
  metrics: string[];
};

type LaunchGateSummary = {
  overall: string;
  readiness_percent: number;
  missing_count: number;
  summary_ar: string;
  blocked_reasons: string[];
};

type OperationalPulse = {
  demo_mode: boolean;
  pending_approvals: number;
  domain_events_24h: number;
  audit_events_24h: number;
  connectors_total: number;
  openclaw_runs: number;
  approval_health: string;
  note_ar?: string | null;
};

type ExecutiveRoomResponse = {
  title_ar: string;
  title_en: string;
  summary_ar: string;
  north_star_ar: string;
  mode: ModeKind;
  surface_coverage: StatusCounts;
  system_coverage: StatusCounts;
  operational_pulse: OperationalPulse;
  launch_gate: LaunchGateSummary;
  planes: PlaneCard[];
  business_systems: BusinessSystemCard[];
  live_surfaces: LiveSurfaceCard[];
  decision_metadata_classes: MetadataClassCard[];
  automation_policy: AutomationBucket[];
  compliance_matrix: ComplianceControlCard[];
  benchmark_harness: BenchmarkHarness;
  next_moves: string[];
};

const FALLBACK: ExecutiveRoomResponse = {
  title_ar: "الغرفة التنفيذية والسيادية",
  title_en: "Dealix Sovereign Growth, Execution & Governance OS",
  summary_ar: "واجهة تنفيذية موحدة تعرض ما هو حي الآن وما هو قيد التأسيس داخل نظام التشغيل المؤسسي.",
  north_star_ar: "typed + enforced + observable + approvable + durable + bilingual + compliance-aware.",
  mode: "demo",
  surface_coverage: { live: 2, foundation: 1, gap: 1 },
  system_coverage: { live: 2, foundation: 3, gap: 1 },
  operational_pulse: {
    demo_mode: true,
    pending_approvals: 0,
    domain_events_24h: 0,
    audit_events_24h: 0,
    connectors_total: 4,
    openclaw_runs: 0,
    approval_health: "ok",
    note_ar: "وضع توضيحي — البيانات الحية تظهر عند تشغيل الـ API.",
  },
  launch_gate: {
    overall: "FAIL",
    readiness_percent: 0,
    missing_count: 0,
    summary_ar: "بيانات توضيحية حتى يبدأ الخادم بإرجاع تقرير الجاهزية الحي.",
    blocked_reasons: [],
  },
  planes: [
    {
      id: "decision",
      title_ar: "Decision Plane",
      status: "foundation",
      current_state_ar: "أساس القرار الحي موجود، لكن التوحيد على structured contracts لم يكتمل بعد.",
      target_state_ar: "قرارات typed + evidence-backed + approval-aware.",
      summary_ar: "طبقة قرار قابلة للتوسعة المؤسسية.",
      evidence_sources: ["/api/v1/operating-system/executive-room"],
      metrics: [{ label_ar: "موافقات", value: "0" }],
    },
    {
      id: "execution",
      title_ar: "Execution Plane",
      status: "foundation",
      current_state_ar: "العمليات والflows موجودة لكن durable execution الكامل ما زال هدفًا.",
      target_state_ar: "workflow runtime موحد للالتزامات الطويلة.",
      summary_ar: "أساس التنفيذ الحي قائم وقابل للتطوير.",
      evidence_sources: ["/api/v1/operations/snapshot"],
      metrics: [{ label_ar: "تشغيلات", value: "0" }],
    },
    {
      id: "trust",
      title_ar: "Trust Plane",
      status: "foundation",
      current_state_ar: "الموافقات والامتثال حيّة، لكن طبقة trust الموحدة لم تُستكمل.",
      target_state_ar: "policy + authorization + secrets + audit موحد.",
      summary_ar: "حوكمة حيّة تحتاج توحيدًا سياديًا.",
      evidence_sources: ["/api/v1/operations/approvals"],
      metrics: [{ label_ar: "SLA", value: "ok" }],
    },
    {
      id: "data",
      title_ar: "Data Plane",
      status: "foundation",
      current_state_ar: "البيانات التشغيلية حية لكن event contracts والقياس الموحد ما زالا قيد البناء.",
      target_state_ar: "truth + events + memory + telemetry بعقود واضحة.",
      summary_ar: "أساس بيانات حي وقابل للحوكمة.",
      evidence_sources: ["/api/v1/operations/domain-events"],
      metrics: [{ label_ar: "موصلات", value: "4" }],
    },
    {
      id: "operating",
      title_ar: "Operating Plane",
      status: "foundation",
      current_state_ar: "go-live gate حي لكن release governance لم يكتمل بعد.",
      target_state_ar: "rulesets + OIDC + provenance + environments.",
      summary_ar: "طبقة تشغيل مؤسسي تتشكل.",
      evidence_sources: ["/api/v1/autonomous-foundation/integrations/live-readiness"],
      metrics: [{ label_ar: "جاهزية", value: "0%" }],
    },
  ],
  business_systems: [
    {
      id: "sales_revenue_os",
      title_ar: "Sales & Revenue OS",
      status: "live",
      summary_ar: "أقوى جزء حي الآن.",
      stages: ["capture", "scoring", "routing", "pipeline", "proposal", "handoff"],
      automation_now: ["capture", "enrichment", "scoring"],
      approval_gates: ["discount خارج السياسة", "signature النهائي"],
    },
    {
      id: "partnership_os",
      title_ar: "Partnership OS",
      status: "foundation",
      summary_ar: "جاهز للبناء فوق الأساس الحالي.",
      stages: ["scouting", "fit", "term sheet", "activation"],
      automation_now: ["research", "drafting"],
      approval_gates: ["term sheet", "rev-share"],
    },
    {
      id: "ma_os",
      title_ar: "M&A / Corporate Development OS",
      status: "foundation",
      summary_ar: "بذور موجودة لكن الـ room الكامل ناقص.",
      stages: ["sourcing", "screening", "DD", "valuation", "offer"],
      automation_now: ["screening", "evidence"],
      approval_gates: ["offer", "signing"],
    },
    {
      id: "expansion_os",
      title_ar: "Expansion OS",
      status: "foundation",
      summary_ar: "launch readiness حي لكن console التوسع لم يكتمل.",
      stages: ["scan", "readiness", "launch", "stop-loss"],
      automation_now: ["readiness checks"],
      approval_gates: ["market launch"],
    },
    {
      id: "pmi_pmo_os",
      title_ar: "PMI / Strategic PMO OS",
      status: "gap",
      summary_ar: "أوضح فجوة تشغيلية حالية.",
      stages: ["day-1", "30/60/90", "dependencies", "escalations"],
      automation_now: [],
      approval_gates: ["exec escalation"],
    },
    {
      id: "executive_board_os",
      title_ar: "Executive / Board OS",
      status: "live",
      summary_ar: "الغرفة التنفيذية تجعل القرار قابلاً للبيع للإدارة العليا.",
      stages: ["executive room", "risk", "approval", "forecast"],
      automation_now: ["summaries", "status narration"],
      approval_gates: ["board exceptions"],
    },
  ],
  live_surfaces: [
    {
      id: "executive_room",
      title_ar: "Executive Room",
      status: "live",
      plane_owner_ar: "Decision + Operating",
      route_hint: "/dashboard",
      api_hint: "/api/v1/operating-system/executive-room",
      note_ar: "واجهة موحدة للقرار والجاهزية والفجوات.",
    },
    {
      id: "approval_center",
      title_ar: "Approval Center",
      status: "foundation",
      plane_owner_ar: "Trust",
      api_hint: "/api/v1/operations/approvals",
      note_ar: "الـ API موجود والواجهة المخصصة قيد الإكمال.",
    },
    {
      id: "connector_health_board",
      title_ar: "Connector Health Board",
      status: "live",
      plane_owner_ar: "Data + Operating",
      api_hint: "/api/v1/operations/snapshot",
      note_ar: "اللوحة موجودة بالفعل داخل Full Ops.",
    },
    {
      id: "model_routing_dashboard",
      title_ar: "Model Routing Dashboard",
      status: "gap",
      plane_owner_ar: "Decision",
      note_ar: "benchmark harness لم يتحول إلى dashboard بعد.",
    },
  ],
  decision_metadata_classes: [
    {
      family: "approval",
      code: "A0",
      label_ar: "تلقائي وآمن",
      mode_ar: "بدون اعتماد",
      examples: ["capture", "scoring"],
    },
    {
      family: "reversibility",
      code: "R2",
      label_ar: "التزام خارجي",
      mode_ar: "اعتماد إلزامي",
      examples: ["term sheet", "signature"],
    },
    {
      family: "sensitivity",
      code: "S3",
      label_ar: "PDPL / حساسية عالية",
      mode_ar: "تدقيق + policy gate",
      examples: ["PII", "data sharing"],
    },
  ],
  automation_policy: [
    {
      id: "fully_automated",
      label_ar: "مؤتمت بالكامل بلا اعتماد",
      mode: "auto",
      items: ["capture", "enrichment", "scoring", "dashboard updates"],
    },
    {
      id: "approval_gated",
      label_ar: "مؤتمت مع اعتماد قبل الالتزام",
      mode: "approval",
      items: ["term sheet", "market launch", "external commitments"],
    },
  ],
  compliance_matrix: [
    {
      id: "pdpl_outbound",
      title_ar: "PDPL Outbound Control",
      status: "live",
      control_ar: "تحقق موافقة قبل outbound.",
      note_ar: "الأساس حي.",
    },
    {
      id: "saudi_control_mapping",
      title_ar: "Saudi Control Mapping",
      status: "foundation",
      control_ar: "ربط workflows الحساسة بالضوابط السعودية.",
      note_ar: "يحتاج matrix حي داخل المنتج.",
    },
    {
      id: "owasp_llm",
      title_ar: "OWASP LLM Controls",
      status: "foundation",
      control_ar: "ضبط مخاطر التطبيقات المعتمدة على LLM.",
      note_ar: "تحتاج برنامجًا حيًا داخل السطح التنفيذي.",
    },
  ],
  benchmark_harness: {
    status: "gap",
    title_ar: "Model Routing Benchmark Harness",
    note_ar: "routing intelligence يجب أن يبنى على benchmark pool داخلي.",
    metrics: ["latency", "success rate", "schema adherence", "Arabic memo quality"],
  },
  next_moves: [
    "حوّل Approval Center إلى surface مستقل.",
    "أظهر Saudi Compliance Matrix داخل المنتج.",
    "ابنِ Model Routing Dashboard فوق benchmark harness.",
  ],
};

function statusLabel(status: StatusKind) {
  if (status === "live") return "Live";
  if (status === "foundation") return "Foundation";
  return "Gap";
}

function statusClasses(status: StatusKind) {
  if (status === "live") return "border-emerald-500/30 bg-emerald-500/10 text-emerald-200";
  if (status === "foundation") return "border-amber-500/30 bg-amber-500/10 text-amber-100";
  return "border-rose-500/30 bg-rose-500/10 text-rose-200";
}

function familyLabel(family: MetadataClassCard["family"]) {
  if (family === "approval") return "Approval";
  if (family === "reversibility") return "Reversibility";
  return "Sensitivity";
}

function modeLabel(mode: ModeKind) {
  return mode === "tenant" ? "Tenant Live" : "Demo";
}

function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`glass-card border border-border/50 ${className}`}>{children}</div>;
}

function metricValueClasses(status: string) {
  if (status === "ok" || status === "PASS") return "text-emerald-300";
  if (status === "warn" || status === "foundation") return "text-amber-200";
  return "text-rose-200";
}

function systemIcon(id: string) {
  switch (id) {
    case "sales_revenue_os":
      return Target;
    case "partnership_os":
      return Handshake;
    case "ma_os":
      return Building2;
    case "expansion_os":
      return Rocket;
    case "pmi_pmo_os":
      return ClipboardList;
    default:
      return Crown;
  }
}

function planeIcon(id: string) {
  switch (id) {
    case "decision":
      return BrainCircuit;
    case "execution":
      return Layers;
    case "trust":
      return ShieldCheck;
    case "data":
      return Database;
    default:
      return GitBranch;
  }
}

export function SovereignOsView() {
  const [data, setData] = useState<ExecutiveRoomResponse>(FALLBACK);
  const [loading, setLoading] = useState(true);
  const [live, setLive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch("/api/v1/operating-system/executive-room", { cache: "no-store" });
        if (!res.ok) throw new Error(`executive-room ${res.status}`);
        const payload = (await res.json()) as ExecutiveRoomResponse;
        setData(payload);
        setLive(true);
      } catch (err) {
        setData(FALLBACK);
        setLive(false);
        setError(err instanceof Error ? err.message : "تعذر تحميل الغرفة التنفيذية");
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  const gapSurfaces = data.live_surfaces.filter((item) => item.status === "gap").length;

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 text-right" dir="rtl">
      <div className="flex flex-col xl:flex-row xl:items-end xl:justify-between gap-6">
        <div className="space-y-3 max-w-4xl mr-0 ml-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary/25 bg-primary/10 text-primary text-xs font-bold">
            <Crown className="w-4 h-4" />
            Executive Room
          </div>
          <h1 className="text-3xl md:text-4xl font-black tracking-tight">{data.title_ar}</h1>
          <p className="text-base text-muted-foreground leading-relaxed">{data.summary_ar}</p>
          <p className="text-sm text-primary/90 leading-relaxed">{data.north_star_ar}</p>
        </div>

        <div className="flex flex-wrap items-center gap-3 justify-end">
          <span className={`text-xs font-bold px-3 py-1.5 rounded-full border ${statusClasses(live ? "live" : "foundation")}`}>
            {modeLabel(data.mode)}
          </span>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border border-border bg-card hover:bg-secondary/50 text-sm font-medium"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            تحديث
          </button>
        </div>
      </div>

      {!live && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
          يتم عرض fallback محلي إلى أن يصبح تقرير `executive-room` متاحًا من الخادم.
        </div>
      )}

      {error && (
        <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
          {error}
        </div>
      )}

      {data.operational_pulse.demo_mode && (
        <div className="rounded-2xl border border-primary/20 bg-primary/5 px-4 py-3 text-sm text-primary/90">
          {data.operational_pulse.note_ar || "وضع توضيحي — سجّل الدخول وشغّل الـ API لعرض إشارات المستأجر الحية."}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <Panel className="p-5">
          <div className="flex items-center gap-2 justify-end text-xs font-bold text-muted-foreground mb-2">
            <GitBranch className="w-4 h-4" />
            جاهزية الإطلاق
          </div>
          <p className={`text-3xl font-black ${metricValueClasses(data.launch_gate.overall)}`}>
            {data.launch_gate.readiness_percent.toFixed(1)}%
          </p>
          <p className="text-xs text-muted-foreground mt-2">{data.launch_gate.summary_ar}</p>
        </Panel>

        <Panel className="p-5">
          <div className="flex items-center gap-2 justify-end text-xs font-bold text-muted-foreground mb-2">
            <ShieldCheck className="w-4 h-4" />
            موافقات معلقة
          </div>
          <p className="text-3xl font-black">{data.operational_pulse.pending_approvals}</p>
          <p className="text-xs text-muted-foreground mt-2">الحالة الحالية لـ Approval SLA: {data.operational_pulse.approval_health}</p>
        </Panel>

        <Panel className="p-5">
          <div className="flex items-center gap-2 justify-end text-xs font-bold text-muted-foreground mb-2">
            <Network className="w-4 h-4" />
            تغطية الأسطح
          </div>
          <p className="text-3xl font-black">{data.surface_coverage.live}</p>
          <p className="text-xs text-muted-foreground mt-2">
            Live {data.surface_coverage.live} · Foundation {data.surface_coverage.foundation} · Gap {data.surface_coverage.gap}
          </p>
        </Panel>

        <Panel className="p-5">
          <div className="flex items-center gap-2 justify-end text-xs font-bold text-muted-foreground mb-2">
            <Activity className="w-4 h-4" />
            نبض التشغيل
          </div>
          <p className="text-3xl font-black">{data.operational_pulse.domain_events_24h}</p>
          <p className="text-xs text-muted-foreground mt-2">
            أحداث 24 ساعة · {data.operational_pulse.connectors_total} موصل · {data.operational_pulse.openclaw_runs} تشغيلات
          </p>
        </Panel>
      </div>

      <Panel className="p-6 space-y-4">
        <div className="flex items-center gap-2 justify-end">
          <LineChart className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-black">الطبقات الخمس — من الرؤية إلى التنفيذ</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {data.planes.map((plane) => {
            const Icon = planeIcon(plane.id);
            return (
              <div key={plane.id} className="rounded-2xl border border-border/50 bg-background/30 p-5 space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${statusClasses(plane.status)}`}>
                    {statusLabel(plane.status)}
                  </span>
                  <div className="space-y-1 text-right">
                    <h3 className="font-black text-lg flex items-center gap-2 justify-end">
                      <Icon className="w-5 h-5 text-primary" />
                      {plane.title_ar}
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{plane.summary_ar}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div className="rounded-xl border border-border/50 bg-card/50 p-3">
                    <p className="text-[11px] font-bold text-muted-foreground mb-1">الوضع الحالي</p>
                    <p className="leading-relaxed">{plane.current_state_ar}</p>
                  </div>
                  <div className="rounded-xl border border-border/50 bg-card/50 p-3">
                    <p className="text-[11px] font-bold text-muted-foreground mb-1">الهدف</p>
                    <p className="leading-relaxed">{plane.target_state_ar}</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {plane.metrics.map((metric) => (
                    <div key={`${plane.id}-${metric.label_ar}`} className="rounded-xl border border-border/40 bg-secondary/20 p-3">
                      <p className="text-[11px] text-muted-foreground font-bold">{metric.label_ar}</p>
                      <p className="text-xl font-black mt-1">{metric.value}</p>
                      {metric.hint_ar && <p className="text-[11px] text-muted-foreground mt-2 leading-relaxed">{metric.hint_ar}</p>}
                    </div>
                  ))}
                </div>

                <div>
                  <p className="text-[11px] font-bold text-muted-foreground mb-2">مصادر الإثبات</p>
                  <div className="flex flex-wrap gap-2 justify-end">
                    {plane.evidence_sources.map((source) => (
                      <span key={source} className="text-[11px] px-2 py-1 rounded-full border border-border/50 bg-background/40 dir-ltr">
                        {source}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Panel>

      <Panel className="p-6 space-y-4">
        <div className="flex items-center gap-2 justify-end">
          <Building2 className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-black">أنظمة التشغيل المؤسسية الستة</h2>
        </div>
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {data.business_systems.map((system) => {
            const Icon = systemIcon(system.id);
            return (
              <div key={system.id} className="rounded-2xl border border-border/50 bg-background/30 p-5 space-y-4">
                <div className="flex items-start justify-between gap-3">
                  <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${statusClasses(system.status)}`}>
                    {statusLabel(system.status)}
                  </span>
                  <div className="space-y-1">
                    <h3 className="font-black text-lg flex items-center gap-2 justify-end">
                      <Icon className="w-5 h-5 text-primary" />
                      {system.title_ar}
                    </h3>
                    <p className="text-sm text-muted-foreground leading-relaxed">{system.summary_ar}</p>
                  </div>
                </div>

                <div>
                  <p className="text-[11px] font-bold text-muted-foreground mb-2">المراحل</p>
                  <div className="flex flex-wrap gap-2 justify-end">
                    {system.stages.map((stage) => (
                      <span key={stage} className="text-[11px] px-2 py-1 rounded-full border border-border/50 bg-secondary/30">
                        {stage}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
                    <p className="text-xs font-bold text-emerald-200 mb-2">المؤتمت الآن</p>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {system.automation_now.length ? (
                        system.automation_now.map((item) => <li key={item}>• {item}</li>)
                      ) : (
                        <li>• لا يوجد سطح حي كافٍ بعد.</li>
                      )}
                    </ul>
                  </div>
                  <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
                    <p className="text-xs font-bold text-amber-100 mb-2">بوابات الاعتماد</p>
                    <ul className="space-y-1 text-sm text-muted-foreground">
                      {system.approval_gates.map((item) => (
                        <li key={item}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Panel>

      <Panel className="p-6 space-y-4">
        <div className="flex items-center gap-2 justify-end">
          <Layers className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-black">الأسطح الحية المطلوبة</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {data.live_surfaces.map((surface) => (
            <div key={surface.id} className="rounded-2xl border border-border/50 bg-background/30 p-5 space-y-3">
              <div className="flex items-start justify-between gap-3">
                <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${statusClasses(surface.status)}`}>
                  {statusLabel(surface.status)}
                </span>
                <div className="space-y-1">
                  <h3 className="font-black text-base">{surface.title_ar}</h3>
                  <p className="text-xs text-primary/90">{surface.plane_owner_ar}</p>
                </div>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">{surface.note_ar}</p>
              <div className="space-y-2 text-[11px] text-muted-foreground">
                {surface.route_hint && (
                  <p className="dir-ltr">
                    Route: <span className="text-foreground">{surface.route_hint}</span>
                  </p>
                )}
                {surface.api_hint && (
                  <p className="dir-ltr">
                    API: <span className="text-foreground">{surface.api_hint}</span>
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </Panel>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <Panel className="p-6 space-y-4">
          <div className="flex items-center gap-2 justify-end">
            <Lock className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-black">عقود القرار الحساسة</h2>
          </div>
          <div className="space-y-3">
            {data.decision_metadata_classes.map((item) => (
              <div key={`${item.family}-${item.code}`} className="rounded-2xl border border-border/50 bg-background/30 p-4 space-y-2">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-[11px] px-2 py-1 rounded-full border border-border/50 bg-secondary/30">
                    {familyLabel(item.family)}
                  </span>
                  <div>
                    <p className="font-black">
                      {item.code} — {item.label_ar}
                    </p>
                    <p className="text-xs text-muted-foreground">{item.mode_ar}</p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 justify-end">
                  {item.examples.map((example) => (
                    <span key={example} className="text-[11px] px-2 py-1 rounded-full border border-border/50 bg-background/40">
                      {example}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel className="p-6 space-y-4">
          <div className="flex items-center gap-2 justify-end">
            <Scale className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-black">Saudi / AI Compliance Matrix</h2>
          </div>
          <div className="space-y-3">
            {data.compliance_matrix.map((item) => (
              <div key={item.id} className="rounded-2xl border border-border/50 bg-background/30 p-4 space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <span className={`text-[11px] font-bold px-2 py-1 rounded-full border ${statusClasses(item.status)}`}>
                    {statusLabel(item.status)}
                  </span>
                  <div className="space-y-1">
                    <p className="font-black">{item.title_ar}</p>
                    <p className="text-sm text-muted-foreground leading-relaxed">{item.control_ar}</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed">{item.note_ar}</p>
              </div>
            ))}
          </div>
        </Panel>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <Panel className="p-6 space-y-4">
          <div className="flex items-center gap-2 justify-end">
            <ShieldCheck className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-black">حدود الأتمتة المؤسسية</h2>
          </div>
          <div className="space-y-3">
            {data.automation_policy.map((bucket) => (
              <div
                key={bucket.id}
                className={`rounded-2xl border p-4 ${
                  bucket.mode === "auto"
                    ? "border-emerald-500/25 bg-emerald-500/5"
                    : "border-amber-500/25 bg-amber-500/5"
                }`}
              >
                <p className="font-black">{bucket.label_ar}</p>
                <div className="flex flex-wrap gap-2 justify-end mt-3">
                  {bucket.items.map((item) => (
                    <span key={item} className="text-[11px] px-2 py-1 rounded-full border border-border/50 bg-background/40">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Panel>

        <Panel className="p-6 space-y-4">
          <div className="flex items-center gap-2 justify-end">
            <BrainCircuit className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-black">{data.benchmark_harness.title_ar}</h2>
          </div>
          <div className={`rounded-2xl border p-4 ${statusClasses(data.benchmark_harness.status)}`}>
            <p className="text-sm leading-relaxed">{data.benchmark_harness.note_ar}</p>
            <div className="flex flex-wrap gap-2 justify-end mt-4">
              {data.benchmark_harness.metrics.map((metric) => (
                <span key={metric} className="text-[11px] px-2 py-1 rounded-full border border-white/15 bg-background/30">
                  {metric}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-border/50 bg-background/30 p-4">
            <div className="flex items-center gap-2 justify-end mb-3">
              <AlertTriangle className="w-4 h-4 text-amber-300" />
              <p className="font-black">Next Moves</p>
            </div>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {data.next_moves.map((item) => (
                <li key={item}>• {item}</li>
              ))}
            </ul>
          </div>
        </Panel>
      </div>

      <Panel className="p-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
          <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4">
            <CheckCircle2 className="w-5 h-5 text-emerald-300 mx-auto mb-2" />
            <p className="text-xs text-muted-foreground">أسطح حيّة</p>
            <p className="text-3xl font-black">{data.surface_coverage.live}</p>
          </div>
          <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-4">
            <ShieldCheck className="w-5 h-5 text-amber-200 mx-auto mb-2" />
            <p className="text-xs text-muted-foreground">تحتاج إكمال Foundation</p>
            <p className="text-3xl font-black">{data.surface_coverage.foundation}</p>
          </div>
          <div className="rounded-2xl border border-rose-500/20 bg-rose-500/5 p-4">
            <AlertTriangle className="w-5 h-5 text-rose-200 mx-auto mb-2" />
            <p className="text-xs text-muted-foreground">فجوات مباشرة</p>
            <p className="text-3xl font-black">{gapSurfaces}</p>
          </div>
        </div>
      </Panel>
    </div>
  );
}

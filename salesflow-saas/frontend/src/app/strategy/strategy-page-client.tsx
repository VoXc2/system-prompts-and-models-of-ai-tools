"use client";

import Link from "next/link";
import {
  Target,
  Shield,
  Zap,
  Globe2,
  TrendingUp,
  AlertTriangle,
  FileDown,
  ArrowLeft,
  Layers,
  BarChart3,
  Users,
  Sparkles,
  Loader2,
  BookOpen,
  Lock,
  Workflow,
  Building2,
  CheckCircle2,
  GitBranch,
  ListChecks,
} from "lucide-react";
import { useStrategySummary } from "@/hooks/use-strategy-summary";
import { getApiBaseUrl } from "@/lib/api-base";

const moatIcons = [Globe2, Shield, Layers, Zap, Sparkles];

const STATIC_MOAT = [
  {
    title: "سياق سعودي حقيقي",
    desc: "عربي أولاً، SAR، زاتكا/فوترة ضمن المسار، واتساب كقناة تشغيل لا كملحق.",
    icon: Globe2,
  },
  {
    title: "حوكمة وليس مجرد أتمتة",
    desc: "موافقات قبل الإرسال الحساس، عزل متعدد المستأجرين، سجلات تدقيق قابلة للتوسع.",
    icon: Shield,
  },
  {
    title: "تشغيل إيرادات كامل",
    desc: "من الاكتشاف إلى التحصيل والتحليلات — وليس شات بوت معزول عن CRM والدفع.",
    icon: Layers,
  },
  {
    title: "تكاملات مفتوحة",
    desc: "مسار Salesforce/CRM، Stripe، توقيع، صوت — تقليل قفل المنصة الواحدة.",
    icon: Zap,
  },
];

const competitors = [
  { cat: "CRM + وكلاء", ex: "Salesforce / Agentforce", them: "عمق CRM، مؤسسات", gap: "تكلفة واعتماد بيانات داخل CRM" },
  { cat: "ذكاء إيرادات", ex: "Gong ونظيرات الفئة", them: "مكالمات، تدريب، توقعات", gap: "سيناريوهات محلية/قنوات مختلطة" },
  { cat: "تسلسلات مبيعات", ex: "Outreach ونظيراتها", them: "أتمتة قوية", gap: "تعقيد وتكوين غربي أحياناً" },
  { cat: "وكلاء SDR مستقلون", ex: "11x، Tario…", them: "صيد وقنوات", gap: "حوكمة متعددة مستأجرين + امتثال محلي" },
];

const STATIC_PHASES = [
  { n: "0", t: "أساس التشغيل", d: "0–90 يوماً", items: ["CI واختبارات حرجة", "مراقبة وAPI صحة", "عميل مرجعي pilot", "روابط تسويق موحّدة"] },
  { n: "1", t: "تمييز تنفيذي", d: "3–9 أشهر", items: ["حوكمة أعمق", "CRM أولوية", "واتساب معتمد", "GTM بأرقام منسوبة"] },
  { n: "2", t: "توسع مؤسسي", d: "9–18 شهراً", items: ["امتثال/تخزين", "ذكاء إيرادات أوضح", "شراكات تكامل"] },
  { n: "3", t: "توسع جغرافي", d: "18–36 شهراً", items: ["خليج/قطاعات", "تكاملات استراتيجية"] },
];

const gapsClosing = {
  tech: ["مراقبة SLO وتكلفة LLM لكل مستأجر", "اختبارات حمل وانحدار", "زاتكا/ERP أعمق حسب ICP", "تجربة منتج موحّدة بصرياً"],
  business: ["مراجع عملاء بأرقام محافظة", "جملة تموضع واحدة", "شركاء بعقود وتدريب", "محتوى ثقة وخصوصية"],
};

const FALLBACK_QUOTE =
  "«ليس مجرد أداة — بل شركة مبيعات رقمية مؤتمتة بالذكاء الاصطناعي تعمل على مدار الساعة، تتطور ذاتياً، وتولد قيمة قابلة للقياس.»";

const FALLBACK_TARGETS = [
  { k: "النمو", v: "+3–5× إيرادات سنوياً (مقابل خط أساس لكل عميل)" },
  { k: "الكفاءة", v: "−70–80% عمل يدوي في مسار المبيعات" },
  { k: "التنبؤ", v: "دقة أعلى في أفق 30 يوماً (بيانات + معايرة)" },
  { k: "الدورة", v: "حوالي −40% زمن إغلاق نسبي للخط الأساسي" },
  { k: "الاكتساب", v: "حوالي −31% تكلفة اكتساب عبر الأتمتة" },
  { k: "الامتثال", v: "PDPL + ممارسات جاهزة لـ SOC2 للضوابط والسجلات" },
];

const FALLBACK_PLANES = [
  {
    id: "decision",
    name_ar: "Decision Plane",
    mission: "كشف الإشارات والتحليل والتوصية وتجهيز evidence packs مع HITL.",
    stack: ["Responses API", "Structured Outputs", "Function Calling / MCP", "LangGraph interrupts"],
  },
  {
    id: "execution",
    name_ar: "Execution Plane",
    mission: "تنفيذ الالتزامات الطويلة متعددة الأنظمة بشكل resilient وقابل للاستئناف.",
    stack: ["LangGraph loops", "Temporal workflows", "Idempotency + compensation"],
  },
  {
    id: "trust",
    name_ar: "Trust Plane",
    mission: "سياسات وتفويض وتدقيق والتحقق من الأفعال الفعلية.",
    stack: ["OPA", "OpenFGA", "Vault", "Keycloak"],
  },
  {
    id: "data",
    name_ar: "Data Plane",
    mission: "مصدر حقيقة موحّد بعقود بيانات وجودة وتتبّع.",
    stack: ["Postgres + pgvector", "Airbyte", "Great Expectations", "OpenTelemetry"],
  },
  {
    id: "operating",
    name_ar: "Operating Plane",
    mission: "قفل SDLC والإصدارات مع provenance قابل للتدقيق.",
    stack: ["GitHub rulesets", "Environments", "OIDC", "Artifact attestations"],
  },
];

const FALLBACK_PROGRAM_LOCKS = [
  "5 planes",
  "6 business tracks",
  "3 agent roles",
  "3 action classes",
  ">=3 approval classes",
  "4 reversibility classes",
  "sensitivity model required",
  "provenance/freshness/confidence trio",
];

const FALLBACK_BUSINESS_TRACKS = [
  { id: "revenue_os", name_ar: "Revenue OS", scope: ["capture→qualification", "outreach→proposal", "renewal/upsell motions"] },
  { id: "partnership_os", name_ar: "Partnership OS", scope: ["scouting", "fit scoring", "activation + scorecards"] },
  { id: "corpdev_os", name_ar: "M&A / CorpDev OS", scope: ["target sourcing", "DD orchestration", "investment memo/board pack"] },
  { id: "expansion_os", name_ar: "Expansion OS", scope: ["market scanning", "launch readiness", "actual vs forecast"] },
  { id: "pmi_pmo_os", name_ar: "PMI / PMO OS", scope: ["Day-1", "30/60/90", "synergy/risk tracking"] },
  { id: "executive_board_os", name_ar: "Executive / Board OS", scope: ["approval center", "risk heatmap", "portfolio governance"] },
];

const FALLBACK_MANDATORY_SURFACES = [
  "Executive Room",
  "Approval Center",
  "Evidence Pack Viewer",
  "Partner Room",
  "DD Room",
  "Risk Board",
  "Policy Violations Board",
  "Actual vs Forecast Dashboard",
  "Revenue Funnel Control Center",
  "Partnership Scorecards",
  "M&A Pipeline Board",
  "Expansion Launch Console",
  "PMI 30/60/90 Engine",
  "Tool Verification Ledger",
  "Connector Health Board",
  "Release Gate Dashboard",
  "Saudi Compliance Matrix",
  "Model Routing Dashboard",
];

const FALLBACK_AUTOMATION_POLICY = {
  full_auto: [
    "intake/enrichment/scoring",
    "memo drafting + evidence aggregation",
    "workflow kickoff + reminders + SLA tracking",
    "variance/anomaly detection",
    "connector sync + quality checks + telemetry",
  ],
  human_approval_required: [
    "term sheet sending",
    "signature request",
    "strategic partner activation",
    "market launch",
    "M&A offer",
    "policy-exception discount",
    "high-sensitivity data sharing",
    "production promotion",
    "capital commitments",
  ],
};

const FALLBACK_ROUTING = {
  lanes: [
    { id: "coding_lane", purpose: "coding and deterministic transformations" },
    { id: "executive_reasoning_lane", purpose: "board-grade reasoning and scenario analysis" },
    { id: "throughput_drafting_lane", purpose: "high-volume drafting and summarization" },
    { id: "fallback_lane", purpose: "resilience on provider degradation" },
  ],
  measured_metrics: ["latency", "schema adherence", "contradiction rate", "Arabic quality", "cost per successful task"],
};

const FALLBACK_CONNECTOR_CONTRACT = [
  "contract + version",
  "retry + timeout policy",
  "idempotency key",
  "approval policy",
  "audit mapping",
  "telemetry mapping",
  "rollback/compensation notes",
];

const FALLBACK_READINESS = [
  "business-critical decisions structured + evidence-backed + schema-bound",
  "long-running commitments durable + resumable + crash-tolerant",
  "sensitive actions tagged with approval/reversibility/sensitivity metadata",
  "connectors versioned with retry/idempotency/audit mapping",
  "releases gated via rulesets + environments + OIDC + provenance",
  "surfaces traceable with OTel + correlation IDs",
];

const FALLBACK_SAUDI_COMPLIANCE = [
  "PDPL controls mapping",
  "ECC/NCA cyber checkpoints",
  "NIST AI RMF lifecycle",
  "OWASP LLM Top 10 mitigations",
];

export function StrategyPageClient() {
  const { data, loading } = useStrategySummary();
  const api = getApiBaseUrl();

  const quote = data?.vision.tagline_ar ? `«${data.vision.tagline_ar}»` : FALLBACK_QUOTE;
  const auditableRows =
    data?.auditable_targets?.length ?
      data.auditable_targets.map((t) => ({ k: t.label_ar, v: t.target }))
    : FALLBACK_TARGETS;

  const moatCards =
    data?.moat_pillars?.length ?
      data.moat_pillars.map((text, i) => {
        const Icon = moatIcons[i % moatIcons.length];
        return { title: `محور تمييز ${i + 1}`, desc: text, icon: Icon };
      })
    : STATIC_MOAT.map((m) => ({ title: m.title, desc: m.desc, icon: m.icon }));

  const phaseBlocks =
    data?.execution_phases_detail?.length ?
      data.execution_phases_detail.map((p) => ({
        n: String(p.id),
        t: p.name_ar,
        d: p.window,
        items: p.deliverables,
      }))
    : STATIC_PHASES;

  const planes = data?.planes?.length ? data.planes : FALLBACK_PLANES;
  const programLockItems =
    data?.program_locks ?
      [
        `${data.program_locks.planes} planes`,
        `${data.program_locks.business_tracks} business tracks`,
        `${data.program_locks.agent_roles} agent roles`,
        `${data.program_locks.action_classes} action classes`,
        `>= ${data.program_locks.approval_classes_min} approval classes`,
        `${data.program_locks.reversibility_classes} reversibility classes`,
        `sensitivity model: ${data.program_locks.sensitivity_model}`,
        `trio: ${data.program_locks.provenance_freshness_confidence}`,
      ]
    : FALLBACK_PROGRAM_LOCKS;
  const businessTracks = data?.business_tracks?.length ? data.business_tracks : FALLBACK_BUSINESS_TRACKS;
  const mandatorySurfaces = data?.mandatory_surfaces?.length ? data.mandatory_surfaces : FALLBACK_MANDATORY_SURFACES;
  const automationPolicy = data?.automation_policy ?? FALLBACK_AUTOMATION_POLICY;
  const routingFabric = data?.routing_fabric ?? FALLBACK_ROUTING;
  const connectorContract =
    data?.connector_contract_requirements?.length ? data.connector_contract_requirements : FALLBACK_CONNECTOR_CONTRACT;
  const readinessDefinition = data?.readiness_definition?.length ? data.readiness_definition : FALLBACK_READINESS;
  const saudiCompliance = data?.saudi_compliance_matrix?.length ? data.saudi_compliance_matrix : FALLBACK_SAUDI_COMPLIANCE;

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-30%,rgba(13,148,136,0.22),transparent)]" />

      <header className="relative border-b border-white/10 bg-black/30 backdrop-blur-xl">
        <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-4 px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-teal-400 to-emerald-700 shadow-lg shadow-teal-900/40">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-400/90">Dealix Strategy</p>
              <h1 className="text-xl font-bold">الانتقال للمستوى التالي</h1>
              {data?.blueprint_version && (
                <p className="text-[10px] text-slate-500 mt-1">Blueprint {data.blueprint_version}</p>
              )}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {loading && (
              <span className="inline-flex items-center gap-1 text-xs text-slate-500">
                <Loader2 className="h-3 w-3 animate-spin" />
                تحديث من API
              </span>
            )}
            <Link
              href="/"
              className="inline-flex items-center gap-1 rounded-full border border-white/15 px-4 py-2 text-sm text-slate-300 hover:bg-white/5"
            >
              <ArrowLeft className="h-4 w-4 rotate-180" />
              الرئيسية
            </Link>
            <a
              href={`${api}/api/v1/strategy/summary`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 rounded-full border border-teal-500/40 bg-teal-950/50 px-4 py-2 text-sm text-teal-200 hover:bg-teal-900/40"
            >
              JSON API
            </a>
          </div>
        </div>
      </header>

      <main className="relative mx-auto max-w-5xl space-y-16 px-6 py-14">
        <section className="space-y-4">
          <p className="text-sm font-medium text-teal-400">ملخص تنفيذي</p>
          <blockquote className="rounded-2xl border border-teal-500/20 bg-teal-950/25 px-5 py-4 text-base italic leading-relaxed text-teal-100/95">
            {quote}
          </blockquote>
          <p className="text-lg leading-relaxed text-slate-300">
            <strong className="text-white">Dealix</strong> —{" "}
            {data?.positioning ??
              "نظام تشغيل إيرادات وعمليات يجمع الاكتشاف، التأهيل، القنوات، العروض، التحصيل، والتحليلات مع حوكمة وعزل متعدد المستأجرين."}
          </p>
        </section>

        <section>
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
            <BarChart3 className="h-5 w-5 text-teal-400" />
            مقاييس مستهدفة (قابلة للتدقيق)
            {data && <span className="text-xs font-normal text-teal-500/80">— مباشر من API</span>}
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {auditableRows.map((row) => (
              <div
                key={row.k + row.v}
                className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-right text-sm"
              >
                <p className="font-bold text-teal-300">{row.k}</p>
                <p className="mt-1 text-slate-400">{row.v}</p>
              </div>
            ))}
          </div>
          <p className="mt-3 text-xs text-slate-500">
            المعرفة والـ RAG داخل المنتج (PostgreSQL + pgvector) — بدون الاعتماد على منصات RAG خارجية كطبقة أساسية.
          </p>
        </section>

        {data?.design_principles && data.design_principles.length > 0 && (
          <section>
            <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
              <BookOpen className="h-5 w-5 text-teal-400" />
              مبادئ التصميم
            </h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {data.design_principles.map((pr) => (
                <div
                  key={pr.id}
                  className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-right text-sm"
                >
                  <p className="font-bold text-white">{pr.title_ar}</p>
                  <p className="mt-1 text-slate-400">{pr.summary}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <Target className="h-5 w-5 text-teal-400" />
            أضلاع التمييز (لماذا نتقدّم منطقياً)
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {moatCards.map((m) => (
              <div
                key={m.title + m.desc}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 transition hover:border-teal-500/35"
              >
                <m.icon className="mb-3 h-8 w-8 text-teal-400/90" />
                <h3 className="font-bold text-white">{m.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{m.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
            <BarChart3 className="h-5 w-5 text-teal-400" />
            إطار مقارنة معياري (ليس تطابقاً حرفياً)
          </h2>
          <div className="overflow-x-auto rounded-2xl border border-white/10">
            <table className="w-full min-w-[640px] text-right text-sm">
              <thead>
                <tr className="border-b border-white/10 bg-white/5">
                  <th className="p-3 font-semibold text-teal-200">الفئة</th>
                  <th className="p-3 font-semibold text-teal-200">أمثلة سوق</th>
                  <th className="p-3 font-semibold text-teal-200">قوتهم النموذجية</th>
                  <th className="p-3 font-semibold text-teal-200">فجوة نموذجية</th>
                </tr>
              </thead>
              <tbody>
                {competitors.map((r) => (
                  <tr key={r.cat} className="border-b border-white/5 text-slate-300">
                    <td className="p-3 font-medium text-white">{r.cat}</td>
                    <td className="p-3">{r.ex}</td>
                    <td className="p-3 text-slate-400">{r.them}</td>
                    <td className="p-3 text-slate-500">{r.gap}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-slate-500">
            {data?.market_frame ??
              "اتجاه السوق العالمي نحو «أنظمة إجراء» مدمجة بالذكاء (Revenue Action Orchestration) يفرض إظهار إجراءات قابلة للقياس وليس تقارير فقط."}
          </p>
        </section>

        <section>
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
            <TrendingUp className="h-5 w-5 text-teal-400" />
            ما نُغلقه من فجوات (تقني وغير تقني)
          </h2>
          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-2xl border border-emerald-500/20 bg-emerald-950/20 p-5">
              <h3 className="mb-3 font-bold text-emerald-200">تقني / منتج</h3>
              <ul className="space-y-2 text-sm text-slate-300">
                {gapsClosing.tech.map((x) => (
                  <li key={x} className="flex gap-2">
                    <span className="text-emerald-500">▸</span>
                    {x}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-2xl border border-cyan-500/20 bg-cyan-950/20 p-5">
              <h3 className="mb-3 font-bold text-cyan-200">تسويق / مبيعات / شراكات</h3>
              <ul className="space-y-2 text-sm text-slate-300">
                {gapsClosing.business.map((x) => (
                  <li key={x} className="flex gap-2">
                    <span className="text-cyan-500">▸</span>
                    {x}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </section>

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <Layers className="h-5 w-5 text-teal-400" />
            خارطة الطريق (مراحل)
            {data?.execution_phases_detail?.length ? (
              <span className="text-xs font-normal text-teal-500/80">— من API</span>
            ) : null}
          </h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {phaseBlocks.map((p) => (
              <div key={p.n} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                <div className="flex items-baseline justify-between gap-2">
                  <span className="text-2xl font-black text-teal-400">{p.n}</span>
                  <span className="text-xs text-slate-500">{p.d}</span>
                </div>
                <h3 className="mt-1 font-bold text-white">{p.t}</h3>
                <ul className="mt-3 space-y-1.5 text-sm text-slate-400">
                  {p.items.map((i) => (
                    <li key={i}>• {i}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-5 flex items-center gap-2 text-lg font-bold text-white">
            <Workflow className="h-5 w-5 text-teal-400" />
            الـ 5 Planes السيادية
          </h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {planes.map((plane) => (
              <div key={plane.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                <p className="text-sm font-bold text-teal-200">{plane.name_ar}</p>
                <p className="mt-2 text-xs leading-relaxed text-slate-400">{plane.mission}</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {plane.stack.map((item) => (
                    <span key={item} className="rounded-full border border-white/10 bg-black/30 px-2 py-1 text-[10px] text-slate-300">
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-white">
              <Lock className="h-5 w-5 text-teal-400" />
              Program Locks
            </h2>
            <ul className="space-y-2 text-sm text-slate-300">
              {programLockItems.map((item) => (
                <li key={item} className="flex gap-2">
                  <span className="text-teal-400">▸</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
            <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-white">
              <Building2 className="h-5 w-5 text-teal-400" />
              المسارات التشغيلية الستة
            </h2>
            <div className="space-y-3">
              {businessTracks.map((track) => (
                <div key={track.id} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2">
                  <p className="text-sm font-bold text-white">{track.name_ar}</p>
                  <p className="mt-1 text-xs text-slate-400">{track.scope.join(" • ")}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section>
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
            <ListChecks className="h-5 w-5 text-teal-400" />
            الأسطح الإلزامية داخل المنتج
          </h2>
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {mandatorySurfaces.map((surface) => (
              <div
                key={surface}
                className="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-slate-300"
              >
                {surface}
              </div>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-emerald-500/25 bg-emerald-950/20 p-5">
            <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-emerald-100">
              <CheckCircle2 className="h-5 w-5" />
              حدود الأتمتة (ما يُؤتمت وما يعتمد)
            </h2>
            <div className="space-y-4">
              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-wide text-emerald-300">يُؤتمت بالكامل</p>
                <ul className="space-y-1 text-sm text-slate-200">
                  {automationPolicy.full_auto.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="mb-2 text-xs font-bold uppercase tracking-wide text-amber-300">اعتماد إلزامي</p>
                <ul className="space-y-1 text-sm text-amber-100/90">
                  {automationPolicy.human_approval_required.map((item) => (
                    <li key={item}>• {item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-cyan-500/25 bg-cyan-950/20 p-5">
            <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-cyan-100">
              <GitBranch className="h-5 w-5" />
              Sovereign Routing + Connector Contracts
            </h2>
            <p className="mb-2 text-xs font-bold uppercase tracking-wide text-cyan-300">Routing lanes</p>
            <ul className="space-y-1 text-sm text-slate-200">
              {routingFabric.lanes.map((lane) => (
                <li key={lane.id}>
                  • <span className="font-semibold">{lane.id}:</span> {lane.purpose}
                </li>
              ))}
            </ul>
            <p className="mb-2 mt-4 text-xs font-bold uppercase tracking-wide text-cyan-300">Measured metrics</p>
            <p className="text-sm text-slate-200">{routingFabric.measured_metrics.join(" • ")}</p>
            <p className="mb-2 mt-4 text-xs font-bold uppercase tracking-wide text-cyan-300">Connector contract</p>
            <p className="text-sm text-slate-200">{connectorContract.join(" • ")}</p>
          </div>
        </section>

        <section className="rounded-2xl border border-teal-500/20 bg-teal-950/20 p-6">
          <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-teal-100">
            <Shield className="h-5 w-5" />
            تعريف الجاهزية النهائية + مصفوفة السعودية
          </h2>
          <ul className="space-y-2 text-sm text-slate-200">
            {readinessDefinition.map((item) => (
              <li key={item} className="flex gap-2">
                <span className="text-teal-300">▸</span>
                {item}
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs font-bold uppercase tracking-wide text-teal-300">Saudi compliance matrix</p>
          <p className="mt-1 text-sm text-slate-300">{saudiCompliance.join(" • ")}</p>
        </section>

        <section className="rounded-2xl border border-amber-500/25 bg-amber-950/20 p-6">
          <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-amber-100">
            <AlertTriangle className="h-5 w-5" />
            مخاطر يجب إدارتها بصراحة
          </h2>
          <ul className="space-y-2 text-sm text-amber-100/80">
            <li>• تكلفة LLM والقنوات الخارجية إن لم تُحسب لكل مستأجر.</li>
            <li>• تعميق وكلاء CRM العالميين — التمييز بالمحلية والامتثال والسرعة.</li>
            <li>• أي إرسال تسويقي يحتاج سياسة وموافقات (واتساب، بريد، خصوصية).</li>
          </ul>
        </section>

        <section className="rounded-2xl border border-teal-500/30 bg-gradient-to-br from-teal-950/40 to-slate-900/60 p-8">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
            <FileDown className="h-5 w-5 text-teal-300" />
            الوثيقة الكاملة والروابط السريعة
          </h2>
          <p className="mb-6 text-sm text-slate-400">
            النسخة الكاملة Markdown تُحدَّث في المستودع وتُنسَخ تلقائياً إلى{" "}
            <code className="rounded bg-black/30 px-1.5 py-0.5">public/strategy/</code> عند المزامنة.
          </p>
          <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap">
            <a
              href="/strategy/DEALIX_NEXT_LEVEL_MASTER_PLAN_AR.md"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-500 px-6 py-3 text-sm font-bold text-slate-950 hover:bg-teal-400"
            >
              <FileDown className="h-4 w-4" />
              وثيقة المستوى التالي (.md)
            </a>
            <a
              href="/strategy/ULTIMATE_EXECUTION_MASTER_AR.md"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-teal-500/50 bg-teal-950/40 px-6 py-3 text-sm font-bold text-teal-100 hover:bg-teal-900/50"
            >
              <FileDown className="h-4 w-4" />
              وثيقة التنفيذ السيادي v5 (.md)
            </a>
            <a
              href="/strategy/INTEGRATION_MASTER_AR.md"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-950/30 px-6 py-3 text-sm font-bold text-emerald-100 hover:bg-emerald-900/40"
            >
              <FileDown className="h-4 w-4" />
              ملف الربط الشامل — التكاملات والإطلاق (.md)
            </a>
            <Link
              href="/investors"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/20 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10"
            >
              عرض المستثمرين (PDF)
            </Link>
            <Link
              href="/marketers"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/20 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10"
            >
              <Users className="h-4 w-4" />
              بوابة المسوّقين
            </Link>
            <Link
              href="/resources"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/20 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10"
            >
              الموارد والـ ZIP
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/20 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10"
            >
              لوحة التشغيل
            </Link>
          </div>
        </section>

        <footer className="border-t border-white/10 pb-12 pt-8 text-center text-xs text-slate-600">
          وثائق حية — راجع ربع سنوياً. المصدر:{" "}
          <code className="text-slate-500">docs/DEALIX_NEXT_LEVEL_MASTER_PLAN_AR.md</code>،{" "}
          <code className="text-slate-500">docs/ULTIMATE_EXECUTION_MASTER_AR.md</code>،{" "}
          <code className="text-slate-500">docs/INTEGRATION_MASTER_AR.md</code>،{" "}
          <code className="text-slate-500">MASTER-BLUEPRINT.mdc</code>
        </footer>
      </main>
    </div>
  );
}

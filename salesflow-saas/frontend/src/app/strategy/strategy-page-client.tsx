"use client";

import Link from "next/link";
import {
  Shield,
  Zap,
  AlertTriangle,
  FileDown,
  ArrowLeft,
  Layers,
  BarChart3,
  Users,
  Sparkles,
  Loader2,
  BookOpen,
  Workflow,
  Database,
  GitBranch,
  LockKeyhole,
  CheckCircle2,
  BadgeCheck,
  Radar,
  Network,
} from "lucide-react";
import { useStrategySummary } from "@/hooks/use-strategy-summary";
import type { OperatingSurfaceStatus } from "@/lib/strategy-summary";
import { STRATEGY_SUMMARY_FALLBACK } from "@/lib/strategy-fallback";
import { getApiBaseUrl } from "@/lib/api-base";

const moatIcons = [Shield, Layers, Workflow, Sparkles, Zap];
const planeIcons = [Radar, Workflow, LockKeyhole, Database, GitBranch];

const surfaceStatusMeta: Record<
  OperatingSurfaceStatus,
  { label: string; className: string }
> = {
  repo_anchor: {
    label: "مرتكز حالي بالمستودع",
    className: "border-emerald-500/30 bg-emerald-950/30 text-emerald-200",
  },
  build_next: {
    label: "أغلقه الآن داخل المنتج",
    className: "border-amber-500/30 bg-amber-950/30 text-amber-100",
  },
  target_required: {
    label: "سطح إلزامي قبل الجاهزية",
    className: "border-sky-500/30 bg-sky-950/30 text-sky-100",
  },
};

export function StrategyPageClient() {
  const { data, loading, source } = useStrategySummary();
  const api = getApiBaseUrl();
  const summary = data ?? STRATEGY_SUMMARY_FALLBACK;
  const isLive = source === "live";

  const quote = `«${summary.vision.tagline_ar}»`;
  const auditableRows = summary.auditable_targets.map((target) => ({
    k: target.label_ar,
    v: target.target,
  }));
  const moatCards = summary.moat_pillars.map((text, index) => ({
    title: `محور تمييز ${index + 1}`,
    desc: text,
    icon: moatIcons[index % moatIcons.length],
  }));
  const phaseBlocks = summary.execution_phases_detail.map((phase) => ({
    n: String(phase.id),
    t: phase.name_ar,
    d: phase.window,
    items: phase.deliverables,
  }));
  const ownerLabelById = new Map([
    ...summary.business_tracks.map((track) => [track.id, track.name_ar] as const),
    ...summary.planes.map((plane) => [plane.id, plane.name_ar] as const),
  ]);

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
              <h1 className="text-xl font-bold">السيادة المؤسسية الكاملة</h1>
              {summary.blueprint_version && (
                <p className="text-[10px] text-slate-500 mt-1">Blueprint {summary.blueprint_version}</p>
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
            <span
              className={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-[10px] ${
                isLive ?
                  "border-emerald-500/40 bg-emerald-950/30 text-emerald-200"
                : "border-white/10 bg-white/5 text-slate-400"
              }`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${isLive ? "bg-emerald-400" : "bg-slate-500"}`} />
              {isLive ? "Live contract" : "Embedded fallback"}
            </span>
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
            {summary.positioning}
          </p>
        </section>

        <section>
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
            <BarChart3 className="h-5 w-5 text-teal-400" />
            مقاييس مستهدفة (قابلة للتدقيق)
            {isLive && <span className="text-xs font-normal text-teal-500/80">— مباشر من API</span>}
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

        <section className="rounded-2xl border border-teal-500/25 bg-teal-950/20 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
            <Shield className="h-5 w-5 text-teal-400" />
            النموذج السيادي التشغيلي
          </h2>
          <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
            <div className="space-y-3">
              <p className="text-xl font-bold text-white">{summary.sovereign_model.name}</p>
              <p className="text-sm leading-7 text-slate-300">{summary.sovereign_model.thesis_ar}</p>
              <blockquote className="rounded-2xl border border-white/10 bg-black/20 px-4 py-4 text-base text-teal-100">
                {summary.sovereign_model.operating_rule_ar}
              </blockquote>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Current market frame</p>
              <p className="mt-3 text-sm leading-7 text-slate-300">{summary.market_frame}</p>
            </div>
          </div>
        </section>

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <Sparkles className="h-5 w-5 text-teal-400" />
            ما الذي يصنع الهيمنة فعلًا؟
          </h2>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            {moatCards.map((card) => (
              <div
                key={card.title}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 transition hover:border-teal-500/35"
              >
                <card.icon className="mb-3 h-8 w-8 text-teal-400/90" />
                <h3 className="font-bold text-white">{card.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{card.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <Layers className="h-5 w-5 text-teal-400" />
            البنية الكبرى: 5 planes
          </h2>
          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
            {summary.planes.map((plane, index) => {
              const Icon = planeIcons[index % planeIcons.length];
              return (
                <div
                  key={plane.id}
                  className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-[11px] uppercase tracking-[0.2em] text-teal-400/90">{plane.name_en}</p>
                      <h3 className="mt-1 text-lg font-bold text-white">{plane.name_ar}</h3>
                    </div>
                    <Icon className="h-6 w-6 shrink-0 text-teal-400" />
                  </div>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{plane.mission}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {plane.capabilities.map((capability) => (
                      <span
                        key={capability}
                        className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-slate-300"
                      >
                        {capability}
                      </span>
                    ))}
                  </div>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {plane.building_blocks.map((block) => (
                      <span
                        key={block}
                        className="rounded-full border border-teal-500/20 bg-teal-950/30 px-3 py-1 text-xs text-teal-100"
                      >
                        {block}
                      </span>
                    ))}
                  </div>
                  <p className="mt-4 text-sm font-medium text-emerald-200">{plane.outcome}</p>
                </div>
              );
            })}
          </div>
        </section>

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <Network className="h-5 w-5 text-teal-400" />
            المنتج الكامل: 6 business tracks
          </h2>
          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
            {summary.business_tracks.map((track) => (
              <div
                key={track.id}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"
              >
                <h3 className="text-lg font-bold text-white">{track.name_ar}</h3>
                <ul className="mt-4 space-y-2 text-sm text-slate-300">
                  {track.scope.map((item) => (
                    <li key={item} className="flex gap-2">
                      <span className="text-teal-400">▸</span>
                      {item}
                    </li>
                  ))}
                </ul>
                <div className="mt-4 rounded-xl border border-teal-500/20 bg-teal-950/20 p-3 text-sm text-teal-100">
                  <p className="font-semibold text-white">نمط الأتمتة</p>
                  <p className="mt-1 leading-7">{track.automation_mode}</p>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {track.primary_surfaces.map((surface) => (
                    <span
                      key={surface}
                      className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-slate-300"
                    >
                      {surface}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <LockKeyhole className="h-5 w-5 text-teal-400" />
            Program locks + action governance
          </h2>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs text-slate-500">Planes</p>
              <p className="mt-2 text-3xl font-black text-white">{summary.program_locks.counts.planes}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs text-slate-500">Business tracks</p>
              <p className="mt-2 text-3xl font-black text-white">{summary.program_locks.counts.business_tracks}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <p className="text-xs text-slate-500">Agent roles</p>
              <p className="mt-2 text-3xl font-black text-white">{summary.program_locks.counts.agent_roles}</p>
            </div>
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <h3 className="font-bold text-white">Action classes</h3>
              <div className="mt-4 space-y-3">
                {summary.program_locks.action_classes.map((item) => (
                  <div key={item.id}>
                    <p className="font-semibold text-teal-200">{item.label_ar}</p>
                    <p className="mt-1 text-sm text-slate-400">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <h3 className="font-bold text-white">Approval classes</h3>
              <div className="mt-4 space-y-3">
                {summary.program_locks.approval_classes.map((item) => (
                  <div key={item.id}>
                    <p className="font-semibold text-amber-100">{item.label_ar}</p>
                    <p className="mt-1 text-sm text-slate-400">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
              <h3 className="font-bold text-white">Reversibility classes</h3>
              <div className="mt-4 space-y-3">
                {summary.program_locks.reversibility_classes.map((item) => (
                  <div key={item.id}>
                    <p className="font-semibold text-sky-100">{item.label_ar}</p>
                    <p className="mt-1 text-sm text-slate-400">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <div className="rounded-2xl border border-emerald-500/20 bg-emerald-950/20 p-5">
              <h3 className="font-bold text-emerald-100">يُؤتمت بالكامل</h3>
              <div className="mt-4 flex flex-wrap gap-2">
                {summary.automation_policy.fully_automated.map((item) => (
                  <span
                    key={item}
                    className="rounded-full border border-emerald-500/30 bg-black/20 px-3 py-1 text-xs text-emerald-100"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
            <div className="rounded-2xl border border-amber-500/20 bg-amber-950/20 p-5">
              <h3 className="font-bold text-amber-100">يُؤتمت مع اعتماد إلزامي</h3>
              <div className="mt-4 flex flex-wrap gap-2">
                {summary.automation_policy.approval_required.map((item) => (
                  <span
                    key={item}
                    className="rounded-full border border-amber-500/30 bg-black/20 px-3 py-1 text-xs text-amber-100"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-5">
            <h3 className="font-bold text-white">Metadata trio + sensitivity model</h3>
            <div className="mt-4 flex flex-wrap gap-2">
              {summary.program_locks.metadata_trio.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-teal-500/30 bg-teal-950/30 px-3 py-1 text-xs text-teal-100"
                >
                  {item}
                </span>
              ))}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {summary.program_locks.sensitivity_levels.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        </section>

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <BadgeCheck className="h-5 w-5 text-teal-400" />
            الأسطح الحيّة الإلزامية داخل المنتج
          </h2>
          <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-3">
            {summary.operating_surfaces.map((surface) => {
              const status = surfaceStatusMeta[surface.status];
              const owner = ownerLabelById.get(surface.owner_track) ?? surface.owner_track;
              return (
                <div
                  key={surface.id}
                  className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className="font-bold text-white">{surface.name_ar}</h3>
                    <span
                      className={`rounded-full border px-3 py-1 text-[11px] ${status.className}`}
                    >
                      {status.label}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-slate-500">{owner}</p>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{surface.summary}</p>
                </div>
              );
            })}
          </div>
        </section>

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <Zap className="h-5 w-5 text-teal-400" />
            Sovereign routing fabric
          </h2>
          <div className="grid gap-4 lg:grid-cols-2">
            {summary.routing_fabric.lanes.map((lane) => (
              <div
                key={lane.id}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"
              >
                <h3 className="text-lg font-bold text-white">{lane.name_ar}</h3>
                <p className="mt-2 text-sm leading-7 text-slate-300">{lane.purpose}</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {lane.models.map((model) => (
                    <span
                      key={model}
                      className="rounded-full border border-teal-500/20 bg-teal-950/30 px-3 py-1 text-xs text-teal-100"
                    >
                      {model}
                    </span>
                  ))}
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {lane.optimize_for.map((metric) => (
                    <span
                      key={metric}
                      className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-slate-300"
                    >
                      {metric}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-5">
            <p className="text-sm font-semibold text-white">Scorecard المفروض قياسه لكل lane</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {summary.routing_fabric.scorecard.map((metric) => (
                <span
                  key={metric}
                  className="rounded-full border border-sky-500/20 bg-sky-950/30 px-3 py-1 text-xs text-sky-100"
                >
                  {metric}
                </span>
              ))}
            </div>
          </div>
        </section>

        {summary.design_principles.length > 0 && (
          <section>
            <h2 className="mb-4 flex items-center gap-2 text-lg font-bold text-white">
              <BookOpen className="h-5 w-5 text-teal-400" />
              مبادئ التصميم
            </h2>
            <div className="grid gap-3 sm:grid-cols-2">
              {summary.design_principles.map((pr) => (
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
            <CheckCircle2 className="h-5 w-5 text-teal-400" />
            تعريف الجاهزية النهائية
          </h2>
          <div className="grid gap-3">
            {summary.readiness_definition.map((item) => (
              <div
                key={item}
                className="flex items-start gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4"
              >
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />
                <p className="text-sm leading-7 text-slate-300">{item}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-6 flex items-center gap-2 text-lg font-bold text-white">
            <Layers className="h-5 w-5 text-teal-400" />
            خارطة الطريق (مراحل)
            {summary.execution_phases_detail.length ? (
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
              href={summary.doc_paths.full_markdown_web}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-teal-500 px-6 py-3 text-sm font-bold text-slate-950 hover:bg-teal-400"
            >
              <FileDown className="h-4 w-4" />
              وثيقة المستوى التالي (.md)
            </a>
            <a
              href={summary.doc_paths.sovereign_operating_model_ar}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-fuchsia-500/40 bg-fuchsia-950/30 px-6 py-3 text-sm font-bold text-fuchsia-100 hover:bg-fuchsia-900/40"
            >
              <FileDown className="h-4 w-4" />
              المرجع السيادي الكامل (.md)
            </a>
            <a
              href={summary.doc_paths.ultimate_execution_ar}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-teal-500/50 bg-teal-950/40 px-6 py-3 text-sm font-bold text-teal-100 hover:bg-teal-900/50"
            >
              <FileDown className="h-4 w-4" />
              وثيقة التنفيذ الشاملة v4 (.md)
            </a>
            <a
              href={summary.doc_paths.integration_master_ar}
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
          <code className="text-slate-500">docs/SOVEREIGN_ENTERPRISE_GROWTH_OS_AR.md</code>،{" "}
          <code className="text-slate-500">docs/ULTIMATE_EXECUTION_MASTER_AR.md</code>،{" "}
          <code className="text-slate-500">docs/INTEGRATION_MASTER_AR.md</code>،{" "}
          <code className="text-slate-500">MASTER-BLUEPRINT.mdc</code>
        </footer>
      </main>
    </div>
  );
}

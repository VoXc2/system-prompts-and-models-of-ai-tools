"use client";

import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  BarChart3,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  ChevronDown,
  Clock,
  Cpu,
  FileCheck,
  FileText,
  Filter,
  Gauge,
  GitBranch,
  Globe,
  Handshake,
  HeartPulse,
  Layers,
  Lock,
  Network,
  PackageCheck,
  Plug,
  Rocket,
  Scale,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  Workflow,
  XCircle,
  Zap,
} from "lucide-react";

/* ─────────────── shared helpers ─────────────── */

const S = ({ label, value, sub, icon: Icon, color = "text-primary", bg = "bg-primary/10" }: {
  label: string; value: string | number; sub?: string;
  icon: React.ComponentType<{ className?: string }>; color?: string; bg?: string;
}) => (
  <div className="rounded-2xl border border-border bg-card/50 p-5 flex items-start gap-4">
    <div className={`p-3 rounded-xl ${bg} shrink-0`}><Icon className={`w-5 h-5 ${color}`} /></div>
    <div className="text-right flex-1 min-w-0">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-xl font-bold mt-1">{value}</p>
      {sub && <p className="text-[11px] text-muted-foreground mt-0.5">{sub}</p>}
    </div>
  </div>
);

const H = ({ ar, en, icon: Icon }: { ar: string; en: string; icon: React.ComponentType<{ className?: string }> }) => (
  <div className="flex items-center gap-3 mb-6">
    <div className="p-2.5 rounded-xl bg-primary/10"><Icon className="w-5 h-5 text-primary" /></div>
    <div className="text-right">
      <h1 className="text-2xl font-bold tracking-tight">{ar}</h1>
      <p className="text-xs text-muted-foreground">{en}</p>
    </div>
  </div>
);

const Badge = ({ children, c = "bg-primary/10 text-primary" }: { children: React.ReactNode; c?: string }) => (
  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${c}`}>{children}</span>
);

/* ═══════════════ 1. ExecutiveRoomView ═══════════════ */

export function ExecutiveRoomView() {
  const planes = [
    { name: "المستوى الاستراتيجي (Strategy)", color: "bg-emerald-500" },
    { name: "المستوى التنفيذي (Execution)", color: "bg-blue-500" },
    { name: "مستوى البيانات (Data)", color: "bg-purple-500" },
    { name: "مستوى الامتثال (Compliance)", color: "bg-amber-500" },
    { name: "مستوى البنية التحتية (Infra)", color: "bg-cyan-500" },
  ];
  const modules = [
    { name: "محرك القرارات", en: "Decision Engine", icon: BrainCircuit },
    { name: "مركز الاعتمادات", en: "Approval Center", icon: CheckCircle2 },
    { name: "غرفة الشراكات", en: "Partner Room", icon: Handshake },
    { name: "لوحة المخاطر", en: "Risk Board", icon: AlertTriangle },
    { name: "الامتثال السعودي", en: "Saudi Compliance", icon: ShieldCheck },
    { name: "توجيه النماذج", en: "Model Routing", icon: Cpu },
  ];
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="غرفة القيادة التنفيذية" en="Executive Room — Sovereign OS" icon={Sparkles} />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <S label="القرارات النشطة (Active Decisions)" value={12} icon={Target} color="text-emerald-500" bg="bg-emerald-500/10" />
        <S label="سير العمل النشط (Active Workflows)" value={7} icon={Workflow} color="text-blue-500" bg="bg-blue-500/10" />
        <S label="في انتظار الاعتماد (Pending Approvals)" value={5} icon={Clock} color="text-amber-500" bg="bg-amber-500/10" />
        <S label="درجة الامتثال (Compliance Score)" value="94%" icon={ShieldCheck} color="text-primary" />
      </div>

      <section>
        <h2 className="text-lg font-bold mb-3">حالة الطبقات (Planes Status)</h2>
        <div className="flex flex-wrap gap-3">
          {planes.map((p) => (
            <div key={p.name} className="flex items-center gap-2 rounded-xl border border-border bg-card/50 px-4 py-2.5">
              <span className={`w-2.5 h-2.5 rounded-full ${p.color}`} />
              <span className="text-sm">{p.name}</span>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-bold mb-3">وحدات النظام (OS Modules)</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {modules.map((m) => (
            <div key={m.name} className="rounded-2xl border border-border bg-card/50 p-5 flex items-center gap-3 hover:border-primary/40 transition-colors cursor-pointer">
              <m.icon className="w-5 h-5 text-primary shrink-0" />
              <div className="text-right">
                <p className="text-sm font-semibold">{m.name}</p>
                <p className="text-[11px] text-muted-foreground">{m.en}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-bold mb-3">إجراءات سريعة (Quick Actions)</h2>
        <div className="flex flex-wrap gap-3">
          {["إنشاء قرار جديد", "مراجعة الاعتمادات", "تقرير الامتثال", "فحص المخاطر"].map((a) => (
            <button key={a} className="px-4 py-2 rounded-xl bg-primary/10 text-primary text-sm font-medium hover:bg-primary/20 transition-colors">
              {a}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

/* ═══════════════ 2. ApprovalCenterView ═══════════════ */

export function ApprovalCenterView() {
  const approvals = [
    { id: "APR-001", title: "إضافة موصل HubSpot", class: "R1", requester: "أحمد", date: "2026-04-14", type: "workflow" },
    { id: "APR-002", title: "نشر إصدار v2.4.1", class: "R2", requester: "سالم", date: "2026-04-13", type: "decision" },
    { id: "APR-003", title: "تغيير سياسة PDPL", class: "R3", requester: "نورة", date: "2026-04-12", type: "workflow" },
    { id: "APR-004", title: "ترقية نموذج الذكاء الاصطناعي", class: "R0", requester: "خالد", date: "2026-04-11", type: "decision" },
    { id: "APR-005", title: "تكامل بوابة الدفع", class: "R2", requester: "فاطمة", date: "2026-04-10", type: "workflow" },
  ];
  const classColor: Record<string, string> = {
    R0: "bg-red-500/10 text-red-400", R1: "bg-amber-500/10 text-amber-400",
    R2: "bg-blue-500/10 text-blue-400", R3: "bg-emerald-500/10 text-emerald-400",
  };
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="مركز الاعتمادات" en="Approval Center" icon={CheckCircle2} />
      <div className="grid grid-cols-3 gap-4">
        <S label="إجمالي المعلق (Total Pending)" value={5} icon={Clock} color="text-amber-500" bg="bg-amber-500/10" />
        <S label="اعتمادات سير العمل (Workflow)" value={3} icon={Workflow} color="text-blue-500" bg="bg-blue-500/10" />
        <S label="اعتمادات القرارات (Decision)" value={2} icon={Target} color="text-emerald-500" bg="bg-emerald-500/10" />
      </div>
      <div className="flex gap-2 flex-wrap">
        {["الكل", "R0", "R1", "R2", "R3"].map((f) => (
          <button key={f} className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-border bg-card/50 hover:bg-primary/10 hover:text-primary transition-colors">{f}</button>
        ))}
      </div>
      <div className="space-y-3">
        {approvals.map((a) => (
          <div key={a.id} className="rounded-2xl border border-border bg-card/50 p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <Badge c={classColor[a.class]}>{a.class}</Badge>
              <div className="text-right min-w-0">
                <p className="text-sm font-semibold truncate">{a.title}</p>
                <p className="text-[11px] text-muted-foreground">{a.requester} · {a.date}</p>
              </div>
            </div>
            <div className="flex gap-2 shrink-0">
              <button className="px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-semibold hover:bg-emerald-500/20 transition-colors">اعتماد</button>
              <button className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 text-xs font-semibold hover:bg-red-500/20 transition-colors">رفض</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════ 3. EvidencePackView ═══════════════ */

export function EvidencePackView() {
  const packs = [
    { id: "EP-101", title: "حزمة العناية الواجبة — شركة النخبة", items: 14, status: "مكتمل", class: "R2", date: "2026-04-10" },
    { id: "EP-102", title: "تقييم الامتثال PDPL Q1", items: 8, status: "قيد المراجعة", class: "R1", date: "2026-04-08" },
    { id: "EP-103", title: "تدقيق أمن البنية التحتية", items: 22, status: "مسودة", class: "R3", date: "2026-04-05" },
  ];
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="حزم الأدلة" en="Evidence Pack Browser" icon={FileCheck} />
      {packs.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border bg-card/30 p-12 text-center">
          <FileText className="w-10 h-10 mx-auto text-muted-foreground mb-3" />
          <p className="text-muted-foreground">لا توجد حزم أدلة بعد</p>
          <button className="mt-4 px-4 py-2 rounded-xl bg-primary text-primary-foreground text-sm font-medium">إنشاء حزمة جديدة</button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {packs.map((p) => (
            <div key={p.id} className="rounded-2xl border border-border bg-card/50 p-5 space-y-3 hover:border-primary/40 transition-colors">
              <div className="flex justify-between items-start">
                <Badge c={p.status === "مكتمل" ? "bg-emerald-500/10 text-emerald-400" : p.status === "قيد المراجعة" ? "bg-amber-500/10 text-amber-400" : "bg-zinc-500/10 text-zinc-400"}>{p.status}</Badge>
                <Badge>{p.class}</Badge>
              </div>
              <p className="font-semibold text-sm">{p.title}</p>
              <div className="flex justify-between text-[11px] text-muted-foreground">
                <span>{p.items} عنصر</span>
                <span>{p.date}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ═══════════════ 4. PartnerRoomView ═══════════════ */

export function PartnerRoomView() {
  const stages = ["استكشاف (Scouted)", "تقييم (Evaluating)", "تفاوض (Negotiating)", "نشط (Active)"];
  const partners = [
    { name: "شركة الابتكار التقني", stage: 3, fit: 92, health: "ممتاز", sector: "تقنية" },
    { name: "مجموعة الرياض المالية", stage: 2, fit: 78, health: "جيد", sector: "مالية" },
    { name: "حلول السحاب العربي", stage: 1, fit: 65, health: "متوسط", sector: "بنية تحتية" },
    { name: "منصة لوجستيات الخليج", stage: 0, fit: 45, health: "جديد", sector: "لوجستيات" },
  ];
  const healthColor: Record<string, string> = { "ممتاز": "text-emerald-400", "جيد": "text-blue-400", "متوسط": "text-amber-400", "جديد": "text-zinc-400" };
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="غرفة الشراكات" en="Partner Room" icon={Handshake} />
      <div className="flex gap-3 overflow-x-auto pb-2">
        {stages.map((s, i) => (
          <div key={s} className="flex items-center gap-2 rounded-xl border border-border bg-card/50 px-4 py-2 text-sm whitespace-nowrap shrink-0">
            <span className={`w-2 h-2 rounded-full ${i === 3 ? "bg-emerald-500" : i === 2 ? "bg-blue-500" : i === 1 ? "bg-amber-500" : "bg-zinc-500"}`} />
            {s}
          </div>
        ))}
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        {partners.map((p) => (
          <div key={p.name} className="rounded-2xl border border-border bg-card/50 p-5 space-y-3">
            <div className="flex justify-between items-start">
              <span className="text-sm font-semibold">{p.name}</span>
              <Badge>{stages[p.stage].split(" ")[0]}</Badge>
            </div>
            <div className="flex gap-4 text-[11px] text-muted-foreground">
              <span>القطاع: {p.sector}</span>
              <span className={healthColor[p.health]}>الصحة: {p.health}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">التوافق الاستراتيجي:</span>
              <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full" style={{ width: `${p.fit}%` }} />
              </div>
              <span className="text-xs font-bold">{p.fit}%</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════ 5. DDRoomView ═══════════════ */

export function DDRoomView() {
  const streams = [
    { name: "القانوني (Legal)", progress: 85, docs: 12, icon: Scale, color: "text-blue-400", bg: "bg-blue-500" },
    { name: "المالي (Financial)", progress: 60, docs: 8, icon: BarChart3, color: "text-emerald-400", bg: "bg-emerald-500" },
    { name: "المنتج (Product)", progress: 45, docs: 5, icon: Layers, color: "text-purple-400", bg: "bg-purple-500" },
    { name: "الأمني (Security)", progress: 30, docs: 3, icon: Shield, color: "text-red-400", bg: "bg-red-500" },
  ];
  const docs = [
    { name: "عقد التأسيس", stream: "قانوني", status: "مراجع" },
    { name: "القوائم المالية 2025", stream: "مالي", status: "قيد المراجعة" },
    { name: "تقرير اختبار الاختراق", stream: "أمني", status: "مطلوب" },
    { name: "خارطة طريق المنتج", stream: "منتج", status: "مراجع" },
  ];
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="غرفة العناية الواجبة" en="Due Diligence Room" icon={Search} />
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {streams.map((s) => (
          <div key={s.name} className="rounded-2xl border border-border bg-card/50 p-5 space-y-3">
            <div className="flex items-center gap-2">
              <s.icon className={`w-5 h-5 ${s.color}`} />
              <span className="text-sm font-semibold">{s.name}</span>
            </div>
            <div className="h-2 bg-secondary rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${s.bg}`} style={{ width: `${s.progress}%` }} />
            </div>
            <div className="flex justify-between text-[11px] text-muted-foreground">
              <span>{s.progress}%</span>
              <span>{s.docs} مستند</span>
            </div>
          </div>
        ))}
      </div>
      <section>
        <h2 className="text-lg font-bold mb-3">متتبع المستندات (Document Tracker)</h2>
        <div className="space-y-2">
          {docs.map((d) => (
            <div key={d.name} className="rounded-xl border border-border bg-card/50 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="w-4 h-4 text-muted-foreground" />
                <span className="text-sm">{d.name}</span>
              </div>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="text-muted-foreground">{d.stream}</span>
                <Badge c={d.status === "مراجع" ? "bg-emerald-500/10 text-emerald-400" : d.status === "قيد المراجعة" ? "bg-amber-500/10 text-amber-400" : "bg-red-500/10 text-red-400"}>{d.status}</Badge>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

/* ═══════════════ 6. RiskBoardView ═══════════════ */

export function RiskBoardView() {
  const risks = [
    { title: "تأخر تكامل بوابة الدفع", severity: "critical" as const, area: "تقني", impact: "عالي", probability: "مرتفع" },
    { title: "نقص كوادر فريق الأمن", severity: "high" as const, area: "تشغيلي", impact: "متوسط", probability: "مرتفع" },
    { title: "تغيير لوائح PDPL Q3", severity: "high" as const, area: "تنظيمي", impact: "عالي", probability: "متوسط" },
    { title: "تأخر تسليم API الشريك", severity: "medium" as const, area: "شراكات", impact: "متوسط", probability: "متوسط" },
    { title: "ارتفاع تكاليف الاستضافة", severity: "low" as const, area: "مالي", impact: "منخفض", probability: "منخفض" },
  ];
  const sev = {
    critical: { label: "حرج (Critical)", border: "border-red-500/40", bg: "bg-red-500/10", text: "text-red-400" },
    high: { label: "عالي (High)", border: "border-amber-500/40", bg: "bg-amber-500/10", text: "text-amber-400" },
    medium: { label: "متوسط (Medium)", border: "border-blue-500/40", bg: "bg-blue-500/10", text: "text-blue-400" },
    low: { label: "منخفض (Low)", border: "border-emerald-500/40", bg: "bg-emerald-500/10", text: "text-emerald-400" },
  };
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="لوحة المخاطر" en="Risk Heatmap Board" icon={AlertTriangle} />
      <div className="space-y-4">
        {risks.map((r) => {
          const s = sev[r.severity];
          return (
            <div key={r.title} className={`rounded-2xl border ${s.border} ${s.bg} p-5 space-y-2`}>
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold">{r.title}</span>
                <Badge c={`${s.bg} ${s.text}`}>{s.label}</Badge>
              </div>
              <div className="flex gap-4 text-[11px] text-muted-foreground">
                <span>المجال: {r.area}</span>
                <span>التأثير: {r.impact}</span>
                <span>الاحتمالية: {r.probability}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════ 7. PolicyViolationsBoardView ═══════════════ */

export function PolicyViolationsBoardView() {
  const violations: { id: string; title: string; severity: string; timestamp: string; policy: string }[] = [];
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="مخالفات السياسات" en="Policy Violations Board" icon={ShieldAlert} />
      {violations.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-emerald-500/30 bg-emerald-500/5 p-12 text-center">
          <ShieldCheck className="w-12 h-12 mx-auto text-emerald-500 mb-3" />
          <p className="text-emerald-400 font-semibold text-lg">لا توجد مخالفات</p>
          <p className="text-sm text-muted-foreground mt-1">جميع السياسات ملتزمة — (No violations detected)</p>
        </div>
      ) : (
        <div className="space-y-3">
          {violations.map((v) => (
            <div key={v.id} className="rounded-2xl border border-red-500/30 bg-red-500/5 p-4 flex items-center justify-between">
              <div className="text-right">
                <p className="text-sm font-semibold">{v.title}</p>
                <p className="text-[11px] text-muted-foreground">{v.policy} · {v.timestamp}</p>
              </div>
              <Badge c="bg-red-500/10 text-red-400">{v.severity}</Badge>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ═══════════════ 8. ActualVsForecastView ═══════════════ */

export function ActualVsForecastView() {
  const periods = [
    { label: "يناير", actual: 420000, forecast: 400000 },
    { label: "فبراير", actual: 385000, forecast: 410000 },
    { label: "مارس", actual: 510000, forecast: 480000 },
    { label: "أبريل", actual: 475000, forecast: 500000 },
  ];
  const fmt = (n: number) => `${(n / 1000).toFixed(0)}K ر.س`;
  const pct = (a: number, f: number) => (((a - f) / f) * 100).toFixed(1);
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="الفعلي مقابل المتوقع" en="Actual vs Forecast — Financial Variance" icon={BarChart3} />
      <div className="flex gap-2">
        {["شهري", "ربع سنوي", "سنوي"].map((p) => (
          <button key={p} className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-border bg-card/50 hover:bg-primary/10 transition-colors">{p}</button>
        ))}
      </div>
      <div className="space-y-4">
        {periods.map((p) => {
          const variance = Number(pct(p.actual, p.forecast));
          const positive = variance >= 0;
          return (
            <div key={p.label} className="rounded-2xl border border-border bg-card/50 p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-semibold">{p.label}</span>
                <Badge c={positive ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}>
                  {positive ? "+" : ""}{variance}%
                </Badge>
              </div>
              <div className="grid grid-cols-2 gap-4 text-[11px]">
                <div>
                  <p className="text-muted-foreground">الفعلي (Actual)</p>
                  <p className="text-base font-bold mt-0.5">{fmt(p.actual)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">المتوقع (Forecast)</p>
                  <p className="text-base font-bold mt-0.5">{fmt(p.forecast)}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════ 9. RevenueFunnelView ═══════════════ */

export function RevenueFunnelView() {
  const stages = [
    { name: "العملاء المحتملين (Leads)", count: 2400, rate: 100, color: "bg-blue-500" },
    { name: "المؤهلين (Qualified)", count: 1200, rate: 50, color: "bg-cyan-500" },
    { name: "العروض المقدمة (Proposals)", count: 480, rate: 40, color: "bg-purple-500" },
    { name: "التفاوض (Negotiation)", count: 192, rate: 40, color: "bg-amber-500" },
    { name: "مغلق - ربح (Closed Won)", count: 96, rate: 50, color: "bg-emerald-500" },
  ];
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="قمع الإيرادات" en="Revenue Funnel Control" icon={TrendingUp} />
      <div className="grid grid-cols-3 gap-4">
        <S label="إجمالي العملاء المحتملين" value="2,400" icon={Users} color="text-blue-500" bg="bg-blue-500/10" />
        <S label="معدل التحويل الإجمالي" value="4.0%" icon={Target} color="text-emerald-500" bg="bg-emerald-500/10" />
        <S label="الصفقات المغلقة" value="96" icon={CheckCircle2} color="text-primary" />
      </div>
      <div className="space-y-3">
        {stages.map((s, i) => (
          <div key={s.name} className="rounded-2xl border border-border bg-card/50 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold">{s.name}</span>
              <span className="text-xs text-muted-foreground">{s.count.toLocaleString()}</span>
            </div>
            <div className="h-3 bg-secondary rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${s.color}`} style={{ width: `${(s.count / 2400) * 100}%` }} />
            </div>
            {i > 0 && <p className="text-[11px] text-muted-foreground mt-1">معدل التحويل: {s.rate}%</p>}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════ 10. PartnerScorecardsView ═══════════════ */

export function PartnerScorecardsView() {
  const partners = [
    { name: "شركة الابتكار التقني", grade: "A+", revenue: "1.2M", deals: 34, satisfaction: 96 },
    { name: "مجموعة الرياض المالية", grade: "A", revenue: "850K", deals: 22, satisfaction: 91 },
    { name: "حلول السحاب العربي", grade: "B", revenue: "420K", deals: 15, satisfaction: 84 },
    { name: "منصة لوجستيات الخليج", grade: "C", revenue: "180K", deals: 8, satisfaction: 72 },
    { name: "تطبيقات المستقبل", grade: "D", revenue: "60K", deals: 3, satisfaction: 58 },
  ];
  const gradeColor: Record<string, string> = {
    "A+": "bg-emerald-500/10 text-emerald-400", A: "bg-emerald-500/10 text-emerald-400",
    B: "bg-blue-500/10 text-blue-400", C: "bg-amber-500/10 text-amber-400",
    D: "bg-red-500/10 text-red-400", F: "bg-red-500/10 text-red-400",
  };
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="بطاقات أداء الشركاء" en="Partner Scorecards" icon={Users} />
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {partners.map((p) => (
          <div key={p.name} className="rounded-2xl border border-border bg-card/50 p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">{p.name}</span>
              <Badge c={gradeColor[p.grade] || "bg-zinc-500/10 text-zinc-400"}>{p.grade}</Badge>
            </div>
            <div className="grid grid-cols-3 gap-2 text-center text-[11px]">
              <div className="rounded-lg bg-secondary/50 p-2">
                <p className="text-muted-foreground">الإيرادات</p>
                <p className="font-bold mt-0.5">{p.revenue} ر.س</p>
              </div>
              <div className="rounded-lg bg-secondary/50 p-2">
                <p className="text-muted-foreground">الصفقات</p>
                <p className="font-bold mt-0.5">{p.deals}</p>
              </div>
              <div className="rounded-lg bg-secondary/50 p-2">
                <p className="text-muted-foreground">الرضا</p>
                <p className="font-bold mt-0.5">{p.satisfaction}%</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════ 11. MAPipelineView ═══════════════ */

export function MAPipelineView() {
  const columns = ["مصادر (Sourced)", "فحص (Screening)", "عناية واجبة (DD)", "تقييم (Valuation)", "تفاوض (Negotiation)", "إغلاق (Closing)", "مغلق (Closed)"];
  const targets = [
    { name: "شركة البيانات الذكية", col: 0, valuation: "8-12M", sector: "تقنية" },
    { name: "منصة التوصيل السريع", col: 1, valuation: "15-20M", sector: "لوجستيات" },
    { name: "حلول الدفع الرقمي", col: 2, valuation: "25-35M", sector: "مالية" },
    { name: "مصنع التغليف المتقدم", col: 3, valuation: "5-8M", sector: "صناعي" },
    { name: "تطبيق الصحة الرقمية", col: 4, valuation: "10-15M", sector: "صحة" },
  ];
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="خط أنابيب الاستحواذ" en="M&A Pipeline — Kanban" icon={GitBranch} />
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((col, ci) => (
          <div key={col} className="min-w-[220px] shrink-0 space-y-3">
            <div className="rounded-xl bg-secondary/50 px-3 py-2 text-xs font-bold text-center">{col}</div>
            {targets.filter((t) => t.col === ci).map((t) => (
              <div key={t.name} className="rounded-2xl border border-border bg-card/50 p-4 space-y-2">
                <p className="text-sm font-semibold">{t.name}</p>
                <p className="text-[11px] text-muted-foreground">{t.sector}</p>
                <Badge>{t.valuation} SAR</Badge>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════ 12. ExpansionLaunchView ═══════════════ */

export function ExpansionLaunchView() {
  const markets = [
    { name: "الرياض", status: "نشط", readiness: 100, color: "bg-emerald-500" },
    { name: "جدة", status: "إطلاق", readiness: 85, color: "bg-blue-500" },
    { name: "الدمام", status: "تخطيط", readiness: 45, color: "bg-amber-500" },
    { name: "نيوم", status: "استكشاف", readiness: 20, color: "bg-purple-500" },
  ];
  const checklist = [
    { task: "ترخيص السجل التجاري", done: true },
    { task: "إعداد فريق المبيعات المحلي", done: true },
    { task: "تكامل بوابات الدفع المحلية", done: false },
    { task: "حملة التسويق الافتتاحية", done: false },
    { task: "اختبار Canary (10% حركة مرور)", done: false },
  ];
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="وحدة تحكم التوسع" en="Expansion Launch Console" icon={Rocket} />
      <section>
        <h2 className="text-lg font-bold mb-3">حالة الأسواق (Market Status)</h2>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {markets.map((m) => (
            <div key={m.name} className="rounded-2xl border border-border bg-card/50 p-5 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold">{m.name}</span>
                <Badge>{m.status}</Badge>
              </div>
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${m.color}`} style={{ width: `${m.readiness}%` }} />
              </div>
              <p className="text-[11px] text-muted-foreground">الجاهزية: {m.readiness}%</p>
            </div>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-lg font-bold mb-3">قائمة الجاهزية (Launch Checklist)</h2>
        <div className="space-y-2">
          {checklist.map((c) => (
            <div key={c.task} className="flex items-center gap-3 rounded-xl border border-border bg-card/50 px-4 py-3">
              {c.done ? <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" /> : <div className="w-4 h-4 rounded-full border-2 border-muted-foreground/40 shrink-0" />}
              <span className={`text-sm ${c.done ? "line-through text-muted-foreground" : ""}`}>{c.task}</span>
            </div>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-lg font-bold mb-3">مقاييس Canary</h2>
        <div className="grid grid-cols-3 gap-4">
          <S label="نسبة الحركة" value="10%" icon={Activity} color="text-cyan-500" bg="bg-cyan-500/10" />
          <S label="معدل الخطأ" value="0.3%" icon={AlertTriangle} color="text-emerald-500" bg="bg-emerald-500/10" />
          <S label="زمن الاستجابة" value="120ms" icon={Gauge} color="text-blue-500" bg="bg-blue-500/10" />
        </div>
      </section>
    </div>
  );
}

/* ═══════════════ 13. PMIEngineView ═══════════════ */

export function PMIEngineView() {
  const plans = [
    { label: "30 يوم", progress: 90, color: "bg-emerald-500" },
    { label: "60 يوم", progress: 55, color: "bg-blue-500" },
    { label: "90 يوم", progress: 25, color: "bg-purple-500" },
  ];
  const workstreams = [
    { name: "تكامل تقني (Tech Integration)", status: "on-track", progress: 78 },
    { name: "توحيد العمليات (Ops Unification)", status: "at-risk", progress: 42 },
    { name: "دمج الفرق (Team Merge)", status: "on-track", progress: 65 },
    { name: "تكامل العملاء (Customer Integration)", status: "delayed", progress: 20 },
  ];
  const wsColor: Record<string, string> = { "on-track": "text-emerald-400", "at-risk": "text-amber-400", "delayed": "text-red-400" };
  const wsLabel: Record<string, string> = { "on-track": "على المسار", "at-risk": "في خطر", "delayed": "متأخر" };
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="محرك PMI 30/60/90" en="Post-Merger Integration Engine" icon={Layers} />
      <section>
        <h2 className="text-lg font-bold mb-3">تقدم الخطة (Plan Progress)</h2>
        <div className="grid grid-cols-3 gap-4">
          {plans.map((p) => (
            <div key={p.label} className="rounded-2xl border border-border bg-card/50 p-5 space-y-3 text-center">
              <p className="text-sm font-bold">{p.label}</p>
              <div className="h-3 bg-secondary rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${p.color}`} style={{ width: `${p.progress}%` }} />
              </div>
              <p className="text-lg font-bold">{p.progress}%</p>
            </div>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-lg font-bold mb-3">تدفقات العمل (Workstreams)</h2>
        <div className="space-y-3">
          {workstreams.map((w) => (
            <div key={w.name} className="rounded-2xl border border-border bg-card/50 p-4 flex items-center justify-between gap-4">
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold">{w.name}</p>
                <div className="h-2 bg-secondary rounded-full overflow-hidden mt-2">
                  <div className="h-full rounded-full bg-primary" style={{ width: `${w.progress}%` }} />
                </div>
              </div>
              <span className={`text-xs font-semibold ${wsColor[w.status]} shrink-0`}>{wsLabel[w.status]}</span>
            </div>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-lg font-bold mb-3">تحقيق التآزر (Synergy Realization)</h2>
        <div className="grid grid-cols-3 gap-4">
          <S label="التآزر المستهدف" value="4.2M ر.س" icon={Target} color="text-emerald-500" bg="bg-emerald-500/10" />
          <S label="المحقق حتى الآن" value="1.8M ر.س" icon={TrendingUp} color="text-blue-500" bg="bg-blue-500/10" />
          <S label="نسبة التحقيق" value="43%" icon={Gauge} color="text-primary" />
        </div>
      </section>
    </div>
  );
}

/* ═══════════════ 14. ToolVerificationView ═══════════════ */

export function ToolVerificationView() {
  const tools = [
    { name: "Groq LLM Provider", status: "verified", capabilities: ["تصنيف", "NLP", "محادثة"], lastVerified: "2026-04-15" },
    { name: "OpenAI Fallback", status: "verified", capabilities: ["توليد نصوص", "تحليل"], lastVerified: "2026-04-14" },
    { name: "WhatsApp Business API", status: "pending", capabilities: ["رسائل", "قوالب"], lastVerified: "—" },
    { name: "Mada Payment Gateway", status: "verified", capabilities: ["مدفوعات", "استرداد"], lastVerified: "2026-04-12" },
    { name: "ZATCA E-Invoicing", status: "failed", capabilities: ["فواتير إلكترونية"], lastVerified: "2026-04-10" },
  ];
  const stColor: Record<string, string> = {
    verified: "bg-emerald-500/10 text-emerald-400",
    pending: "bg-amber-500/10 text-amber-400",
    failed: "bg-red-500/10 text-red-400",
  };
  const stLabel: Record<string, string> = { verified: "مُتحقق", pending: "قيد التحقق", failed: "فشل" };
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="سجل التحقق من الأدوات" en="Tool Verification Ledger" icon={PackageCheck} />
      {tools.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border bg-card/30 p-12 text-center">
          <Cpu className="w-10 h-10 mx-auto text-muted-foreground mb-3" />
          <p className="text-muted-foreground">لا توجد أدوات مسجلة</p>
        </div>
      ) : (
        <div className="space-y-3">
          {tools.map((t) => (
            <div key={t.name} className="rounded-2xl border border-border bg-card/50 p-4 flex items-center justify-between gap-4">
              <div className="flex-1 min-w-0 text-right">
                <p className="text-sm font-semibold">{t.name}</p>
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {t.capabilities.map((c) => (
                    <span key={c} className="px-2 py-0.5 rounded-md bg-secondary/50 text-[10px] text-muted-foreground">{c}</span>
                  ))}
                </div>
              </div>
              <div className="text-left shrink-0 space-y-1">
                <Badge c={stColor[t.status]}>{stLabel[t.status]}</Badge>
                <p className="text-[10px] text-muted-foreground">{t.lastVerified}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ═══════════════ 15. ConnectorHealthView ═══════════════ */

export function ConnectorHealthView() {
  const connectors = [
    { name: "WhatsApp Business", status: "healthy", latency: "45ms", uptime: "99.98%" },
    { name: "HubSpot CRM", status: "healthy", latency: "120ms", uptime: "99.95%" },
    { name: "Mada Payment", status: "degraded", latency: "890ms", uptime: "98.20%" },
    { name: "ZATCA E-Invoice", status: "error", latency: "—", uptime: "92.10%" },
    { name: "Google Calendar", status: "healthy", latency: "78ms", uptime: "99.99%" },
    { name: "Slack Notifications", status: "healthy", latency: "55ms", uptime: "99.97%" },
  ];
  const stCfg: Record<string, { dot: string; label: string; border: string }> = {
    healthy: { dot: "bg-emerald-500", label: "سليم (Healthy)", border: "border-emerald-500/20" },
    degraded: { dot: "bg-amber-500", label: "متدهور (Degraded)", border: "border-amber-500/20" },
    error: { dot: "bg-red-500", label: "خطأ (Error)", border: "border-red-500/20" },
  };
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="صحة الموصلات" en="Connector Health Monitor" icon={Plug} />
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {connectors.map((c) => {
          const cfg = stCfg[c.status];
          return (
            <div key={c.name} className={`rounded-2xl border ${cfg.border} bg-card/50 p-5 space-y-3`}>
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${cfg.dot}`} />
                <span className="text-sm font-semibold">{c.name}</span>
              </div>
              <div className="flex justify-between text-[11px] text-muted-foreground">
                <span>الحالة: {cfg.label}</span>
                <span>زمن الاستجابة: {c.latency}</span>
              </div>
              <p className="text-[11px] text-muted-foreground">وقت التشغيل: {c.uptime}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ═══════════════ 16. ReleaseGateView ═══════════════ */

export function ReleaseGateView() {
  const gates = [
    { name: "اختبارات الوحدة (Unit Tests)", passed: true, details: "1,247 / 1,247 passed" },
    { name: "اختبارات التكامل (Integration)", passed: true, details: "89 / 89 passed" },
    { name: "فحص الأمان (Security Scan)", passed: true, details: "0 critical, 0 high" },
    { name: "مراجعة الكود (Code Review)", passed: true, details: "2 approvals" },
    { name: "اختبار Canary (10%)", passed: false, details: "Error rate 0.8% > 0.5% threshold" },
    { name: "اختبار الأداء (Performance)", passed: true, details: "P99 < 200ms" },
  ];
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="بوابات الإصدار" en="Release Gate Dashboard" icon={GitBranch} />
      <div className="grid grid-cols-2 gap-4 mb-4">
        <S label="الإصدار الحالي (Current)" value="v2.4.1" icon={Layers} color="text-blue-500" bg="bg-blue-500/10" />
        <S label="الإصدار المرشح (Candidate)" value="v2.5.0-rc.1" icon={Rocket} color="text-amber-500" bg="bg-amber-500/10" />
      </div>
      <div className="space-y-3">
        {gates.map((g) => (
          <div key={g.name} className={`rounded-2xl border ${g.passed ? "border-emerald-500/20" : "border-red-500/30 bg-red-500/5"} bg-card/50 p-4 flex items-center justify-between gap-4`}>
            <div className="flex items-center gap-3">
              {g.passed ? <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" /> : <XCircle className="w-5 h-5 text-red-500 shrink-0" />}
              <div className="text-right">
                <p className="text-sm font-semibold">{g.name}</p>
                <p className="text-[11px] text-muted-foreground">{g.details}</p>
              </div>
            </div>
            <Badge c={g.passed ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}>{g.passed ? "ناجح" : "فشل"}</Badge>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ═══════════════ 17. SaudiComplianceView ═══════════════ */

export function SaudiComplianceView() {
  const pdpl = [
    { control: "إدارة الموافقة (Consent Mgmt)", status: "compliant" },
    { control: "حقوق صاحب البيانات (Data Subject Rights)", status: "compliant" },
    { control: "الإخطار بالخرق (Breach Notification)", status: "partial" },
    { control: "نقل البيانات عبر الحدود (Cross-border Transfer)", status: "compliant" },
    { control: "تقييم الأثر (Impact Assessment)", status: "non-compliant" },
  ];
  const nca = [
    { control: "إدارة الهوية والوصول (IAM)", status: "compliant" },
    { control: "أمن الشبكات (Network Security)", status: "compliant" },
    { control: "إدارة الثغرات (Vuln Mgmt)", status: "partial" },
    { control: "الاستجابة للحوادث (Incident Response)", status: "compliant" },
  ];
  const ai = [
    { control: "شفافية النموذج (Model Transparency)", status: "compliant" },
    { control: "تحيز الخوارزمية (Algo Bias)", status: "partial" },
    { control: "قابلية التفسير (Explainability)", status: "compliant" },
  ];
  const stCfg: Record<string, { label: string; c: string }> = {
    compliant: { label: "ملتزم", c: "bg-emerald-500/10 text-emerald-400" },
    partial: { label: "جزئي", c: "bg-amber-500/10 text-amber-400" },
    "non-compliant": { label: "غير ملتزم", c: "bg-red-500/10 text-red-400" },
  };
  const renderTable = (title: string, rows: { control: string; status: string }[]) => (
    <section>
      <h2 className="text-lg font-bold mb-3">{title}</h2>
      <div className="space-y-2">
        {rows.map((r) => (
          <div key={r.control} className="rounded-xl border border-border bg-card/50 px-4 py-3 flex items-center justify-between">
            <span className="text-sm">{r.control}</span>
            <Badge c={stCfg[r.status].c}>{stCfg[r.status].label}</Badge>
          </div>
        ))}
      </div>
    </section>
  );
  const total = [...pdpl, ...nca, ...ai];
  const compliant = total.filter((r) => r.status === "compliant").length;
  const score = Math.round((compliant / total.length) * 100);
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="مصفوفة الامتثال السعودي" en="Saudi Compliance Matrix" icon={ShieldCheck} />
      <S label="درجة الامتثال الإجمالية (Overall Score)" value={`${score}%`} sub={`${compliant} من ${total.length} ضوابط ملتزمة`} icon={Shield} color="text-emerald-500" bg="bg-emerald-500/10" />
      {renderTable("ضوابط PDPL (PDPL Controls)", pdpl)}
      {renderTable("ضوابط NCA ECC (NCA ECC Controls)", nca)}
      {renderTable("حوكمة الذكاء الاصطناعي (AI Governance)", ai)}
    </div>
  );
}

/* ═══════════════ 18. ModelRoutingView ═══════════════ */

export function ModelRoutingView() {
  const models = [
    { name: "Groq llama-3.1-70b", tier: "Primary", successRate: 99.2, latency: "180ms", tasks: ["تصنيف", "NLP عربي", "محادثة"] },
    { name: "OpenAI GPT-4o-mini", tier: "Fallback", successRate: 98.8, latency: "420ms", tasks: ["توليد نصوص", "تحليل"] },
    { name: "Claude (Anthropic)", tier: "Specialist", successRate: 99.5, latency: "350ms", tasks: ["عروض مبيعات", "مقترحات"] },
    { name: "Gemini (Google)", tier: "Specialist", successRate: 97.9, latency: "280ms", tasks: ["بحث", "تحليل بيانات"] },
    { name: "DeepSeek", tier: "Specialist", successRate: 96.5, latency: "250ms", tasks: ["برمجة", "مراجعة كود"] },
  ];
  const taskMap = [
    { task: "تصنيف العملاء المحتملين", model: "Groq", priority: 1 },
    { task: "تحليل المشاعر (عربي)", model: "Groq", priority: 1 },
    { task: "إنشاء عروض المبيعات", model: "Claude", priority: 1 },
    { task: "أبحاث السوق", model: "Gemini", priority: 1 },
    { task: "مراجعة الكود", model: "DeepSeek", priority: 1 },
    { task: "الاحتياطي العام", model: "OpenAI", priority: 2 },
  ];
  const tierColor: Record<string, string> = {
    Primary: "bg-emerald-500/10 text-emerald-400",
    Fallback: "bg-amber-500/10 text-amber-400",
    Specialist: "bg-blue-500/10 text-blue-400",
  };
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-8 text-right" dir="rtl">
      <H ar="توجيه النماذج" en="Model Routing Dashboard" icon={Network} />
      <section>
        <h2 className="text-lg font-bold mb-3">ملفات النماذج (Model Profiles)</h2>
        <div className="space-y-3">
          {models.map((m) => (
            <div key={m.name} className="rounded-2xl border border-border bg-card/50 p-4 flex items-center justify-between gap-4">
              <div className="flex-1 min-w-0 text-right">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold">{m.name}</span>
                  <Badge c={tierColor[m.tier]}>{m.tier}</Badge>
                </div>
                <div className="flex flex-wrap gap-1.5 mt-1.5">
                  {m.tasks.map((t) => (
                    <span key={t} className="px-2 py-0.5 rounded-md bg-secondary/50 text-[10px] text-muted-foreground">{t}</span>
                  ))}
                </div>
              </div>
              <div className="text-left shrink-0 text-[11px] space-y-0.5">
                <p className="text-muted-foreground">نجاح: <span className="font-bold text-foreground">{m.successRate}%</span></p>
                <p className="text-muted-foreground">زمن: <span className="font-bold text-foreground">{m.latency}</span></p>
              </div>
            </div>
          ))}
        </div>
      </section>
      <section>
        <h2 className="text-lg font-bold mb-3">ربط المهام بالنماذج (Task → Model)</h2>
        <div className="space-y-2">
          {taskMap.map((t) => (
            <div key={t.task} className="rounded-xl border border-border bg-card/50 px-4 py-3 flex items-center justify-between">
              <span className="text-sm">{t.task}</span>
              <Badge>{t.model}</Badge>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

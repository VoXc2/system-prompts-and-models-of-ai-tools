"use client";

import { useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  Users,
  Target,
  TrendingUp,
  Calendar,
  ArrowUpRight,
  BrainCircuit,
  Zap,
  MapPin,
  Search,
  Sparkles,
  Loader2,
} from "lucide-react";
import { StrategyBriefPanel } from "./strategy-brief-panel";
import { DeploymentReadinessBanner } from "./deployment-readiness-banner";
import { useAuth } from "@/contexts/auth-context";
import { apiFetch } from "@/lib/api-client";
import { formatSar, stageLabelAr } from "@/lib/dashboard-format";

type DashboardOverview = {
  total_leads: number;
  new_leads_today: number;
  total_deals: number;
  open_deals_value: string | number;
  closed_won_value: string | number;
  closed_won_count: number;
  messages_sent_today: number;
  conversion_rate: number;
  active_workflows: number;
};

type PipelineSummary = {
  stages: Record<string, number>;
  total_value_by_stage: Record<string, number>;
};

const DEMO_STATS = [
  { label: "العملاء المحتملين", value: "2,450", trend: "+12.5%", icon: Users, color: "text-blue-500", bg: "bg-blue-500/10" },
  { label: "الاجتماعات المجدولة", value: "145", trend: "+24.3%", icon: Calendar, color: "text-purple-500", bg: "bg-purple-500/10" },
  { label: "المبيعات المغلقة", value: "89", trend: "+8.2%", icon: Target, color: "text-emerald-500", bg: "bg-emerald-500/10" },
  { label: "إيرادات الشهر", value: "1.2M ر.س", trend: "+18.4%", icon: TrendingUp, color: "text-amber-500", bg: "bg-amber-500/10" },
];

const DEMO_PIPELINE = [
  { name: "شركة الأفق التقنية", stage: "تفاوض", value: "125,000 ر.س", prob: "80%", agent: "وكيل الإغلاق" },
  { name: "مجموعة الرواد", stage: "عرض سعر", value: "450,000 ر.س", prob: "60%", agent: "متدرب الذكاء الاصطناعي" },
  { name: "مصنع الشرق الأوسط", stage: "اجتماع أولي", value: "85,000 ر.س", prob: "30%", agent: "مجدول المواعيد" },
  { name: "مؤسسة النور", stage: "تأهيل", value: "غير محدد", prob: "10%", agent: "وكيل التأهيل" },
];

const DEMO_AI = [
  { title: "الأرباح المتوقعة", value: "1.8M ر.س", desc: "بناءً على 45 صفقة في مرحلة التفاوض", icon: Sparkles },
  { title: "القطاع الأكثر نمواً", value: "العقارات", desc: "ارتفاع في الطلب بنسبة 35% في الرياض", icon: Zap },
];

export function DashboardView() {
  const { user } = useAuth();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [pipeline, setPipeline] = useState<PipelineSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      setOverview(null);
      setPipeline(null);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    Promise.all([
      apiFetch("/api/v1/dashboard/overview"),
      apiFetch("/api/v1/dashboard/pipeline"),
    ])
      .then(async ([r1, r2]) => {
        if (cancelled) return;
        if (r1.ok) setOverview((await r1.json()) as DashboardOverview);
        else setError("تعذر تحميل ملخص اللوحة.");
        if (r2.ok) setPipeline((await r2.json()) as PipelineSummary);
      })
      .catch(() => {
        if (!cancelled) setError("تعذر الاتصال بالخادم.");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [user]);

  const displayName = useMemo(() => {
    const local = user?.email?.split("@")[0];
    if (!local) return "فريقك";
    return local.replace(/[._]/g, " ");
  }, [user?.email]);

  const stats = useMemo(() => {
    if (!overview) return DEMO_STATS;
    return [
      {
        label: "العملاء المحتملين",
        value: overview.total_leads.toLocaleString("ar-SA"),
        trend: `+${overview.new_leads_today} اليوم`,
        icon: Users,
        color: "text-blue-500",
        bg: "bg-blue-500/10",
      },
      {
        label: "الصفقات",
        value: overview.total_deals.toLocaleString("ar-SA"),
        trend: `${overview.conversion_rate}% تحويل`,
        icon: Target,
        color: "text-purple-500",
        bg: "bg-purple-500/10",
      },
      {
        label: "صفقات مغلقة (فوز)",
        value: String(overview.closed_won_count),
        trend: formatSar(overview.closed_won_value),
        icon: TrendingUp,
        color: "text-emerald-500",
        bg: "bg-emerald-500/10",
      },
      {
        label: "قيمة المسار المفتوح",
        value: formatSar(overview.open_deals_value),
        trend: `${overview.messages_sent_today} رسالة صادرة اليوم`,
        icon: BarChart3,
        color: "text-amber-500",
        bg: "bg-amber-500/10",
      },
    ];
  }, [overview]);

  const aiInsights = useMemo(() => {
    if (!overview) return DEMO_AI;
    return [
      {
        title: "معدل التحويل",
        value: `${overview.conversion_rate}%`,
        desc: `من ${overview.total_leads.toLocaleString("ar-SA")} عميل محتمل إلى صفقة فوز`,
        icon: Sparkles,
      },
      {
        title: "قيمة الإغلاق (فوز)",
        value: formatSar(overview.closed_won_value),
        desc: `إجمالي ${overview.closed_won_count} صفقة مغلقة بنجاح`,
        icon: Zap,
      },
    ];
  }, [overview]);

  const pipelineRows = useMemo(() => {
    if (!pipeline?.stages) return null;
    const entries = Object.entries(pipeline.stages).filter(([, n]) => n > 0);
    if (entries.length === 0) return null;
    return entries.map(([stage, count]) => ({
      name: stageLabelAr(stage),
      stage: `${count} صفقة`,
      value: formatSar(pipeline.total_value_by_stage[stage] ?? 0),
      prob: "—",
      agent: "—",
    }));
  }, [pipeline]);

  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 md:space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <DeploymentReadinessBanner />

      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div className="text-right">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-2">
            أهلاً بك، {displayName} 👋
          </h1>
          <p className="text-sm md:text-base text-muted-foreground">
            {overview
              ? "نظرة من قاعدة بيانات حسابك (مزامنة مباشرة مع الـ API)."
              : "نظرة عامة على أداء نظام المبيعات الذكي اليوم."}
          </p>
          {error ? <p className="mt-2 text-sm text-amber-600">{error}</p> : null}
        </div>
        <div className="flex w-full md:w-auto gap-3">
          <button
            type="button"
            className="flex-1 md:flex-none px-4 py-2.5 rounded-xl border border-border bg-card hover:bg-secondary/50 transition-colors text-xs md:text-sm font-medium"
          >
            تصدير التقرير
          </button>
          <button
            type="button"
            className="flex-1 md:flex-none px-4 py-2.5 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground transition-colors shadow-lg shadow-primary/25 text-xs md:text-sm font-medium flex items-center justify-center gap-2"
          >
            <Zap className="w-4 h-4" />
            تفعيل وكيل جديد
          </button>
        </div>
      </div>

      {user && loading ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          جاري تحميل مؤشرات الحساب…
        </div>
      ) : null}

      <StrategyBriefPanel />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {aiInsights.map((insight, i) => (
          <div key={i} className="glass-card p-4 border-primary/20 bg-primary/5 flex items-center gap-4">
            <div className="p-3 rounded-full bg-primary text-primary-foreground shadow-lg shadow-primary/25">
              <insight.icon className="w-5 h-5" />
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground font-bold uppercase tracking-wider">{insight.title}</p>
              <h4 className="text-xl font-bold">{insight.value}</h4>
              <p className="text-xs text-muted-foreground mt-0.5">{insight.desc}</p>
            </div>
          </div>
        ))}
      </div>

      <p className="text-[11px] text-muted-foreground/80 text-center md:text-right">
        {overview
          ? "الأرقام أعلاه من /api/v1/dashboard/overview لمستأجرك الحالي."
          : "الأرقام أعلاه تمثيل بصري للوحة حتى يُربط الحساب ببيانات المنصة — سجّل الدخول لمزامنة الـ API."}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="glass-card p-5 md:p-6 relative overflow-hidden group">
            <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full blur-2xl opacity-20 transition-all group-hover:opacity-40 group-hover:scale-150 ${stat.bg.replace("/10", "")}`} />
            <div className="flex justify-between items-start mb-4">
              <div className={`p-2.5 rounded-2xl ${stat.bg}`}>
                <stat.icon className={`w-5 h-5 md:w-6 md:h-6 ${stat.color}`} />
              </div>
              <span className="flex items-center gap-1 text-[10px] md:text-sm font-medium text-emerald-500 bg-emerald-500/10 px-2 md:px-2.5 py-0.5 md:py-1 rounded-full">
                <ArrowUpRight className="w-3 h-3" />
                {stat.trend}
              </span>
            </div>
            <div>
              <h3 className="text-2xl md:text-3xl font-bold tracking-tight mb-1">{stat.value}</h3>
              <p className="text-xs md:text-sm text-muted-foreground font-medium">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-6 border border-border/50">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-bold">{pipelineRows ? "توزيع الصفقات حسب المرحلة" : "أحدث الصفقات في المسار"}</h2>
            <button type="button" className="text-sm text-primary hover:underline">
              عرض الكل
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-right">
              <thead>
                <tr className="text-muted-foreground border-b border-border/50 bg-secondary/20">
                  <th className="py-3 px-4 font-medium">{pipelineRows ? "المرحلة" : "العميل"}</th>
                  <th className="py-3 px-4 font-medium">{pipelineRows ? "عدد" : "المرحلة"}</th>
                  <th className="py-3 px-4 font-medium">القيمة</th>
                  <th className="py-3 px-4 font-medium">احتمالية الإغلاق</th>
                  <th className="py-3 px-4 font-medium">الوكيل المسؤول</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {(pipelineRows ?? DEMO_PIPELINE).map((deal, i) => (
                  <tr key={i} className="hover:bg-white/5 transition-colors group">
                    <td className="py-4 px-4 font-medium text-foreground">{deal.name}</td>
                    <td className="py-4 px-4">
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-secondary/50 text-secondary-foreground border border-border/50">
                        {deal.stage}
                      </span>
                    </td>
                    <td className="py-4 px-4 font-mono text-foreground/80">{deal.value}</td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full transition-all duration-1000"
                            style={{ width: deal.prob === "—" ? "0%" : deal.prob }}
                          />
                        </div>
                        <span className="text-xs text-muted-foreground">{deal.prob}</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-muted-foreground flex items-center gap-2">
                      <BrainCircuit className="w-4 h-4 opacity-50" />
                      {deal.agent}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-6">
          <div className="glass-card p-6 border-blue-500/30 bg-blue-500/5">
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-bold">محرك صيد العملاء 🏹</h2>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs text-muted-foreground block">القطاع المستهدف</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="مثل: عيادات جراحة، عقارات..."
                    className="w-full bg-card border border-border rounded-lg py-2 px-9 text-sm text-right focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-xs text-muted-foreground block">المنطقة</label>
                <select className="w-full bg-card border border-border rounded-lg py-2 px-3 text-sm text-right outline-none">
                  <option>الرياض، السعودية</option>
                  <option>جدة، السعودية</option>
                  <option>الدمام، السعودية</option>
                  <option>الأحساء، السعودية</option>
                </select>
              </div>
              <button
                type="button"
                className="w-full py-2.5 rounded-xl bg-blue-500 hover:bg-blue-600 text-white text-sm font-bold shadow-lg shadow-blue-500/25 transition-all"
              >
                إطلاق حملة الصيد الآلية
              </button>
            </div>
          </div>

          <div className="glass-card p-6 flex flex-col border border-border/50">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-lg font-bold">تنبيهات الإدارة العُليا</h2>
              <span className="w-2 h-2 rounded-full bg-destructive animate-pulse" />
            </div>
            <div className="space-y-4 flex-1">
              <div className="p-4 rounded-xl bg-destructive/10 border border-destructive/20 flex flex-col gap-2 text-right">
                <span className="text-xs font-bold text-destructive">مراجعة شكوى</span>
                <p className="text-sm font-medium">
                  شركة &quot;التطوير الذكي&quot; تطلب تفعيل الضمان الذهبي لعدم الوصول للمستهدف التفاعلي.
                </p>
                <button type="button" className="text-xs font-bold text-destructive underline mt-1 text-right w-full">
                  مراجعة فحص الشرط الرابع
                </button>
              </div>
              <div className="p-4 rounded-xl bg-primary/10 border border-primary/20 flex flex-col gap-2 text-right">
                <span className="text-xs font-bold text-primary">تفعيل توظيف مسوق</span>
                <p className="text-sm font-medium">
                  المسوق &quot;أحمد عبدالله&quot; أكمل 12 إغلاق، يحتاج لتحويل عقده إلى رسمي عبر Qiwa.
                </p>
                <button type="button" className="text-xs font-bold text-primary underline mt-1 text-right w-full">
                  بدء عملية HR
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

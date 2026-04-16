"use client";

import type { LucideIcon } from "lucide-react";


import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Clock,
  DollarSign,
  Flag,
  GitBranch,
  Globe,
  Shield,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";

const KPICard = ({
  label,
  value,
  sub,
  icon: Icon,
  trend,
  color = "primary",
}: {
  label: string;
  value: string | number;
  sub?: string;
  icon: LucideIcon;
  trend?: "up" | "down" | "neutral";
  color?: string;
}) => {
  const colorMap: Record<string, string> = {
    primary: "from-primary/20 to-primary/5 border-primary/20 text-primary",
    green: "from-emerald-500/20 to-emerald-500/5 border-emerald-500/20 text-emerald-400",
    amber: "from-amber-500/20 to-amber-500/5 border-amber-500/20 text-amber-400",
    red: "from-red-500/20 to-red-500/5 border-red-500/20 text-red-400",
    blue: "from-blue-500/20 to-blue-500/5 border-blue-500/20 text-blue-400",
  };

  return (
    <div className={`rounded-2xl border bg-gradient-to-br p-5 ${colorMap[color]}`}>
      <div className="flex items-start justify-between mb-3">
        <p className="text-xs font-medium text-muted-foreground leading-tight">{label}</p>
        <Icon className="w-4 h-4 opacity-70" />
      </div>
      <p className="text-2xl font-bold text-foreground">{value}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
      {trend && (
        <div className={`mt-2 text-xs font-medium ${trend === "up" ? "text-emerald-400" : trend === "down" ? "text-red-400" : "text-muted-foreground"}`}>
          {trend === "up" ? "▲" : trend === "down" ? "▼" : "–"} {trend === "up" ? "صاعد" : trend === "down" ? "هابط" : "مستقر"}
        </div>
      )}
    </div>
  );
};

const NextBestAction = ({ action, impact, module: mod, urgency }: {
  action: string;
  impact: string;
  module: string;
  urgency: "high" | "medium" | "low";
}) => {
  const urgencyColor = urgency === "high" ? "border-red-500/30 bg-red-500/5" : urgency === "medium" ? "border-amber-500/30 bg-amber-500/5" : "border-border bg-secondary/20";
  return (
    <div className={`rounded-xl border p-3 ${urgencyColor}`}>
      <div className="flex items-start gap-2">
        <Zap className={`w-4 h-4 mt-0.5 flex-shrink-0 ${urgency === "high" ? "text-red-400" : urgency === "medium" ? "text-amber-400" : "text-muted-foreground"}`} />
        <div className="min-w-0">
          <p className="text-sm font-medium text-foreground leading-tight">{action}</p>
          <p className="text-xs text-muted-foreground mt-0.5">{impact}</p>
          <span className="inline-block mt-1 text-xs bg-secondary/50 px-2 py-0.5 rounded-full text-muted-foreground">{mod}</span>
        </div>
      </div>
    </div>
  );
};

const MOCK_NBA = [
  { action: "اعتماد عرض شراكة مع شركة الأفق للتقنية", impact: "عائد محتمل: ٢.٤M SAR", module: "Partnership OS", urgency: "high" as const },
  { action: "مراجعة ملف الاستحواذ — مرحلة DD Room", impact: "صفقة بـ ١٢M SAR — تنتهي خلال ٤٨ ساعة", module: "M&A OS", urgency: "high" as const },
  { action: "إطلاق حملة توسع السوق — الرياض الشمالية", impact: "قطاع تقني — جاهزية ٨٧٪", module: "Expansion OS", urgency: "medium" as const },
  { action: "اعتماد خصم ٢٠٪ خارج السياسة — العميل: شركة النخبة", impact: "قيمة الصفقة: ٨٠٠K SAR", module: "Sales OS", urgency: "medium" as const },
  { action: "مراجعة تقرير PDPL للربع الثاني", impact: "٣ انتهاكات محتملة بحاجة إلى معالجة", module: "Compliance", urgency: "high" as const },
];

const RISK_ITEMS = [
  { label: "مخاطر الامتثال", level: 72, color: "bg-amber-400" },
  { label: "مخاطر السوق", level: 45, color: "bg-blue-400" },
  { label: "مخاطر التشغيل", level: 28, color: "bg-emerald-400" },
  { label: "مخاطر الشركاء", level: 55, color: "bg-orange-400" },
  { label: "مخاطر الاستحواذ", level: 38, color: "bg-purple-400" },
];

export function ExecutiveRoom() {
  return (
    <div className="p-6 space-y-6" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">غرفة القيادة التنفيذية</h1>
          <p className="text-sm text-muted-foreground mt-1">لوحة القرار الحية — Dealix Sovereign OS</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-secondary/40 px-3 py-2 rounded-xl border border-border">
          <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span>بيانات حية — آخر تحديث: الآن</span>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <KPICard label="الإيرادات الفعلية (الربع الحالي)" value="٤.٢M SAR" sub="هدف: ٥M SAR" icon={DollarSign} trend="up" color="green" />
        <KPICard label="قيمة خط الصفقات" value="١٨.٧M SAR" sub="٣٢ فرصة نشطة" icon={TrendingUp} trend="up" color="primary" />
        <KPICard label="اعتمادات معلقة" value="٧" sub="٣ عالية الأولوية" icon={Clock} trend="down" color="amber" />
        <KPICard label="انتهاكات السياسات" value="٢" sub="PDPL + NCA" icon={Shield} trend="down" color="red" />
        <KPICard label="خط الشراكات" value="١١.٢M SAR" sub="٨ شراكات نشطة" icon={Users} trend="up" color="blue" />
        <KPICard label="خط الاستحواذ (M&A)" value="٣٦M SAR" sub="٤ أهداف قيد الدراسة" icon={GitBranch} trend="neutral" color="primary" />
        <KPICard label="سير العمليات الدائمة" value="١٢" sub="٣ بانتظار HITL" icon={Activity} trend="neutral" color="amber" />
        <KPICard label="جاهزية التوسع" value="٨٧٪" sub="سوق الرياض الشمالية" icon={Globe} trend="up" color="green" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Next Best Actions */}
        <div className="lg:col-span-2 bg-card/50 border border-border rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-5 h-5 text-primary" />
            <h2 className="font-bold text-foreground">أفضل الإجراءات التالية</h2>
          </div>
          <div className="space-y-2">
            {MOCK_NBA.map((item, i) => (
              <NextBestAction key={i} {...item} />
            ))}
          </div>
        </div>

        {/* Risk Heatmap */}
        <div className="bg-card/50 border border-border rounded-2xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h2 className="font-bold text-foreground">خريطة المخاطر الحية</h2>
          </div>
          <div className="space-y-4">
            {RISK_ITEMS.map((item) => (
              <div key={item.label}>
                <div className="flex justify-between text-xs text-muted-foreground mb-1">
                  <span>{item.label}</span>
                  <span className="font-medium">{item.level}٪</span>
                </div>
                <div className="h-2 bg-secondary/50 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${item.color}`}
                    style={{ width: `${item.level}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Actual vs Forecast */}
          <div className="mt-6 pt-4 border-t border-border/50">
            <h3 className="text-sm font-bold text-foreground mb-3 flex items-center gap-1.5">
              <BarChart3 className="w-4 h-4 text-primary" />
              الفعلي مقابل المستهدف
            </h3>
            {[
              { label: "المبيعات", actual: 84, target: 100 },
              { label: "الشراكات", actual: 62, target: 100 },
              { label: "الاستحواذ", actual: 40, target: 100 },
            ].map((item) => (
              <div key={item.label} className="mb-3">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-muted-foreground">{item.label}</span>
                  <span className="text-foreground font-medium">{item.actual}٪</span>
                </div>
                <div className="h-1.5 bg-secondary/50 rounded-full relative overflow-hidden">
                  <div className="absolute inset-0 w-full bg-border/30" />
                  <div
                    className="h-full bg-primary rounded-full relative z-10"
                    style={{ width: `${item.actual}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Status Board */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {[
          { label: "Sales OS", items: ["٣٢ فرصة نشطة", "٧ في مرحلة التوقيع", "١٢ تجديد قادم"], icon: DollarSign, color: "text-emerald-400" },
          { label: "Partnership OS", items: ["٨ شراكات نشطة", "٢ في مرحلة term sheet", "٣ للتفعيل قريباً"], icon: Users, color: "text-blue-400" },
          { label: "M&A OS", items: ["٤ أهداف قيد الدراسة", "١ في DD Room", "١ جاهز للعرض"], icon: GitBranch, color: "text-purple-400" },
        ].map((panel) => (
          <div key={panel.label} className="bg-card/50 border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <panel.icon className={`w-4 h-4 ${panel.color}`} />
              <span className="text-sm font-bold text-foreground">{panel.label}</span>
            </div>
            <ul className="space-y-1.5">
              {panel.items.map((item) => (
                <li key={item} className="flex items-center gap-2 text-xs text-muted-foreground">
                  <CheckCircle2 className="w-3 h-3 text-emerald-400 flex-shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

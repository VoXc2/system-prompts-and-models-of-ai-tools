"use client";

import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  GitBranch,
  Layers,
  Target,
  TrendingUp,
} from "lucide-react";

const MOCK_PMI = [
  {
    id: "pmi-001",
    name_ar: "تكامل تك هب — PMI الأساسي",
    program_type: "pmi",
    status: "planning",
    synergy_realized_pct: 0,
    issue_count_open: 3,
    day1_readiness: { score: 65, items: ["البنية التحتية", "الفريق", "البيانات"] },
    plan_30d: { completed: 4, total: 12 },
    plan_60d: { completed: 0, total: 18 },
    plan_90d: { completed: 0, total: 24 },
    risk_register: [
      { risk: "تأخر نقل البيانات", severity: "high" },
      { risk: "تعارض سياسات HR", severity: "medium" },
      { risk: "تأخر تكامل التقنية", severity: "medium" },
    ],
  },
];

type Severity = "high" | "medium" | "low";

const severityColors: Record<Severity, string> = {
  high: "text-red-400 bg-red-500/10 border-red-500/20",
  medium: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  low: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
};

const severityLabels: Record<Severity, string> = {
  high: "عالي",
  medium: "متوسط",
  low: "منخفض",
};

function PlanProgress({ label, completed, total }: { label: string; completed: number; total: number }) {
  const pct = total > 0 ? (completed / total) * 100 : 0;
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-muted-foreground">{label}</span>
        <span className="text-foreground font-medium">{completed}/{total}</span>
      </div>
      <div className="h-2 bg-secondary/40 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function PMIEngine() {
  return (
    <div className="p-6 space-y-5" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">PMI / Strategic PMO OS</h1>
          <p className="text-sm text-muted-foreground mt-1">خطط ٣٠/٦٠/٩٠ يوم — سجل المخاطر — تتبع التضافر</p>
        </div>
      </div>

      {MOCK_PMI.map((project) => (
        <div key={project.id} className="bg-card/50 border border-border rounded-2xl p-6 space-y-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Layers className="w-5 h-5 text-primary" />
                <h2 className="font-bold text-foreground text-lg">{project.name_ar}</h2>
              </div>
              <span className="text-xs bg-secondary/40 text-muted-foreground px-2 py-0.5 rounded-full">{project.program_type.toUpperCase()}</span>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-emerald-400">{project.synergy_realized_pct}٪</p>
              <p className="text-xs text-muted-foreground">التضافر المحقق</p>
            </div>
          </div>

          {/* Day 1 Readiness */}
          <div className="bg-secondary/20 rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Target className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-bold text-foreground">جاهزية اليوم الأول</h3>
              <span className={`text-sm font-bold mr-auto ${project.day1_readiness.score >= 80 ? "text-emerald-400" : project.day1_readiness.score >= 60 ? "text-amber-400" : "text-red-400"}`}>
                {project.day1_readiness.score}٪
              </span>
            </div>
            <div className="h-2 bg-secondary/40 rounded-full overflow-hidden mb-3">
              <div
                className={`h-full rounded-full ${project.day1_readiness.score >= 80 ? "bg-emerald-400" : project.day1_readiness.score >= 60 ? "bg-amber-400" : "bg-red-400"}`}
                style={{ width: `${project.day1_readiness.score}%` }}
              />
            </div>
            <div className="flex gap-2 flex-wrap">
              {project.day1_readiness.items.map((item) => (
                <span key={item} className="text-xs bg-secondary/40 text-muted-foreground px-2 py-1 rounded-lg flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {item}
                </span>
              ))}
            </div>
          </div>

          {/* 30/60/90 Plans */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-secondary/20 rounded-xl p-4">
              <p className="text-xs font-bold text-foreground mb-3">خطة ٣٠ يوم</p>
              <PlanProgress label="المهام" completed={project.plan_30d.completed} total={project.plan_30d.total} />
            </div>
            <div className="bg-secondary/20 rounded-xl p-4">
              <p className="text-xs font-bold text-foreground mb-3">خطة ٦٠ يوم</p>
              <PlanProgress label="المهام" completed={project.plan_60d.completed} total={project.plan_60d.total} />
            </div>
            <div className="bg-secondary/20 rounded-xl p-4">
              <p className="text-xs font-bold text-foreground mb-3">خطة ٩٠ يوم</p>
              <PlanProgress label="المهام" completed={project.plan_90d.completed} total={project.plan_90d.total} />
            </div>
          </div>

          {/* Risk Register */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold text-foreground">سجل المخاطر</h3>
              <span className="mr-auto text-xs text-red-400 font-bold">{project.issue_count_open} قضايا مفتوحة</span>
            </div>
            <div className="space-y-2">
              {project.risk_register.map((risk, i) => (
                <div key={i} className={`flex items-center justify-between p-3 rounded-xl border ${severityColors[risk.severity as Severity]}`}>
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span className="text-sm">{risk.risk}</span>
                  </div>
                  <span className="text-xs font-medium">{severityLabels[risk.severity as Severity]}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

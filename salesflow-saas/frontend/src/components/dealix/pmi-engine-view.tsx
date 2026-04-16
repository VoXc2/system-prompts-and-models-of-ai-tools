"use client";

import { GitBranch, CheckCircle2, Clock, AlertTriangle, TrendingUp, Users } from "lucide-react";

const milestones = [
  { name: "اليوم الأول", type: "day1", status: "completed", progress: 100 },
  { name: "خطة 30 يوم", type: "30_day", status: "completed", progress: 100 },
  { name: "خطة 60 يوم", type: "60_day", status: "on_track", progress: 72 },
  { name: "خطة 90 يوم", type: "90_day", status: "pending", progress: 20 },
];

const workstreams = [
  { name: "دمج الأنظمة التقنية", owner: "فريق التقنية", status: "in_progress", progress: 65, escalations: 0 },
  { name: "توحيد العمليات المالية", owner: "فريق المالية", status: "in_progress", progress: 45, escalations: 1 },
  { name: "دمج فرق المبيعات", owner: "فريق المبيعات", status: "in_progress", progress: 80, escalations: 0 },
  { name: "محاذاة الثقافة والموارد البشرية", owner: "فريق HR", status: "blocked", progress: 30, escalations: 2 },
  { name: "توحيد البنية التحتية", owner: "فريق DevOps", status: "pending", progress: 10, escalations: 0 },
];

const risks = [
  { title: "مقاومة التغيير من فريق الشركة المستحوذ عليها", severity: "high", status: "mitigating" },
  { title: "تأخر ترحيل قاعدة البيانات", severity: "medium", status: "open" },
  { title: "فقدان عملاء رئيسيين أثناء الانتقال", severity: "critical", status: "mitigating" },
];

export function PMIEngineView() {
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-right">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-1">محرك التكامل الاستراتيجي — 30/60/90</h1>
        <p className="text-sm text-muted-foreground">تكامل ما بعد الاستحواذ — تقنية المستقبل</p>
      </div>

      {/* Synergy Tracker */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "التآزر المستهدف", value: "3.2M ر.س", icon: TrendingUp, color: "text-emerald-500" },
          { label: "التآزر المحقق", value: "1.1M ر.س", icon: CheckCircle2, color: "text-blue-500" },
          { label: "مسارات العمل النشطة", value: "5", icon: GitBranch, color: "text-purple-500" },
          { label: "التصعيدات", value: "3", icon: AlertTriangle, color: "text-red-500" },
        ].map((s, i) => (
          <div key={i} className="glass-card p-4">
            <s.icon className={`w-5 h-5 ${s.color} mb-2`} />
            <p className="text-xs text-muted-foreground font-bold">{s.label}</p>
            <p className="text-xl font-bold mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Milestones Timeline */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-bold mb-4">المحطات الزمنية</h2>
        <div className="flex items-center gap-2">
          {milestones.map((m, i) => (
            <div key={i} className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                  m.status === "completed" ? "bg-emerald-500 text-white" :
                  m.status === "on_track" ? "bg-amber-500 text-white" :
                  "bg-secondary text-muted-foreground"
                }`}>
                  {m.status === "completed" ? "✓" : m.progress + "%"}
                </div>
                <div className="flex-1 h-1 bg-secondary rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${
                    m.status === "completed" ? "bg-emerald-500" : "bg-amber-500"
                  }`} style={{ width: `${m.progress}%` }} />
                </div>
              </div>
              <p className="text-xs font-bold text-center">{m.name}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Workstreams */}
      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-border/50">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-primary" />
            مسارات العمل
          </h2>
        </div>
        <div className="divide-y divide-border/20">
          {workstreams.map((w, i) => (
            <div key={i} className="flex items-center justify-between p-4 hover:bg-secondary/20 transition-colors">
              <div className="text-right flex-1">
                <p className="text-sm font-bold">{w.name}</p>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                  <Users className="w-3 h-3" /> {w.owner}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className="w-24 h-1.5 bg-secondary rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${
                    w.status === "blocked" ? "bg-red-500" : w.progress > 70 ? "bg-emerald-500" : "bg-amber-500"
                  }`} style={{ width: `${w.progress}%` }} />
                </div>
                <span className="text-xs font-bold w-10 text-left">{w.progress}%</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                  w.status === "in_progress" ? "bg-blue-500/20 text-blue-400" :
                  w.status === "blocked" ? "bg-red-500/20 text-red-400" :
                  "bg-gray-500/20 text-gray-400"
                }`}>
                  {w.status === "in_progress" ? "قيد التنفيذ" : w.status === "blocked" ? "معطل" : "معلق"}
                </span>
                {w.escalations > 0 && (
                  <span className="text-xs bg-red-500/20 text-red-400 px-2 py-0.5 rounded-full font-bold">
                    {w.escalations} تصعيد
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Register */}
      <div className="glass-card p-6 border border-red-500/20 bg-red-500/5">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          سجل المخاطر
        </h2>
        <div className="space-y-2">
          {risks.map((r, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-card/50 border border-border/30">
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${
                  r.severity === "critical" ? "bg-red-600" :
                  r.severity === "high" ? "bg-red-500" : "bg-amber-500"
                }`} />
                <p className="text-sm font-bold">{r.title}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                  r.severity === "critical" ? "bg-red-600/20 text-red-400" :
                  r.severity === "high" ? "bg-red-500/20 text-red-400" : "bg-amber-500/20 text-amber-400"
                }`}>{r.severity}</span>
                <span className="text-xs text-muted-foreground">{r.status === "mitigating" ? "قيد المعالجة" : "مفتوح"}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

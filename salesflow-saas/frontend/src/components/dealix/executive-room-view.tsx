"use client";

import {
  Shield, AlertTriangle, CheckCircle2, Clock, FileText,
  TrendingUp, BarChart3, Link2, Cpu, Globe, ArrowUpRight,
} from "lucide-react";

const pendingApprovals = [
  { action: "اعتماد خصم 18% — شركة الأفق", class: "director", impact: "45,000 ر.س", urgency: "عاجل" },
  { action: "تفعيل شراكة — مجموعة النور", class: "vp", impact: "200,000 ر.س", urgency: "متوسط" },
  { action: "إرسال عرض استحواذ — تقنية المستقبل", class: "c_level", impact: "2,500,000 ر.س", urgency: "عاجل" },
];

const riskItems = [
  { name: "تأخر DD لهدف الاستحواذ #3", severity: "high", category: "استحواذ" },
  { name: "انخفاض تحويل القمع 12%", severity: "medium", category: "مبيعات" },
  { name: "شريك رئيسي — صحة متدنية", severity: "high", category: "شراكات" },
];

const surfaces = [
  { id: "approvals", label: "مركز الاعتماد", icon: CheckCircle2, count: 3, color: "text-amber-500" },
  { id: "evidence", label: "حزم الأدلة", icon: FileText, count: 12, color: "text-blue-500" },
  { id: "risk", label: "خريطة المخاطر", icon: AlertTriangle, count: 5, color: "text-red-500" },
  { id: "violations", label: "مخالفات السياسات", icon: Shield, count: 1, color: "text-orange-500" },
  { id: "forecast", label: "فعلي vs متوقع", icon: TrendingUp, count: 0, color: "text-emerald-500" },
  { id: "compliance", label: "الامتثال السعودي", icon: Globe, count: 0, color: "text-purple-500" },
  { id: "models", label: "توجيه النماذج", icon: Cpu, count: 0, color: "text-cyan-500" },
  { id: "connectors", label: "صحة الموصلات", icon: Link2, count: 0, color: "text-teal-500" },
];

export function ExecutiveRoomView() {
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="text-right">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-1">غرفة القيادة التنفيذية</h1>
        <p className="text-sm text-muted-foreground">القرار، الأثر المالي، البدائل، المخاطر، الصلاحية، قابلية الرجوع، المسؤول</p>
      </div>

      {/* Surface Tiles */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {surfaces.map((s) => (
          <div key={s.id} className="glass-card p-4 border border-border/50 hover:border-primary/30 transition-all cursor-pointer group">
            <div className="flex items-center justify-between mb-2">
              <s.icon className={`w-5 h-5 ${s.color}`} />
              {s.count > 0 && (
                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-bold">{s.count}</span>
              )}
            </div>
            <p className="text-sm font-bold">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Pending Approvals */}
      <div className="glass-card p-6 border border-amber-500/20 bg-amber-500/5">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-amber-500" />
          اعتمادات معلقة
          <span className="text-xs bg-amber-500/20 text-amber-400 px-2 py-0.5 rounded-full">{pendingApprovals.length}</span>
        </h2>
        <div className="space-y-3">
          {pendingApprovals.map((a, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-card/50 border border-border/30">
              <div className="text-right">
                <p className="text-sm font-bold">{a.action}</p>
                <p className="text-xs text-muted-foreground">مستوى: {a.class} — أثر: {a.impact}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-1 rounded-full font-bold ${
                  a.urgency === "عاجل" ? "bg-red-500/20 text-red-400" : "bg-yellow-500/20 text-yellow-400"
                }`}>
                  {a.urgency}
                </span>
                <button className="text-xs px-3 py-1.5 rounded-lg bg-primary text-primary-foreground font-bold">اعتمد</button>
                <button className="text-xs px-3 py-1.5 rounded-lg border border-border font-bold">رفض</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Heatmap Summary */}
      <div className="glass-card p-6 border border-red-500/20 bg-red-500/5">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          المخاطر النشطة
        </h2>
        <div className="space-y-2">
          {riskItems.map((r, i) => (
            <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-card/50 border border-border/30">
              <div className="flex items-center gap-3">
                <div className={`w-2 h-2 rounded-full ${
                  r.severity === "high" ? "bg-red-500" : r.severity === "medium" ? "bg-amber-500" : "bg-green-500"
                }`} />
                <p className="text-sm font-bold">{r.name}</p>
              </div>
              <span className="text-xs text-muted-foreground">{r.category}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Five Planes Status */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-primary" />
          حالة الأنظمة الخمسة
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {[
            { plane: "Decision", ar: "القرار", status: "active", icon: "🧠" },
            { plane: "Execution", ar: "التنفيذ", status: "active", icon: "⚡" },
            { plane: "Trust", ar: "الثقة", status: "active", icon: "🛡️" },
            { plane: "Data", ar: "البيانات", status: "active", icon: "📊" },
            { plane: "Operating", ar: "التشغيل", status: "active", icon: "🔧" },
          ].map((p) => (
            <div key={p.plane} className="text-center p-3 rounded-xl border border-border/50 bg-card/50">
              <span className="text-2xl">{p.icon}</span>
              <p className="text-sm font-bold mt-1">{p.ar}</p>
              <p className="text-xs text-muted-foreground">{p.plane}</p>
              <span className="inline-block mt-1 text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full">
                {p.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

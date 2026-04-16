"use client";

import { Building2, Search, FileCheck, FileSignature, Scale, TrendingUp, AlertTriangle } from "lucide-react";

const targets = [
  { name: "تقنية المستقبل", status: "dd_active", value: "2.5M", fit: 88, ddProgress: 65 },
  { name: "حلول السحابة العربية", status: "screening", value: "1.8M", fit: 72, ddProgress: 0 },
  { name: "شركة البرمجيات المتقدمة", status: "offer_stage", value: "5.2M", fit: 91, ddProgress: 100 },
  { name: "مؤسسة الرقمنة الوطنية", status: "sourced", value: "800K", fit: 55, ddProgress: 0 },
];

const ddStreams = [
  { type: "مالي", status: "مكتمل", progress: 100, icon: "💰" },
  { type: "قانوني", status: "قيد التنفيذ", progress: 70, icon: "⚖️" },
  { type: "منتج", status: "قيد التنفيذ", progress: 45, icon: "🔧" },
  { type: "أمني", status: "معلق", progress: 0, icon: "🛡️" },
  { type: "تجاري", status: "قيد التنفيذ", progress: 30, icon: "📊" },
];

const statusMap: Record<string, { label: string; color: string }> = {
  sourced: { label: "مكتشف", color: "bg-blue-500/20 text-blue-400" },
  screening: { label: "فرز", color: "bg-yellow-500/20 text-yellow-400" },
  dd_active: { label: "فحص نافي للجهالة", color: "bg-purple-500/20 text-purple-400" },
  offer_stage: { label: "مرحلة العرض", color: "bg-amber-500/20 text-amber-400" },
  negotiation: { label: "تفاوض", color: "bg-orange-500/20 text-orange-400" },
  closed: { label: "مكتمل", color: "bg-emerald-500/20 text-emerald-400" },
};

export function MAPipelineView() {
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-end">
        <div className="text-right">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-1">مسار الاستحواذ والتطوير المؤسسي</h1>
          <p className="text-sm text-muted-foreground">اكتشاف → فرز → فحص → تقييم → عرض → تفاوض → إغلاق → دمج</p>
        </div>
        <button className="px-4 py-2.5 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-bold shadow-lg shadow-primary/25 flex items-center gap-2">
          <Search className="w-4 h-4" />
          هدف جديد
        </button>
      </div>

      {/* Pipeline Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "إجمالي الأهداف", value: "4", icon: Building2, color: "text-blue-500" },
          { label: "فحص نافي للجهالة نشط", value: "1", icon: FileCheck, color: "text-purple-500" },
          { label: "مرحلة العرض", value: "1", icon: FileSignature, color: "text-amber-500" },
          { label: "إجمالي القيمة", value: "10.3M ر.س", icon: Scale, color: "text-emerald-500" },
        ].map((s, i) => (
          <div key={i} className="glass-card p-4">
            <s.icon className={`w-5 h-5 ${s.color} mb-2`} />
            <p className="text-xs text-muted-foreground font-bold">{s.label}</p>
            <p className="text-xl font-bold mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Targets Table */}
      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-border/50">
          <h2 className="text-lg font-bold">أهداف الاستحواذ</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/30 text-muted-foreground text-xs">
                <th className="text-right p-3 font-bold">الشركة</th>
                <th className="text-right p-3 font-bold">الحالة</th>
                <th className="text-right p-3 font-bold">القيمة التقديرية</th>
                <th className="text-right p-3 font-bold">الملاءمة الاستراتيجية</th>
                <th className="text-right p-3 font-bold">تقدم DD</th>
              </tr>
            </thead>
            <tbody>
              {targets.map((t, i) => (
                <tr key={i} className="border-b border-border/20 hover:bg-secondary/30 transition-colors cursor-pointer">
                  <td className="p-3 font-bold">{t.name}</td>
                  <td className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${statusMap[t.status]?.color}`}>
                      {statusMap[t.status]?.label}
                    </span>
                  </td>
                  <td className="p-3 font-bold">{t.value} ر.س</td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div className="h-full bg-primary rounded-full" style={{ width: `${t.fit}%` }} />
                      </div>
                      <span className="text-xs font-bold">{t.fit}%</span>
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${t.ddProgress === 100 ? "bg-emerald-500" : "bg-amber-500"}`} style={{ width: `${t.ddProgress}%` }} />
                      </div>
                      <span className="text-xs font-bold">{t.ddProgress}%</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* DD Room */}
      <div className="glass-card p-6 border border-purple-500/20 bg-purple-500/5">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <FileCheck className="w-5 h-5 text-purple-500" />
          غرفة الفحص النافي للجهالة — تقنية المستقبل
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {ddStreams.map((d, i) => (
            <div key={i} className="text-center p-3 rounded-xl border border-border/50 bg-card/50">
              <span className="text-xl">{d.icon}</span>
              <p className="text-sm font-bold mt-1">{d.type}</p>
              <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden mt-2">
                <div className={`h-full rounded-full ${
                  d.progress === 100 ? "bg-emerald-500" : d.progress > 0 ? "bg-amber-500" : "bg-muted"
                }`} style={{ width: `${d.progress}%` }} />
              </div>
              <p className="text-xs text-muted-foreground mt-1">{d.status}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

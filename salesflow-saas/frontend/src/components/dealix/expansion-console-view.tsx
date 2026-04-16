"use client";

import { Globe, Rocket, Shield, TrendingUp, MapPin, AlertTriangle } from "lucide-react";

const markets = [
  { name: "الإمارات — دبي", status: "active", readiness: 95, regulatory: "ready", revenue: "850K" },
  { name: "مصر — القاهرة", status: "launched", readiness: 80, regulatory: "partial", revenue: "120K" },
  { name: "البحرين", status: "preparing", readiness: 60, regulatory: "ready", revenue: "0" },
  { name: "الكويت", status: "evaluating", readiness: 35, regulatory: "partial", revenue: "0" },
  { name: "المغرب", status: "scanning", readiness: 10, regulatory: "unknown", revenue: "0" },
];

const statusColors: Record<string, string> = {
  active: "bg-emerald-500/20 text-emerald-400",
  launched: "bg-blue-500/20 text-blue-400",
  preparing: "bg-amber-500/20 text-amber-400",
  evaluating: "bg-purple-500/20 text-purple-400",
  scanning: "bg-gray-500/20 text-gray-400",
};

const statusLabels: Record<string, string> = {
  active: "نشط",
  launched: "تم الإطلاق",
  preparing: "تحضير",
  evaluating: "تقييم",
  scanning: "مسح",
};

export function ExpansionConsoleView() {
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-end">
        <div className="text-right">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-1">وحدة تحكم التوسع</h1>
          <p className="text-sm text-muted-foreground">مسح → تقييم → تحضير → إطلاق → تحسين — مع قواعد وقف الخسارة</p>
        </div>
        <button className="px-4 py-2.5 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-bold shadow-lg shadow-primary/25 flex items-center gap-2">
          <Globe className="w-4 h-4" />
          سوق جديد
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "أسواق نشطة", value: "2", icon: Rocket, color: "text-emerald-500" },
          { label: "قيد التحضير", value: "1", icon: MapPin, color: "text-amber-500" },
          { label: "قيد المسح", value: "2", icon: Globe, color: "text-blue-500" },
          { label: "إجمالي الإيرادات", value: "970K ر.س", icon: TrendingUp, color: "text-purple-500" },
        ].map((s, i) => (
          <div key={i} className="glass-card p-4">
            <s.icon className={`w-5 h-5 ${s.color} mb-2`} />
            <p className="text-xs text-muted-foreground font-bold">{s.label}</p>
            <p className="text-xl font-bold mt-1">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-border/50">
          <h2 className="text-lg font-bold">خريطة الأسواق</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/30 text-muted-foreground text-xs">
                <th className="text-right p-3 font-bold">السوق</th>
                <th className="text-right p-3 font-bold">الحالة</th>
                <th className="text-right p-3 font-bold">الجاهزية</th>
                <th className="text-right p-3 font-bold">التنظيمي</th>
                <th className="text-right p-3 font-bold">الإيرادات</th>
              </tr>
            </thead>
            <tbody>
              {markets.map((m, i) => (
                <tr key={i} className="border-b border-border/20 hover:bg-secondary/30 transition-colors cursor-pointer">
                  <td className="p-3 font-bold">{m.name}</td>
                  <td className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${statusColors[m.status]}`}>
                      {statusLabels[m.status]}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div className="h-full bg-primary rounded-full" style={{ width: `${m.readiness}%` }} />
                      </div>
                      <span className="text-xs font-bold">{m.readiness}%</span>
                    </div>
                  </td>
                  <td className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                      m.regulatory === "ready" ? "bg-emerald-500/20 text-emerald-400" :
                      m.regulatory === "partial" ? "bg-amber-500/20 text-amber-400" :
                      "bg-gray-500/20 text-gray-400"
                    }`}>
                      {m.regulatory === "ready" ? "جاهز" : m.regulatory === "partial" ? "جزئي" : "غير معروف"}
                    </span>
                  </td>
                  <td className="p-3 font-bold">{m.revenue} ر.س</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

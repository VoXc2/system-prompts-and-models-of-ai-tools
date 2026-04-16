"use client";

import { Handshake, TrendingUp, Users, Star, Activity, ArrowUpRight, Shield } from "lucide-react";

const partners = [
  { name: "مجموعة النور للتقنية", type: "استراتيجي", status: "نشط", tier: "بلاتيني", score: 92, revenue: "1.2M" },
  { name: "شركة البيانات السعودية", type: "تقنية", status: "تقييم", tier: "ذهبي", score: 78, revenue: "0" },
  { name: "مؤسسة الأفق للاستشارات", type: "قناة", status: "نشط", tier: "فضي", score: 85, revenue: "450K" },
  { name: "حلول المستقبل الرقمية", type: "إحالة", status: "محتمل", tier: "قياسي", score: 65, revenue: "0" },
];

const scorecardHighlights = [
  { metric: "إيرادات الشركاء", value: "1.65M ر.س", trend: "+22%", color: "text-emerald-500" },
  { metric: "صفقات مشتركة", value: "34", trend: "+15%", color: "text-blue-500" },
  { metric: "هامش المساهمة", value: "28%", trend: "+3%", color: "text-purple-500" },
  { metric: "شركاء نشطون", value: "12", trend: "+2", color: "text-amber-500" },
];

export function PartnershipRoomView() {
  return (
    <div className="p-4 md:p-8 max-w-7xl mx-auto space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-end">
        <div className="text-right">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight mb-1">غرفة الشراكات</h1>
          <p className="text-sm text-muted-foreground">اكتشاف → تقييم → تفعيل → متابعة → توسع</p>
        </div>
        <button className="px-4 py-2.5 rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground text-sm font-bold shadow-lg shadow-primary/25 flex items-center gap-2">
          <Handshake className="w-4 h-4" />
          شريك جديد
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {scorecardHighlights.map((s, i) => (
          <div key={i} className="glass-card p-4">
            <p className="text-xs text-muted-foreground font-bold">{s.metric}</p>
            <p className="text-xl font-bold mt-1">{s.value}</p>
            <p className={`text-xs ${s.color} font-bold mt-1`}>{s.trend}</p>
          </div>
        ))}
      </div>

      {/* Partners Table */}
      <div className="glass-card overflow-hidden">
        <div className="p-4 border-b border-border/50">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Users className="w-5 h-5 text-primary" />
            سجل الشركاء
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border/30 text-muted-foreground text-xs">
                <th className="text-right p-3 font-bold">الشريك</th>
                <th className="text-right p-3 font-bold">النوع</th>
                <th className="text-right p-3 font-bold">الحالة</th>
                <th className="text-right p-3 font-bold">المستوى</th>
                <th className="text-right p-3 font-bold">الملاءمة</th>
                <th className="text-right p-3 font-bold">الإيرادات</th>
              </tr>
            </thead>
            <tbody>
              {partners.map((p, i) => (
                <tr key={i} className="border-b border-border/20 hover:bg-secondary/30 transition-colors cursor-pointer">
                  <td className="p-3 font-bold">{p.name}</td>
                  <td className="p-3 text-muted-foreground">{p.type}</td>
                  <td className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                      p.status === "نشط" ? "bg-emerald-500/20 text-emerald-400" :
                      p.status === "تقييم" ? "bg-amber-500/20 text-amber-400" :
                      "bg-blue-500/20 text-blue-400"
                    }`}>{p.status}</span>
                  </td>
                  <td className="p-3">
                    <span className="flex items-center gap-1">
                      <Star className="w-3 h-3 text-amber-400" />
                      <span className="text-xs">{p.tier}</span>
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                        <div className="h-full bg-primary rounded-full" style={{ width: `${p.score}%` }} />
                      </div>
                      <span className="text-xs font-bold">{p.score}</span>
                    </div>
                  </td>
                  <td className="p-3 font-bold">{p.revenue} ر.س</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

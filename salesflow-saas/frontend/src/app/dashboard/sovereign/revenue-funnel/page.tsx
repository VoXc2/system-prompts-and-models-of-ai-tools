"use client";

import { useState } from "react";
import {
  DollarSign,
  Users,
  Target,
  TrendingUp,
  ArrowLeft,
  Filter,
} from "lucide-react";
import Link from "next/link";

const FUNNEL_STAGES = [
  { key: "awareness", label: "الوعي", labelEn: "Awareness", color: "bg-blue-500", count: 0, value: 0 },
  { key: "interest", label: "الاهتمام", labelEn: "Interest", color: "bg-indigo-500", count: 0, value: 0 },
  { key: "consideration", label: "التقييم", labelEn: "Consideration", color: "bg-purple-500", count: 0, value: 0 },
  { key: "intent", label: "نية الشراء", labelEn: "Intent", color: "bg-amber-500", count: 0, value: 0 },
  { key: "evaluation", label: "المفاوضة", labelEn: "Evaluation", color: "bg-orange-500", count: 0, value: 0 },
  { key: "closed", label: "الإغلاق", labelEn: "Closed Won", color: "bg-emerald-500", count: 0, value: 0 },
];

const SUMMARY_CARDS = [
  { label: "إجمالي العملاء المحتملين", labelEn: "Total Leads", value: "—", icon: Users, color: "text-blue-500 bg-blue-500/10" },
  { label: "قيمة خط الأنابيب", labelEn: "Pipeline Value", value: "— ر.س", icon: DollarSign, color: "text-emerald-500 bg-emerald-500/10" },
  { label: "معدل التحويل", labelEn: "Conversion Rate", value: "—%", icon: Target, color: "text-purple-500 bg-purple-500/10" },
  { label: "متوسط حجم الصفقة", labelEn: "Avg Deal Size", value: "— ر.س", icon: TrendingUp, color: "text-amber-500 bg-amber-500/10" },
];

export default function RevenueFunnelPage() {
  const [stages] = useState(FUNNEL_STAGES);

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">مركز قمع الإيرادات</h1>
        <p className="text-sm text-muted-foreground">Revenue Funnel — إدارة مراحل القمع البيعي</p>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {SUMMARY_CARDS.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.labelEn} className="bg-card border border-border rounded-2xl p-5 flex items-start gap-4">
              <div className={`w-11 h-11 rounded-xl flex items-center justify-center shrink-0 ${card.color}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{card.value}</p>
                <p className="text-sm font-medium">{card.label}</p>
                <p className="text-[10px] text-muted-foreground">{card.labelEn}</p>
              </div>
            </div>
          );
        })}
      </section>

      <section className="bg-card border border-border rounded-2xl p-6">
        <h2 className="text-lg font-bold mb-1">مراحل القمع</h2>
        <p className="text-xs text-muted-foreground mb-6">Funnel Stages</p>

        <div className="space-y-3">
          {stages.map((stage, idx) => {
            const widthPct = Math.max(20, 100 - idx * 13);
            return (
              <div key={stage.key} className="flex items-center gap-4">
                <div className="w-28 shrink-0 text-right">
                  <p className="text-sm font-medium">{stage.label}</p>
                  <p className="text-[10px] text-muted-foreground">{stage.labelEn}</p>
                </div>
                <div className="flex-1">
                  <div
                    className={`${stage.color} h-10 rounded-xl flex items-center justify-between px-4 transition-all`}
                    style={{ width: `${widthPct}%` }}
                  >
                    <span className="text-white text-xs font-bold">{stage.count} عميل</span>
                    <span className="text-white/80 text-xs">{stage.value.toLocaleString("ar-SA")} ر.س</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="bg-card border border-border rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold">الربط بمسار الصفقات</h2>
            <p className="text-xs text-muted-foreground">Link to CRM Pipeline</p>
          </div>
          <Link
            href="/dashboard"
            className="flex items-center gap-2 px-4 py-2 bg-primary/10 text-primary text-xs font-bold rounded-xl border border-primary/20 hover:bg-primary/20 transition-colors"
          >
            <span>الذهاب لمسار الصفقات</span>
            <ArrowLeft className="w-4 h-4" />
          </Link>
        </div>
        <div className="flex items-center gap-3 text-muted-foreground">
          <Filter className="w-10 h-10 opacity-20" />
          <p className="text-sm">يمكنك إدارة تفاصيل كل صفقة من خلال مسار الصفقات في اللوحة الرئيسية.</p>
        </div>
      </section>
    </div>
  );
}

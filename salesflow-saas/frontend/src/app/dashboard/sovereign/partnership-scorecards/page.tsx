"use client";

import { useEffect, useState } from "react";
import { Award, Loader2, Star } from "lucide-react";

interface Scorecard {
  id: string;
  partner_name: string;
  overall_score: number;
  revenue_contribution: number;
  lead_quality_score: number;
  sla_compliance_pct: number;
  satisfaction_score: number;
  contribution_margin: number;
  period: string;
}

const getScoreColor = (score: number) => {
  if (score >= 80) return "text-emerald-500";
  if (score >= 60) return "text-amber-500";
  return "text-red-500";
};

const getScoreBg = (score: number) => {
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-amber-500";
  return "bg-red-500";
};

export default function PartnershipScorecardsPage() {
  const [cards, setCards] = useState<Scorecard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/partnerships/scorecards")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setCards(Array.isArray(d) ? d : d.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold text-foreground">بطاقات أداء الشراكات</h1>
        <p className="text-sm text-muted-foreground">Partnership Scorecards — تقييم شامل لأداء الشركاء</p>
      </header>

      {cards.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Award className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد بطاقات أداء بعد</p>
          <p className="text-sm text-muted-foreground/70">No scorecards available yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {cards.map((sc) => (
            <div key={sc.id} className="bg-card border border-border rounded-2xl p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-5">
                <div>
                  <h3 className="font-bold text-base">{sc.partner_name}</h3>
                  <p className="text-[10px] text-muted-foreground">{sc.period}</p>
                </div>
                <div className="text-center">
                  <p className={`text-3xl font-bold ${getScoreColor(sc.overall_score)}`}>{sc.overall_score}</p>
                  <p className="text-[10px] text-muted-foreground">النتيجة الإجمالية</p>
                </div>
              </div>

              <div className="space-y-3">
                {[
                  { label: "مساهمة الإيرادات", labelEn: "Revenue Contribution", value: `${sc.revenue_contribution.toLocaleString("ar-SA")} ر.س` },
                  { label: "جودة العملاء", labelEn: "Lead Quality", value: `${sc.lead_quality_score}/100` },
                  { label: "الالتزام بالاتفاقية", labelEn: "SLA Compliance", value: `${sc.sla_compliance_pct}%` },
                  { label: "رضا العملاء", labelEn: "Satisfaction", value: `${sc.satisfaction_score}/100` },
                  { label: "هامش المساهمة", labelEn: "Contribution Margin", value: `${sc.contribution_margin}%` },
                ].map((metric) => (
                  <div key={metric.labelEn} className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-medium">{metric.label}</p>
                      <p className="text-[10px] text-muted-foreground">{metric.labelEn}</p>
                    </div>
                    <span className="text-sm font-bold">{metric.value}</span>
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t border-border/50">
                <div className="flex items-center gap-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className={`w-4 h-4 ${
                        star <= Math.round(sc.overall_score / 20)
                          ? "text-amber-400 fill-amber-400"
                          : "text-muted-foreground/20"
                      }`}
                    />
                  ))}
                  <span className="text-xs text-muted-foreground mr-2">
                    {Math.round(sc.overall_score / 20)}/5
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

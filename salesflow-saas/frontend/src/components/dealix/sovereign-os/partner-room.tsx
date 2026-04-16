"use client";

import {
  Activity,
  CheckCircle2,
  DollarSign,
  Globe,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";

const STAGES: Record<string, string> = {
  scouting: "الاستكشاف",
  fit_scoring: "تقييم الملاءمة",
  economics: "الاقتصاديات",
  structure_design: "هيكل الشراكة",
  term_sheet: "Term Sheet",
  approval: "الاعتماد",
  signature: "التوقيع",
  activation: "التفعيل",
  scorecard: "بطاقة الأداء",
  expansion: "التوسع",
};

const STAGE_ORDER = Object.keys(STAGES);

const MOCK_PARTNERS = [
  {
    id: "1",
    name_ar: "شركة الأفق التقنية",
    stage: "term_sheet",
    type: "reseller",
    fit_score: 89,
    rev_share_pct: 15,
    exclusivity: true,
    health_score: null,
    contribution_sar: null,
    renewal_days: null,
  },
  {
    id: "2",
    name_ar: "مؤسسة الشريك الذهبي",
    stage: "scorecard",
    type: "strategic",
    fit_score: 94,
    rev_share_pct: 12,
    exclusivity: false,
    health_score: 88,
    contribution_sar: 1800000,
    renewal_days: 90,
  },
  {
    id: "3",
    name_ar: "ويب تك للحلول",
    stage: "activation",
    type: "technology",
    fit_score: 77,
    rev_share_pct: 10,
    exclusivity: false,
    health_score: null,
    contribution_sar: null,
    renewal_days: null,
  },
  {
    id: "4",
    name_ar: "البنية الرقمية للتحول",
    stage: "scouting",
    type: "referral",
    fit_score: 61,
    rev_share_pct: null,
    exclusivity: false,
    health_score: null,
    contribution_sar: null,
    renewal_days: null,
  },
];

const typeColors: Record<string, string> = {
  reseller: "bg-blue-500/10 text-blue-400",
  strategic: "bg-purple-500/10 text-purple-400",
  technology: "bg-emerald-500/10 text-emerald-400",
  referral: "bg-amber-500/10 text-amber-400",
};

const typeLabels: Record<string, string> = {
  reseller: "موزّع",
  strategic: "استراتيجي",
  technology: "تقني",
  referral: "إحالة",
};

function StageProgress({ stage }: { stage: string }) {
  const idx = STAGE_ORDER.indexOf(stage);
  return (
    <div className="flex items-center gap-0.5">
      {STAGE_ORDER.map((s, i) => (
        <div
          key={s}
          className={`h-1.5 flex-1 rounded-full ${
            i < idx ? "bg-primary" : i === idx ? "bg-primary/70 animate-pulse" : "bg-secondary/40"
          }`}
        />
      ))}
    </div>
  );
}

function HealthBadge({ score }: { score: number }) {
  const color = score >= 80 ? "text-emerald-400" : score >= 60 ? "text-amber-400" : "text-red-400";
  return (
    <div className="flex items-center gap-1.5">
      <Activity className={`w-4 h-4 ${color}`} />
      <span className={`text-sm font-bold ${color}`}>{score}</span>
    </div>
  );
}

export function PartnerRoom() {
  return (
    <div className="p-6 space-y-5" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">غرفة الشراكات</h1>
          <p className="text-sm text-muted-foreground mt-1">دورة الشراكة الكاملة — من الاستكشاف إلى التوسع</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-foreground">١١.٢M SAR</p>
          <p className="text-xs text-muted-foreground">هامش المساهمة المتوقع</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "شراكات نشطة", value: "٨", icon: Users, color: "text-primary" },
          { label: "في Term Sheet", value: "١", icon: Globe, color: "text-amber-400" },
          { label: "تفعيل هذا الشهر", value: "٢", icon: Zap, color: "text-emerald-400" },
          { label: "متوسط الصحة", value: "٨٨٪", icon: Activity, color: "text-blue-400" },
        ].map((s) => (
          <div key={s.label} className="bg-card/50 border border-border rounded-2xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <s.icon className={`w-4 h-4 ${s.color}`} />
              <p className="text-xs text-muted-foreground">{s.label}</p>
            </div>
            <p className="text-2xl font-bold text-foreground">{s.value}</p>
          </div>
        ))}
      </div>

      <div className="space-y-3">
        {MOCK_PARTNERS.map((partner) => (
          <div key={partner.id} className="bg-card/50 border border-border rounded-2xl p-5 hover:border-primary/20 transition-all">
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-bold text-foreground">{partner.name_ar}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${typeColors[partner.type]}`}>
                    {typeLabels[partner.type]}
                  </span>
                  {partner.exclusivity && (
                    <span className="text-xs bg-purple-500/10 text-purple-400 px-2 py-0.5 rounded-full">حصري</span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">{STAGES[partner.stage]}</p>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-sm font-bold text-foreground">ملاءمة {partner.fit_score}٪</p>
                {partner.health_score && <HealthBadge score={partner.health_score} />}
              </div>
            </div>

            <StageProgress stage={partner.stage} />

            <div className="mt-3 grid grid-cols-2 md:grid-cols-4 gap-2">
              {partner.rev_share_pct && (
                <div className="bg-secondary/20 rounded-xl p-2.5">
                  <p className="text-xs text-muted-foreground">حصة الإيراد</p>
                  <p className="text-sm font-bold text-foreground">{partner.rev_share_pct}٪</p>
                </div>
              )}
              {partner.contribution_sar && (
                <div className="bg-secondary/20 rounded-xl p-2.5">
                  <p className="text-xs text-muted-foreground">المساهمة</p>
                  <p className="text-sm font-bold text-foreground">
                    {(partner.contribution_sar / 1000000).toFixed(1)}M SAR
                  </p>
                </div>
              )}
              {partner.renewal_days && (
                <div className="bg-secondary/20 rounded-xl p-2.5">
                  <p className="text-xs text-muted-foreground">تجديد خلال</p>
                  <p className="text-sm font-bold text-amber-400">{partner.renewal_days} يوم</p>
                </div>
              )}
            </div>

            <div className="mt-3 flex gap-2">
              {partner.stage === "term_sheet" && (
                <button
                  type="button"
                  className="flex items-center gap-1.5 text-xs bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/20 px-3 py-1.5 rounded-lg transition-all"
                >
                  إرسال للاعتماد
                </button>
              )}
              <button
                type="button"
                className="flex items-center gap-1.5 text-xs bg-secondary/40 hover:bg-secondary/70 text-foreground px-3 py-1.5 rounded-lg transition-all"
              >
                <TrendingUp className="w-3.5 h-3.5" />
                بطاقة الأداء
              </button>
              {partner.stage !== "scouting" && (
                <button
                  type="button"
                  className="flex items-center gap-1.5 text-xs bg-primary/10 hover:bg-primary/20 text-primary px-3 py-1.5 rounded-lg transition-all mr-auto"
                >
                  <DollarSign className="w-3.5 h-3.5" />
                  تتبع الهامش
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

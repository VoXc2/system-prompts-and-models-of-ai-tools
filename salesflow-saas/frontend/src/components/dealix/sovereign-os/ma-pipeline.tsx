"use client";

import {
  BarChart3,
  Building2,
  ChevronLeft,
  DollarSign,
  FileSearch,
  GitMerge,
  Shield,
  TrendingUp,
} from "lucide-react";

const STAGES = [
  "sourcing",
  "screening",
  "ownership_mapping",
  "dd_room",
  "valuation",
  "ic_pack",
  "offer_strategy",
  "negotiation",
  "signing",
  "close",
];

const STAGE_LABELS: Record<string, string> = {
  sourcing: "الاستكشاف",
  screening: "التصفية",
  ownership_mapping: "تحليل الملكية",
  dd_room: "غرفة DD",
  valuation: "التقييم",
  ic_pack: "حزمة IC",
  offer_strategy: "استراتيجية العرض",
  negotiation: "التفاوض",
  signing: "التوقيع",
  close: "الإغلاق",
};

const MOCK_TARGETS = [
  {
    id: "1",
    name_ar: "شركة تك هب للحلول الرقمية",
    stage: "dd_room",
    strategic_fit_score: 92,
    valuation_range: { low: 9.5, mid: 12, high: 15 },
    offer_amount_sar: null,
    approval_required: true,
    dd_streams: ["قانوني ✓", "مالي ✓", "منتج ⏳", "أمن ⏳"],
  },
  {
    id: "2",
    name_ar: "مجموعة البيانات الذكية",
    stage: "valuation",
    strategic_fit_score: 78,
    valuation_range: { low: 4, mid: 5.5, high: 7 },
    offer_amount_sar: null,
    approval_required: false,
    dd_streams: ["قانوني ✓", "مالي ✓", "منتج ✓", "أمن ✓"],
  },
  {
    id: "3",
    name_ar: "بلات فورم العروض السعودية",
    stage: "ic_pack",
    strategic_fit_score: 85,
    valuation_range: { low: 7, mid: 9, high: 11 },
    offer_amount_sar: null,
    approval_required: true,
    dd_streams: ["قانوني ✓", "مالي ✓", "منتج ✓", "أمن ✓"],
  },
  {
    id: "4",
    name_ar: "نكست لوجيك لحلول المؤسسات",
    stage: "screening",
    strategic_fit_score: 65,
    valuation_range: { low: 2, mid: 3, high: 4 },
    offer_amount_sar: null,
    approval_required: false,
    dd_streams: [],
  },
];

function FitBadge({ score }: { score: number }) {
  const color = score >= 85 ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/20"
    : score >= 70 ? "text-amber-400 bg-amber-500/10 border-amber-500/20"
    : "text-red-400 bg-red-500/10 border-red-500/20";
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${color}`}>
      ملاءمة {score}٪
    </span>
  );
}

function StageBar({ stage }: { stage: string }) {
  const idx = STAGES.indexOf(stage);
  return (
    <div className="flex items-center gap-0.5 overflow-x-auto">
      {STAGES.map((s, i) => (
        <div
          key={s}
          className={`h-1.5 flex-1 rounded-full min-w-3 transition-all ${
            i < idx ? "bg-primary" : i === idx ? "bg-primary animate-pulse" : "bg-secondary/40"
          }`}
          title={STAGE_LABELS[s]}
        />
      ))}
    </div>
  );
}

export function MAPipeline() {
  return (
    <div className="p-6 space-y-5" dir="rtl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">لوحة الاستحواذ M&A</h1>
          <p className="text-sm text-muted-foreground mt-1">من الاستكشاف إلى الإغلاق — تنفيذ دائم ومحمي</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-foreground">٣٦M SAR</p>
          <p className="text-xs text-muted-foreground">إجمالي خط الاستحواذ</p>
        </div>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "أهداف نشطة", value: "٤", icon: Building2, color: "text-primary" },
          { label: "في DD Room", value: "١", icon: FileSearch, color: "text-amber-400" },
          { label: "تحتاج اعتماد", value: "٢", icon: Shield, color: "text-red-400" },
          { label: "متوسط الملاءمة", value: "٨٠٪", icon: TrendingUp, color: "text-emerald-400" },
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
        {MOCK_TARGETS.map((target) => (
          <div key={target.id} className="bg-card/50 border border-border rounded-2xl p-5 hover:border-primary/20 transition-all">
            <div className="flex items-start justify-between gap-3 mb-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Building2 className="w-4 h-4 text-muted-foreground" />
                  <h3 className="font-bold text-foreground">{target.name_ar}</h3>
                  {target.approval_required && (
                    <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded-full">يتطلب اعتماد</span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground">{STAGE_LABELS[target.stage]}</p>
              </div>
              <FitBadge score={target.strategic_fit_score} />
            </div>

            <StageBar stage={target.stage} />

            <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-3">
              <div className="bg-secondary/20 rounded-xl p-3">
                <p className="text-xs text-muted-foreground mb-1">نطاق التقييم</p>
                <p className="text-sm font-bold text-foreground">
                  {target.valuation_range.low}M — {target.valuation_range.high}M SAR
                </p>
              </div>
              <div className="bg-secondary/20 rounded-xl p-3">
                <p className="text-xs text-muted-foreground mb-1">نقطة الوسط</p>
                <p className="text-sm font-bold text-foreground">{target.valuation_range.mid}M SAR</p>
              </div>
              {target.dd_streams.length > 0 && (
                <div className="bg-secondary/20 rounded-xl p-3">
                  <p className="text-xs text-muted-foreground mb-1">مسارات DD</p>
                  <div className="flex flex-wrap gap-1">
                    {target.dd_streams.map((s) => (
                      <span key={s} className="text-xs text-muted-foreground">{s}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-3 flex gap-2">
              <button
                type="button"
                className="flex items-center gap-1.5 text-xs bg-secondary/40 hover:bg-secondary/70 text-foreground px-3 py-1.5 rounded-lg transition-all"
              >
                <BarChart3 className="w-3.5 h-3.5" />
                نموذج التضافر
              </button>
              <button
                type="button"
                className="flex items-center gap-1.5 text-xs bg-secondary/40 hover:bg-secondary/70 text-foreground px-3 py-1.5 rounded-lg transition-all"
              >
                <GitMerge className="w-3.5 h-3.5" />
                حزمة IC
              </button>
              <button
                type="button"
                className="flex items-center gap-1.5 text-xs bg-primary/10 hover:bg-primary/20 text-primary px-3 py-1.5 rounded-lg transition-all mr-auto"
              >
                <DollarSign className="w-3.5 h-3.5" />
                إرسال عرض
                <ChevronLeft className="w-3 h-3" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

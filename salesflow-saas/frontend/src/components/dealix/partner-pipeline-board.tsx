"use client";

import { useEffect, useState } from "react";

type PartnerDeal = {
  id: string; company_name: string; company_name_ar?: string;
  deal_type: string; stage: string; estimated_value: number;
  created_at: string;
};

const STAGES = [
  { key: "discovery", label: "استكشاف", en: "Discovery" },
  { key: "outreach", label: "تواصل", en: "Outreach" },
  { key: "negotiating", label: "تفاوض", en: "Negotiating" },
  { key: "term_sheet", label: "ورقة شروط", en: "Term Sheet" },
  { key: "due_diligence", label: "فحص العناية", en: "Due Diligence" },
  { key: "closed", label: "مغلق", en: "Closed" },
];

const STAGE_COLORS: Record<string, string> = {
  discovery: "border-t-blue-500",
  outreach: "border-t-indigo-500",
  negotiating: "border-t-yellow-500",
  term_sheet: "border-t-orange-500",
  due_diligence: "border-t-purple-500",
  closed: "border-t-emerald-500",
};

export function PartnerPipelineBoard({ deals: initialDeals }: { deals?: PartnerDeal[] }) {
  const [deals, setDeals] = useState<PartnerDeal[]>(initialDeals || []);

  useEffect(() => {
    if (initialDeals) return;
    const fetchDeals = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/v1/strategic-deals/`);
        if (res.ok) {
          const data = await res.json();
          setDeals((data.deals || []).map((d: Record<string, unknown>) => ({
            id: d.id, company_name: d.target_company_name || d.deal_title,
            company_name_ar: d.deal_title_ar, deal_type: d.deal_type,
            stage: d.status, estimated_value: d.estimated_value_sar || 0,
            created_at: d.created_at,
          })));
        }
      } catch { /* silent */ }
    };
    fetchDeals();
  }, [initialDeals]);
  const byStage: Record<string, PartnerDeal[]> = {};
  STAGES.forEach((s) => { byStage[s.key] = []; });
  deals.forEach((d) => {
    if (byStage[d.stage]) byStage[d.stage].push(d);
  });

  const totalValue = deals.reduce((sum, d) => sum + d.estimated_value, 0);

  return (
    <div className="space-y-4 p-6" dir="rtl">
      <div className="flex justify-between items-center">
        <div className="text-sm text-muted-foreground">
          إجمالي الأنبوب: <span className="font-bold text-foreground">{totalValue.toLocaleString()} SAR</span>
        </div>
        <h2 className="text-xl font-bold">أنبوب الشراكات | Partner Pipeline</h2>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {STAGES.map((stage) => {
          const stageDeals = byStage[stage.key] || [];
          const stageValue = stageDeals.reduce((sum, d) => sum + d.estimated_value, 0);
          return (
            <div key={stage.key} className="space-y-2">
              <div className={`text-center p-2 rounded border-t-2 ${STAGE_COLORS[stage.key] || "border-t-gray-400"} bg-border/5`}>
                <div className="text-xs font-semibold">{stage.label}</div>
                <div className="text-xs text-muted-foreground">{stage.en}</div>
                <div className="text-xs mt-1">{stageDeals.length} صفقة — {stageValue.toLocaleString()} SAR</div>
              </div>
              {stageDeals.map((deal) => (
                <div key={deal.id} className="glass-card p-3 border border-border/40 text-right">
                  <p className="text-sm font-medium truncate">{deal.company_name_ar || deal.company_name}</p>
                  <p className="text-xs text-muted-foreground">{deal.deal_type}</p>
                  <p className="text-xs font-bold mt-1">{deal.estimated_value.toLocaleString()} SAR</p>
                </div>
              ))}
            </div>
          );
        })}
      </div>

      {deals.length === 0 && (
        <p className="text-sm text-muted-foreground text-center py-8">لا توجد صفقات شراكات في الأنبوب</p>
      )}
    </div>
  );
}

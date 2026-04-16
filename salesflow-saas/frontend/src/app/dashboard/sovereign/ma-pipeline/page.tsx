"use client";

import { useEffect, useState } from "react";
import { Building2, Loader2, GitBranch } from "lucide-react";

interface MADeal {
  id: string;
  company_name: string;
  sector: string;
  status: string;
  valuation_sar: number;
  deal_type: string;
  created_at: string;
  priority: string;
}

const PIPELINE_COLUMNS: { key: string; label: string; color: string }[] = [
  { key: "identified", label: "تم التحديد", color: "border-t-gray-400" },
  { key: "screening", label: "فحص مبدئي", color: "border-t-blue-500" },
  { key: "dd_in_progress", label: "عناية واجبة", color: "border-t-amber-500" },
  { key: "negotiation", label: "تفاوض", color: "border-t-purple-500" },
  { key: "closing", label: "إغلاق", color: "border-t-emerald-500" },
  { key: "completed", label: "مكتمل", color: "border-t-emerald-700" },
];

const PRIORITY_DOT: Record<string, string> = {
  critical: "bg-red-500",
  high: "bg-orange-500",
  medium: "bg-amber-500",
  low: "bg-emerald-500",
};

export default function MAPipelinePage() {
  const [deals, setDeals] = useState<MADeal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/ma/pipeline")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setDeals(Array.isArray(d) ? d : d.items || []))
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
        <h1 className="text-2xl font-bold text-foreground">خط أنابيب الاستحواذ</h1>
        <p className="text-sm text-muted-foreground">M&A Pipeline — لوحة كانبان لصفقات الاستحواذ</p>
      </header>

      {deals.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <GitBranch className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد صفقات في خط الأنابيب</p>
          <p className="text-sm text-muted-foreground/70">No deals in the pipeline yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 overflow-x-auto">
          {PIPELINE_COLUMNS.map((col) => {
            const colDeals = deals.filter((d) => d.status === col.key);
            return (
              <div key={col.key} className="min-w-[220px]">
                <div className={`bg-card border border-border rounded-2xl border-t-4 ${col.color}`}>
                  <div className="px-4 py-3 border-b border-border/50">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold">{col.label}</span>
                      <span className="text-[10px] bg-muted px-2 py-0.5 rounded-full">{colDeals.length}</span>
                    </div>
                  </div>
                  <div className="p-3 space-y-2 min-h-[200px]">
                    {colDeals.length === 0 ? (
                      <p className="text-[10px] text-muted-foreground text-center py-8">فارغ</p>
                    ) : (
                      colDeals.map((deal) => (
                        <div key={deal.id} className="bg-muted/30 border border-border/50 rounded-xl p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <div className={`w-2 h-2 rounded-full ${PRIORITY_DOT[deal.priority] || PRIORITY_DOT.medium}`} />
                            <span className="text-xs font-bold truncate">{deal.company_name}</span>
                          </div>
                          <p className="text-[10px] text-muted-foreground mb-1">{deal.sector}</p>
                          <div className="flex items-center justify-between text-[10px]">
                            <span className="text-muted-foreground">{deal.deal_type}</span>
                            <span className="font-bold">{(deal.valuation_sar / 1_000_000).toFixed(1)}M</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

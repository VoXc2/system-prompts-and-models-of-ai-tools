"use client";

import { useEffect, useState } from "react";
import { Loader2, Lock, FileSearch, Shield } from "lucide-react";

interface DDTarget {
  id: string;
  company_name: string;
  sector: string;
  status: string;
  dd_phase: string;
  valuation_sar: number;
  access_level: string;
  assigned_team: string[];
  last_updated: string;
  completion_pct: number;
}

const STATUS_BADGE: Record<string, { class: string; label: string }> = {
  screening: { class: "bg-gray-500/10 text-gray-400 border-gray-500/20", label: "فحص مبدئي" },
  in_progress: { class: "bg-blue-500/10 text-blue-500 border-blue-500/20", label: "جارٍ" },
  review: { class: "bg-amber-500/10 text-amber-500 border-amber-500/20", label: "مراجعة" },
  completed: { class: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20", label: "مكتمل" },
  on_hold: { class: "bg-orange-500/10 text-orange-500 border-orange-500/20", label: "متوقف" },
  cancelled: { class: "bg-red-500/10 text-red-500 border-red-500/20", label: "ملغى" },
};

const ACCESS_BADGE: Record<string, { class: string; label: string }> = {
  full: { class: "bg-emerald-500/10 text-emerald-500", label: "وصول كامل" },
  restricted: { class: "bg-amber-500/10 text-amber-500", label: "وصول مقيد" },
  view_only: { class: "bg-gray-500/10 text-gray-400", label: "عرض فقط" },
};

export default function DDRoomPage() {
  const [targets, setTargets] = useState<DDTarget[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/sovereign/ma/targets")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setTargets(Array.isArray(d) ? d : d.items || []))
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
        <h1 className="text-2xl font-bold text-foreground">غرفة العناية الواجبة</h1>
        <p className="text-sm text-muted-foreground">Due Diligence Room — تفاصيل أهداف الاستحواذ وحالة DD</p>
      </header>

      {targets.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <FileSearch className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد أهداف استحواذ بعد</p>
          <p className="text-sm text-muted-foreground/70">No M&A targets yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {targets.map((t) => {
            const status = STATUS_BADGE[t.status] || STATUS_BADGE.screening;
            const access = ACCESS_BADGE[t.access_level] || ACCESS_BADGE.view_only;
            return (
              <div key={t.id} className="bg-card border border-border rounded-2xl p-6 hover:shadow-lg transition-shadow">
                <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <h3 className="font-bold text-base">{t.company_name}</h3>
                      <span className={`inline-flex px-2.5 py-1 rounded-full text-[10px] font-bold border ${status.class}`}>
                        {status.label}
                      </span>
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] ${access.class}`}>
                        <Lock className="w-3 h-3" />
                        {access.label}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground mb-3">
                      <span>القطاع: {t.sector}</span>
                      <span>•</span>
                      <span>التقييم: {t.valuation_sar.toLocaleString("ar-SA")} ر.س</span>
                      <span>•</span>
                      <span>المرحلة: {t.dd_phase}</span>
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
                      <Shield className="w-3 h-3" />
                      <span>الفريق: {t.assigned_team.join("، ")}</span>
                    </div>
                  </div>

                  <div className="w-32 shrink-0">
                    <div className="text-center mb-2">
                      <span className="text-2xl font-bold">{t.completion_pct}%</span>
                      <p className="text-[10px] text-muted-foreground">الإنجاز</p>
                    </div>
                    <div className="w-full bg-muted rounded-full h-2">
                      <div
                        className="bg-primary rounded-full h-2 transition-all"
                        style={{ width: `${t.completion_pct}%` }}
                      />
                    </div>
                  </div>
                </div>

                <p className="text-[10px] text-muted-foreground mt-3">
                  آخر تحديث: {new Date(t.last_updated).toLocaleDateString("ar-SA")}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { FileText, Loader2, Package, Filter } from "lucide-react";

interface EvidencePack {
  id: string;
  title: string;
  type: string;
  status: string;
  created_at: string;
  artifact_count: number;
  owner: string;
}

const STATUS_BADGE: Record<string, { class: string; label: string }> = {
  assembling: { class: "bg-gray-500/10 text-gray-400 border-gray-500/20", label: "قيد التجميع" },
  draft: { class: "bg-gray-500/10 text-gray-400 border-gray-500/20", label: "مسودة" },
  review: { class: "bg-amber-500/10 text-amber-500 border-amber-500/20", label: "قيد المراجعة" },
  approved: { class: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20", label: "معتمد" },
  archived: { class: "bg-blue-500/10 text-blue-400 border-blue-500/20", label: "مؤرشف" },
};

const STATUS_FILTERS = ["all", "assembling", "draft", "review", "approved", "archived"] as const;

export default function EvidencePacksPage() {
  const [items, setItems] = useState<EvidencePack[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    fetch("/api/v1/sovereign/executive/evidence-packs")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setItems(Array.isArray(d) ? d : d.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = statusFilter === "all" ? items : items.filter((i) => i.status === statusFilter);

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
        <h1 className="text-2xl font-bold text-foreground">حزم الأدلة</h1>
        <p className="text-sm text-muted-foreground">Evidence Packs — حزم المستندات والأدلة للحوكمة</p>
      </header>

      <div className="flex items-center gap-2 flex-wrap">
        <Filter className="w-4 h-4 text-muted-foreground" />
        {STATUS_FILTERS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
              statusFilter === s
                ? "bg-primary/10 text-primary border-primary/30"
                : "bg-card border-border text-muted-foreground hover:text-foreground"
            }`}
          >
            {s === "all" ? "الكل" : STATUS_BADGE[s]?.label || s}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Package className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد حزم أدلة بعد</p>
          <p className="text-sm text-muted-foreground/70">No evidence packs yet</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((pack) => {
            const badge = STATUS_BADGE[pack.status] || STATUS_BADGE.draft;
            return (
              <div
                key={pack.id}
                className="bg-card border border-border rounded-2xl p-5 hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-blue-500" />
                  </div>
                  <span className={`inline-flex px-2.5 py-1 rounded-full text-[10px] font-bold border ${badge.class}`}>
                    {badge.label}
                  </span>
                </div>
                <h3 className="font-bold text-sm mb-1 line-clamp-2">{pack.title}</h3>
                <div className="flex items-center gap-3 text-xs text-muted-foreground mt-2">
                  <span>{pack.type}</span>
                  <span>•</span>
                  <span>{pack.artifact_count} ملف</span>
                  <span>•</span>
                  <span>{pack.owner}</span>
                </div>
                <p className="text-[10px] text-muted-foreground mt-2">
                  {new Date(pack.created_at).toLocaleDateString("ar-SA")}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

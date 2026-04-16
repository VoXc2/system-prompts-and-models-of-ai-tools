"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, XCircle, Clock, Loader2, Inbox } from "lucide-react";

interface Approval {
  id: string;
  title: string;
  type: string;
  requester: string;
  created_at: string;
  priority: string;
  status: string;
}

const TYPE_LABELS: Record<string, string> = {
  all: "الكل",
  ma: "استحواذ",
  partnership: "شراكة",
  expansion: "توسع",
  budget: "ميزانية",
  policy: "سياسة",
};

const PRIORITY_BADGE: Record<string, string> = {
  critical: "bg-red-500/10 text-red-500 border-red-500/20",
  high: "bg-orange-500/10 text-orange-500 border-orange-500/20",
  medium: "bg-amber-500/10 text-amber-500 border-amber-500/20",
  low: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
};

export default function ApprovalCenterPage() {
  const [items, setItems] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    fetch("/api/v1/sovereign/executive/approval-center")
      .then((r) => (r.ok ? r.json() : []))
      .then((d) => setItems(Array.isArray(d) ? d : d.items || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = filter === "all" ? items : items.filter((i) => i.type === filter);

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
        <h1 className="text-2xl font-bold text-foreground">مركز الاعتماد</h1>
        <p className="text-sm text-muted-foreground">Approval Center — جميع الموافقات المعلقة عبر المسارات</p>
      </header>

      <div className="flex items-center gap-2 flex-wrap">
        {Object.entries(TYPE_LABELS).map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setFilter(key)}
            className={`px-4 py-2 rounded-full text-xs font-medium border transition-all ${
              filter === key
                ? "bg-primary/10 text-primary border-primary/30"
                : "bg-card border-border text-muted-foreground hover:text-foreground"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="bg-card border border-border rounded-2xl p-12 text-center">
          <Inbox className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
          <p className="text-lg font-bold text-muted-foreground">لا توجد موافقات معلقة</p>
          <p className="text-sm text-muted-foreground/70">No pending approvals</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <div
              key={item.id}
              className="bg-card border border-border rounded-2xl p-5 flex flex-col sm:flex-row sm:items-center gap-4"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Clock className="w-4 h-4 text-amber-500 shrink-0" />
                  <span className="font-bold text-sm truncate">{item.title}</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span>{TYPE_LABELS[item.type] || item.type}</span>
                  <span>•</span>
                  <span>{item.requester}</span>
                  <span>•</span>
                  <span>{new Date(item.created_at).toLocaleDateString("ar-SA")}</span>
                </div>
              </div>

              <span
                className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold border ${
                  PRIORITY_BADGE[item.priority] || PRIORITY_BADGE.medium
                }`}
              >
                {item.priority}
              </span>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  type="button"
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 text-emerald-500 text-xs font-bold border border-emerald-500/20 hover:bg-emerald-500/20 transition-colors"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  اعتماد
                </button>
                <button
                  type="button"
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-red-500/10 text-red-500 text-xs font-bold border border-red-500/20 hover:bg-red-500/20 transition-colors"
                >
                  <XCircle className="w-4 h-4" />
                  رفض
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
